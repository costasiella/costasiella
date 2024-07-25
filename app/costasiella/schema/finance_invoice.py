from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import Account, AccountSubscription, Business, FinanceInvoice, FinanceInvoiceGroup, FinancePaymentMethod
from ..modules.gql_tools import require_login, require_login_and_permission, require_permission, get_rid
from ..modules.messages import Messages
from ..modules.finance_tools import display_float_as_amount

from .custom_schema_validators import is_year, is_month

m = Messages()


class FinanceInvoiceInterface(graphene.Interface):
    id = graphene.GlobalID()
    subtotal_display = graphene.String()
    tax_display = graphene.String()
    total_display = graphene.String()
    paid_display = graphene.String()
    balance_display = graphene.String()
    credit_invoice_number = graphene.String()
    credit_invoice_id = graphene.ID()


class FinanceInvoiceNode(DjangoObjectType):
    class Meta:
        model = FinanceInvoice
        fields = (
            'account',
            'business',
            'finance_invoice_group',
            'finance_payment_method',
            'instructor_payment',
            'employee_claim',
            'custom_to',
            'relation_company',
            'relation_company_registration',
            'relation_company_tax_registration',
            'relation_contact_name',
            'relation_address',
            'relation_postcode',
            'relation_city',
            'relation_country',
            'status',
            'summary',
            'invoice_number',
            'date_sent',
            'date_due',
            'terms',
            'footer',
            'note',
            'subtotal',
            'tax',
            'total',
            'paid',
            'balance',
            'credit_invoice_for',
            'created_at',
            'updated_at',
            # Reverse relations
            'items',
            'payments'
        )
        filter_fields = {
            'account': ['exact'],
            'business': ['exact'],
            'invoice_number': ['icontains', 'exact'],
            'status': ['exact'],
            'date_sent': ['lte', 'gte'],
            'date_due': ['lte', 'gte'],
        }
        interfaces = (graphene.relay.Node, FinanceInvoiceInterface, )

    def resolve_subtotal_display(self, info):
        return display_float_as_amount(self.subtotal)

    def resolve_tax_display(self, info):
        return display_float_as_amount(self.tax)

    def resolve_total_display(self, info):
        return display_float_as_amount(self.total)

    def resolve_paid_display(self, info):
        return display_float_as_amount(self.paid)

    def resolve_balance_display(self, info):
        return display_float_as_amount(self.balance)

    def resolve_credit_invoice_number(self, info):
        return_value = ""
        if self.credit_invoice_for:
            credit_finance_invoice = FinanceInvoice.objects.get(id=self.credit_invoice_for)
            return_value = credit_finance_invoice.invoice_number

        return return_value

    def resolve_credit_invoice_id(self, info):
        return_value = ""
        if self.credit_invoice_for:
            credit_finance_invoice = FinanceInvoice.objects.get(id=self.credit_invoice_for)
            return_value = to_global_id("FinanceInvoiceNode", credit_finance_invoice.id)

        return return_value

    @classmethod
    def get_node(cls, info, id):
        user = info.context.user
        require_login(user)

        # Own invoice always ok
        finance_invoice = cls._meta.model.objects.get(id=id)
        if finance_invoice.account == user:
            return finance_invoice

        # Permission required to invoices belonging to other accounts
        require_permission(user, 'costasiella.view_financeinvoice')

        return finance_invoice


class FinanceInvoiceQuery(graphene.ObjectType):
    finance_invoices = DjangoFilterConnectionField(FinanceInvoiceNode)
    finance_invoice = graphene.relay.Node.Field(FinanceInvoiceNode)

    def resolve_finance_invoices(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login(user)
        view_permission = user.has_perm('costasiella.view_financeinvoice')

        if view_permission and 'account' in kwargs and kwargs['account']:
            # Allow user to filter by any account
            rid = get_rid(kwargs.get('account', user.id))
            account_id = rid.id
        elif view_permission:
            # return all
            account_id = None
        else:
            # A user can only query their own invoices
            account_id = user.id

        order_by = '-pk'
        if account_id:
            return FinanceInvoice.objects.filter(account=account_id).order_by(order_by)
        else:
            return FinanceInvoice.objects.all().order_by(order_by)


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Fetch & check invoice group
    if not update:
        ## Create only

        # Check if account or business is in input
        if 'account' not in input and 'business' not in input:
            raise Exception(_('Either the account or business field is required to create an invoice.'))

        # invoice group
        rid = get_rid(input['finance_invoice_group'])
        finance_invoice_group = FinanceInvoiceGroup.objects.filter(id=rid.id).first()
        result['finance_invoice_group'] = finance_invoice_group
        if not finance_invoice_group:
            raise Exception(_('Invalid Finance Invoice Group ID!'))

        # Check account_subscription
        if 'account_subscription' in input:
            if input['account_subscription']:
                rid = get_rid(input['account_subscription'])
                account_subscription = AccountSubscription.objects.filter(id=rid.id).first()
                result['account_subscription'] = account_subscription
                if not account_subscription:
                    raise Exception(_('Invalid Account Subscription ID!'))

        if 'subscription_year' in input:
            is_year(input['subscription_year'])
            result['subscription_year'] = input['subscription_year']

        if 'subscription_month' in input:
            is_month(input['subscription_month'])
            result['subscription_month'] = input['subscription_month']

    # account
    if 'account' in input:
        rid = get_rid(input['account'])
        account = Account.objects.filter(id=rid.id).first()
        result['account'] = account
        if not account:
            raise Exception(_('Invalid Account ID!'))

    # Check business
    if 'business' in input:
        if input['business']:
            rid = get_rid(input['business'])
            business = Business.objects.get(id=rid.id)
            result['business'] = business
            if not business:
                raise Exception(_('Invalid Business ID!'))
        else:
            result['business'] = None

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


class CreateFinanceInvoice(graphene.relay.ClientIDMutation):
    class Input:
        finance_invoice_group = graphene.ID(required=True)
        account = graphene.ID(required=False)
        business = graphene.ID(required=False)
        summary = graphene.String(required=False, default_value="")
        account_subscription = graphene.ID(required=False)
        subscription_year = graphene.Int(required=False)
        subscription_month = graphene.Int(required=False)
        
    finance_invoice = graphene.Field(FinanceInvoiceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeinvoice')

        validation_result = validate_create_update_input(input)
        finance_invoice_group = validation_result['finance_invoice_group']

        finance_invoice = FinanceInvoice(
            finance_invoice_group=finance_invoice_group,
            status='DRAFT',
            terms=finance_invoice_group.terms,
            footer=finance_invoice_group.footer
        )

        if 'account' in validation_result:
            finance_invoice.account = validation_result['account']

        if 'summary' in input:
            finance_invoice.summary = input['summary']

        # Save invoice
        finance_invoice.save()

        # Do this after an initial save to override the "invoice_to_business" field on an account, if set.
        if 'business' in validation_result:
            finance_invoice.business = validation_result['business']
            finance_invoice.set_relation_info()
            finance_invoice.save()

        if ('account_subscription' in validation_result
                and 'subscription_year' in validation_result
                and 'subscription_month' in validation_result):
            finance_invoice.item_add_subscription(
                validation_result['account_subscription'],
                validation_result['subscription_year'],
                validation_result['subscription_month']
            )

        # Add empty invoice item when creating an invoice manually
        finance_invoice.item_add_empty()

        return CreateFinanceInvoice(finance_invoice=finance_invoice)


class UpdateFinanceInvoice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        account = graphene.ID(required=False)
        business = graphene.ID(required=False)
        finance_payment_method = graphene.ID(required=False)
        summary = graphene.String(required=False)
        custom_to = graphene.Boolean(required=False)
        relation_company = graphene.String(required=False)
        relation_company_registration = graphene.String(required=False)
        relation_company_tax_registration = graphene.String(required=False)
        relation_contact_name = graphene.String(required=False)
        relation_address = graphene.String(required=False)
        relation_postcode = graphene.String(required=False)
        relation_city = graphene.String(required=False)
        relation_country = graphene.String(required=False)
        invoice_number = graphene.String(required=False)
        date_sent = graphene.types.datetime.Date(required=False)
        date_due = graphene.types.datetime.Date(required=False)
        status = graphene.String(required=False)
        terms = graphene.String(required=False)
        footer = graphene.String(required=False)
        note = graphene.String(required=False)

    finance_invoice = graphene.Field(FinanceInvoiceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeinvoice')

        rid = get_rid(input['id'])
        finance_invoice = FinanceInvoice.objects.filter(id=rid.id).first()
        if not finance_invoice:
            raise Exception('Invalid Finance Invoice  ID!')

        validation_result = validate_create_update_input(input, update=True)

        if 'account' in validation_result:
            finance_invoice.account = validation_result['account']

        if 'business' in validation_result:
            finance_invoice.business = validation_result['business']

        if 'summary' in input:
            finance_invoice.summary = input['summary']

        if 'custom_to' in input:
            finance_invoice.custom_to = input['custom_to']

        if 'relation_company' in input:
            finance_invoice.relation_company = input['relation_company']

        if 'relation_company_registration' in input:
            finance_invoice.relation_company_registration = input['relation_company_registration']

        if 'relation_company_tax_registration' in input:
            finance_invoice.relation_company_tax_registration = input['relation_company_tax_registration']

        if 'relation_contact_name' in input:
            finance_invoice.relation_contact_name = input['relation_contact_name']

        if 'relation_address' in input:
            finance_invoice.relation_address = input['relation_address']

        if 'relation_postcode' in input:
            finance_invoice.relation_postcode = input['relation_postcode']

        if 'relation_city' in input:
            finance_invoice.relation_city = input['relation_city']

        if 'relation_country' in input:
            finance_invoice.relation_country = input['relation_country']

        if 'invoice_number' in input:
            finance_invoice.invoice_number = input['invoice_number']

        if 'date_sent' in input:
            finance_invoice.date_sent = input['date_sent']

        if 'date_due' in input:
            finance_invoice.date_due = input['date_due']

        if 'status' in input:
            finance_invoice.status = input['status']

        if 'terms' in input:
            finance_invoice.terms = input['terms']

        if 'footer' in input:
            finance_invoice.footer = input['footer']

        if 'note' in input:
            finance_invoice.note = input['note']

        if 'finance_payment_method' in validation_result:
            finance_invoice.finance_payment_method = validation_result['finance_payment_method']

        # Applies custom relation address info only when customTo is set
        finance_invoice.set_relation_info()
        finance_invoice.save()

        return UpdateFinanceInvoice(finance_invoice=finance_invoice)


class CancelAndCreateCreditFinanceInvoice(graphene.relay.ClientIDMutation):
    """
    Mutation to cancel an invoice and create a credit invoice.
    Returns credit invoice
    """
    class Input:
        id = graphene.ID(required=True)

    finance_invoice = graphene.Field(FinanceInvoiceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeinvoice')

        rid = get_rid(input['id'])
        finance_invoice = FinanceInvoice.objects.filter(id=rid.id).first()
        if not finance_invoice:
            raise Exception('Invalid Finance Invoice  ID!')

        credit_finance_invoice = None
        # Check if a credit invoice already exists for this invoice. If so, fetch and return that without doing anything
        qs = FinanceInvoice.objects.filter(credit_invoice_for=rid.id)
        if qs.exists():
            credit_finance_invoice = qs.first()
        else:
            credit_finance_invoice = finance_invoice.cancel_and_create_credit_invoice()

        return CancelAndCreateCreditFinanceInvoice(finance_invoice=credit_finance_invoice)


class DeleteFinanceInvoice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    
    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financeinvoice')

        rid = get_rid(input['id'])

        finance_invoice = FinanceInvoice.objects.filter(id=rid.id).first()
        if not finance_invoice:
            raise Exception('Invalid Finance Invoice ID!')

        ok = bool(finance_invoice.delete())

        return DeleteFinanceInvoice(ok=ok)


class FinanceInvoiceMutation(graphene.ObjectType):
    delete_finance_invoice = DeleteFinanceInvoice.Field()
    create_finance_invoice = CreateFinanceInvoice.Field()
    update_finance_invoice = UpdateFinanceInvoice.Field()
    cancel_and_create_credit_finance_invoice = CancelAndCreateCreditFinanceInvoice.Field()
