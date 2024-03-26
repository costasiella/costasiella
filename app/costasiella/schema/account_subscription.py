from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Sum

import uuid
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from django_filters import FilterSet, OrderingFilter, CharFilter

import validators

from .custom_filters import EmptyStringFilter

from ..modules.encrypted_fields import EncryptedTextField

from ..dudes import SalesDude, SystemSettingDude
from ..models import Account, \
    AccountBankAccount, \
    AccountBankAccountMandate, \
    AccountSubscription, \
    AccountSubscriptionCredit, \
    FinancePaymentMethod, \
    OrganizationSubscription
from ..modules.gql_tools import require_login, require_login_and_permission, require_permission, get_rid
from ..modules.messages import Messages

m = Messages()


def validate_create_update_input(user, input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Fetch & check account
    if not update:
        # Create only
        rid = get_rid(input['account'])
        account = Account.objects.filter(id=rid.id).first()
        result['account'] = account
        if not account:
            raise Exception(_('Invalid Account ID!'))

        # If user doesn't have permissions to create a subscription, date has to be >= today
        if not user.has_perm('costasiella.add_accountsubscription'):
            today = timezone.now().date()
            if input['date_start'] < today:
                raise Exception(_("Subscription can't start in the past"))

    # Fetch & check organization subscription
    rid = get_rid(input['organization_subscription'])
    organization_subscription = OrganizationSubscription.objects.get(pk=rid.id)
    result['organization_subscription'] = organization_subscription
    if not organization_subscription:
        raise Exception(_('Invalid Organization Subscription ID!'))

    # Check finance payment method
    if 'finance_payment_method' in input:
        if input['finance_payment_method']:
            rid = get_rid(input['finance_payment_method'])
            finance_payment_method = FinancePaymentMethod.objects.filter(id=rid.id).first()
            if not finance_payment_method:
                raise Exception(_('Invalid Finance Payment Method ID!'))
        else:
            finance_payment_method = None

        result['finance_payment_method'] = finance_payment_method

    return result


class AccountSubscriptionNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    credit_total = graphene.Float()


class AccountSubscriptionFilter(FilterSet):
    account__key_number__isempty = EmptyStringFilter(field_name="account__key_number")

    class Meta:
        model = AccountSubscription
        fields = {
            'account': ['exact'],
            'date_start': ['gte', 'lte', 'exact'],
            'date_end': ['gte', 'lte', 'exact'],
            'account__key_number': ['exact', 'gt', 'isempty']
        }
        filter_overrides = {
            EncryptedTextField: {
                'filter_class': CharFilter,
            },
        }

    # order_by = OrderingFilter(
    #     fields=(
    #         'date_start',
    #     )
    # )


class AccountSubscriptionNode(DjangoObjectType):   
    class Meta:
        model = AccountSubscription
        # Filterset is used to be able to detect subscriptions where an account
        # doesn't have a key number.
        filterset_class = AccountSubscriptionFilter
        # Fields to include
        fields = (
            'account',
            'organization_subscription',
            'finance_payment_method',
            'date_start',
            'date_end',
            'note',
            'registration_fee_paid',
            'created_at',
            'updated_at',
        )

        interfaces = (graphene.relay.Node, AccountSubscriptionNodeInterface,)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login(user)

        permission = 'costasiella.view_accountsubscription'
        account_subscription = self._meta.model.objects.get(id=id)

        if not (user.has_perm(permission) or account_subscription.account == user):
            require_login_and_permission(user, permission)

        return account_subscription

    def resolve_credit_total(self, info):
        today = timezone.now().date()

        return self.get_credits_total(today)


class AccountSubscriptionQuery(graphene.ObjectType):
    account_subscriptions = DjangoFilterConnectionField(AccountSubscriptionNode)
    account_subscription = graphene.relay.Node.Field(AccountSubscriptionNode)

    def resolve_account_subscriptions(self, info, **kwargs):
        user = info.context.user
        require_login(user)

        # Default filter values
        account_id = None
        filter_empty_key_number = False

        # Check if user has permission to view other accounts & build filter
        if user.has_perm('costasiella.view_accountsubscription') and 'account' in kwargs and kwargs['account']:
            rid = get_rid(kwargs.get('account', user.id))
            account_id = rid.id
        if (user.has_perm('costasiella.view_accountsubscription')
                and 'account__key_number' in kwargs
                and kwargs['account__key_number'] == ""):
            filter_empty_key_number = True
        else:
            # User doesn't have permissions, set a default filter
            account_id = user.id

        # Apply filters
        qs = AccountSubscription.objects
        if account_id:
            qs.filter(account=account_id)

        if filter_empty_key_number:
            qs.filter(account__key_number="")

        return qs.order_by('-date_start')


class CreateAccountSubscription(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        organization_subscription = graphene.ID(required=True)
        finance_payment_method = graphene.ID(required=False, default_value="")
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        note = graphene.String(required=False, default_value="")

    account_subscription = graphene.Field(AccountSubscriptionNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        system_setting_dude = SystemSettingDude()
        shop_payment_method = system_setting_dude.get("workflow_shop_subscription_payment_method") or "MOLLIE"

        # Validate input
        result = validate_create_update_input(user, input, update=False)

        if shop_payment_method == "DIRECTDEBIT":
            require_login(user)
            # Allow users to create subscriptions for themselves only
            if not user.id == result['account'].id:
                require_permission(user, 'costasiella.add_accountsubscription')
        else:
            # Any online payment should go through orders instead
            require_login_and_permission(user, 'costasiella.add_accountsubscription')

        # account_subscription = AccountSubscription(
        #     account=result['account'],
        #     organization_subscription=result['organization_subscription'],
        #     date_start=input['date_start'],
        # )
        sales_dude = SalesDude()

        finance_payment_method = None
        if shop_payment_method == "DIRECTDEBIT" and user == result['account']:
            # Payment method should always start as direct debit
            finance_payment_method = FinancePaymentMethod.objects.get(id=103)

            # Save account subscription to be able to create an invoice
            # account_subscription.save()

            # User has agreed to direct debit in Shop, create mandate signed today if it doesn't exist yet.
            # We can assume a bank account exits for an account (it should)
            account_bank_account = AccountBankAccount.objects.filter(account=result['account']).first()
            if not account_bank_account.has_direct_debit_mandate():
                account_bank_account.add_mandate()

            # Create invoice for first month of subscription
            # account_subscription.create_invoice_for_month(account_subscription.date_start.year,
            #                                               account_subscription.date_start.month)
        else:
            if 'finance_payment_method' in result:
                finance_payment_method = result['finance_payment_method']

        sales_dude_result = sales_dude.sell_subscription(
            account=result['account'],
            organization_subscription=result['organization_subscription'],
            date_start=input['date_start'],
            date_end=input['date_end'] if 'date_end' in input else None,
            finance_payment_method=finance_payment_method,
            note=input['note'] if 'note' in input else "",
            create_invoice=True)
        account_subscription = sales_dude_result['account_subscription']

        return CreateAccountSubscription(account_subscription=account_subscription)


class UpdateAccountSubscription(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        organization_subscription = graphene.ID(required=True)
        finance_payment_method = graphene.ID(required=False, default_value="")
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        note = graphene.String(required=False, default_value="")
        registration_fee_paid = graphene.Boolean(required=False, default_value=False)        
        
    account_subscription = graphene.Field(AccountSubscriptionNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountsubscription')

    
        rid = get_rid(input['id'])
        account_subscription = AccountSubscription.objects.filter(id=rid.id).first()
        if not account_subscription:
            raise Exception('Invalid Account Subscription ID!')

        result = validate_create_update_input(user, input, update=True)

        account_subscription.organization_subscription=result['organization_subscription']
        account_subscription.date_start=input['date_start']

        if 'registration_fee_paid' in input:
            account_subscription.registration_fee_paid = input['registration_fee_paid']

        if 'date_end' in input:
            # Allow None as a value to be able to NULL date_end
            account_subscription.date_end = input['date_end']

        if 'note' in input:
            account_subscription.note = input['note']

        if 'finance_payment_method' in result:
            account_subscription.finance_payment_method = result['finance_payment_method']

        
        account_subscription.save(force_update=True)

        return UpdateAccountSubscription(account_subscription=account_subscription)


class DeleteAccountSubscription(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountsubscription')

        rid = get_rid(input['id'])
        account_subscription = AccountSubscription.objects.filter(id=rid.id).first()
        if not account_subscription:
            raise Exception('Invalid Account Subscription ID!')

        ok = bool(account_subscription.delete())

        return DeleteAccountSubscription(ok=ok)


class CreateAccountSubscriptionInvoicesMonth(graphene.relay.ClientIDMutation):
    class Input:
        x = graphene.Int()
        y = graphene.Int()

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountsubscription')

        from costasiella.tasks import add

        # print(input)
        x = input['x']
        y = input['y']

        task = add.delay(x, y)
        # print(task)
        ok = True

        return CreateAccountSubscriptionInvoicesMonth(ok=ok)


class CreateAccountSubscriptionInvoicesForMonth(graphene.relay.ClientIDMutation):
    class Input:
        year = graphene.Int()
        month = graphene.Int()
        description = graphene.String()
        invoice_date = graphene.String()

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        from costasiella.tasks import account_subscription_invoices_add_for_month

        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeinvoice')

        year = input['year']
        month = input['month']
        description = input['description']
        invoice_date = input['invoice_date']

        task = account_subscription_invoices_add_for_month.delay(
            year=year,
            month=month,
            invoice_date=invoice_date,
            description=description
        )
        ok = True

        return CreateAccountSubscriptionInvoicesForMonth(ok=ok)


class CreateAccountSubscriptionInvoicesMollieCollectionForMonth(graphene.relay.ClientIDMutation):
    class Input:
        year = graphene.Int()
        month = graphene.Int()

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        from costasiella.tasks import account_subscription_invoices_add_for_month_mollie_collection

        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeinvoice')

        year = input['year']
        month = input['month']

        task = account_subscription_invoices_add_for_month_mollie_collection.delay(year=year, month=month)
        ok = True

        return CreateAccountSubscriptionInvoicesMollieCollectionForMonth(ok=ok)


class AccountSubscriptionMutation(graphene.ObjectType):
    create_account_subscription = CreateAccountSubscription.Field()
    create_account_subscription_invoices_for_month = \
        CreateAccountSubscriptionInvoicesForMonth.Field()
    create_account_subscription_invoices_mollie_collection_for_month = \
        CreateAccountSubscriptionInvoicesMollieCollectionForMonth.Field()
    delete_account_subscription = DeleteAccountSubscription.Field()
    update_account_subscription = UpdateAccountSubscription.Field()
