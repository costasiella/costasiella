import datetime

from django.utils.translation import gettext as _
from django.utils import timezone

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import AccountSubscription, AccountSubscriptionCredit
from ..modules.gql_tools import get_error_code, require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail

m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Fetch & check account subscription
    if not update:
        rid = get_rid(input['account_subscription'])
        account_subscription = AccountSubscription.objects.get(pk=rid.id)
        result['account_subscription'] = account_subscription
        if not account_subscription:
            raise Exception(_('Invalid Account Subscription ID!'))

    return result


class OrganizationSubscriptionCreditNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    expired = graphene.Boolean()


class AccountSubscriptionCreditNode(DjangoObjectType):
    class Meta:
        model = AccountSubscriptionCredit
        # Fields to include
        fields = (
            'advance',
            'reconciled',
            'account_subscription',
            'schedule_item_attendance',
            'expiration',
            'description',
            'subscription_year',
            'subscription_month',
            'created_at',
            'updated_at'
        )
        filter_fields = {
            'account_subscription': ['exact'],
        }
        interfaces = (graphene.relay.Node, OrganizationSubscriptionCreditNodeInterface, )

    @classmethod
    def get_node(cls, info, id):
        user = info.context.user
        require_login(user)

        account_subscription_credit = cls._meta.model.objects.get(id=id)
        #TODO: Perhaps add a filter here that raises an exception if the mutation_type field isn't "SINGLE"?
        if not account_subscription_credit.account_subscription.account == user:
            # Allow users to get credits for their own subscriptions, but require permissions for all others.
            require_login_and_permission(user, 'costasiella.view_accountsubscriptioncredit')

        return account_subscription_credit

    def resolve_expired(self, info):
        today = timezone.now().date()
        expired = False

        if self.expiration < today:
            expired = True

        return expired


class AccountSubscriptionCreditQuery(graphene.ObjectType):
    account_subscription_credits = DjangoFilterConnectionField(AccountSubscriptionCreditNode)
    account_subscription_credit = graphene.relay.Node.Field(AccountSubscriptionCreditNode)

    def resolve_account_subscription_credits(self, info, account_subscription, **kwargs):
        user = info.context.user
        require_login(user)

        rid = get_rid(account_subscription)
        account_subscription = AccountSubscription.objects.get(id=rid.id)

        if not (user.has_perm('costasiella.view_accountsubscriptioncredit') or account_subscription.account == user):
            raise GraphQLError(m.user_permission_denied, extensions={'code': get_error_code('USER_PERMISSION_DENIED')})

        # return requested information:
        # Include mutation_type=SINGLE to prevent old style credits from appearing
        return AccountSubscriptionCredit.objects.filter(
            account_subscription__id=rid.id,
            mutation_type="SINGLE",
        ).order_by('-created_at')


class CreateAccountSubscriptionCredit(graphene.relay.ClientIDMutation):
    """
    Returns the last credit added if amount > 1.
    This behavior is strange, but it's ok for now.
    """
    class Input:
        account_subscription = graphene.ID(required=True)
        description = graphene.String(required=False, default_value="")
        amount = graphene.Int(required=False, default_value=1)

    account_subscription_credit = graphene.Field(AccountSubscriptionCreditNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountsubscriptioncredit')

        # Validate input
        result = validate_create_update_input(input, update=False)

        today = timezone.now().date()

        for i in range(0, input['amount']):
            account_subscription_credit = AccountSubscriptionCredit(
                account_subscription=result['account_subscription'],
                description=input['description'],
                expiration=today + datetime.timedelta(
                    days=result['account_subscription'].organization_subscription.credit_validity)
            )

            account_subscription_credit.save()

        return CreateAccountSubscriptionCredit(account_subscription_credit=account_subscription_credit)


class UpdateAccountSubscriptionCredit(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        expiration = graphene.types.Date()
        description = graphene.String(required=False, default_value="")
        
    account_subscription_credit = graphene.Field(AccountSubscriptionCreditNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountsubscriptioncredit')

        rid = get_rid(input['id'])
        account_subscription_credit = AccountSubscriptionCredit.objects.filter(id=rid.id).first()
        if not account_subscription_credit:
            raise Exception('Invalid Account Subscription Credit ID!')

        validate_create_update_input(input, update=True)

        account_subscription_credit.expiration = input['expiration']
        account_subscription_credit.description = input['description']

        account_subscription_credit.save()

        return UpdateAccountSubscriptionCredit(account_subscription_credit=account_subscription_credit)


class DeleteAccountSubscriptionCredit(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountsubscriptioncredit')

        rid = get_rid(input['id'])
        account_subscription_credit = AccountSubscriptionCredit.objects.filter(id=rid.id).first()
        if not account_subscription_credit:
            raise Exception('Invalid Account Subscription Credit ID!')

        ok = bool(account_subscription_credit.delete())

        return DeleteAccountSubscriptionCredit(ok=ok)


def create_account_subscription_credit_for_month_validation(input):
    """
    Validate input for create subscription credits for month task
    """
    from .custom_schema_validators import is_month, is_year

    is_month(input['month'])
    is_year(input['year'])


class CreateAccountSubscriptionCreditForMonth(graphene.relay.ClientIDMutation):
    class Input:
        year = graphene.Int()
        month = graphene.Int()

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        from costasiella.tasks import account_subscription_credits_add_for_month

        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountsubscriptioncredit')

        year = input['year']
        month = input['month']

        task = account_subscription_credits_add_for_month.delay(year=year, month=month)
        ok = True

        return CreateAccountSubscriptionCreditForMonth(ok=ok)


class AccountSubscriptionCreditMutation(graphene.ObjectType):
    create_account_subscription_credit = CreateAccountSubscriptionCredit.Field()
    create_account_subscription_credit_for_month = CreateAccountSubscriptionCreditForMonth.Field()
    delete_account_subscription_credit = DeleteAccountSubscriptionCredit.Field()
    update_account_subscription_credit = UpdateAccountSubscriptionCredit.Field()
