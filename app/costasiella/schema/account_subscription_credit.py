from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import AccountSubscription, AccountSubscriptionCredit
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail

m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    if not input['mutation_type'] in ['ADD', 'SUB']:
        raise Exception(_('Invalid mutation type; ADD and SUB are accepted'))

    # Fetch & check account subscription
    if not update:
        rid = get_rid(input['account_subscription'])
        account_subscription = AccountSubscription.objects.get(pk=rid.id)
        result['account_subscription'] = account_subscription
        if not account_subscription:
            raise Exception(_('Invalid Account Subscription ID!'))

    return result


class AccountSubscriptionCreditNode(DjangoObjectType):
    class Meta:
        model = AccountSubscriptionCredit
        filter_fields = {
            'account_subscription': ['exact'],
        }
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountsubscriptioncredit')

        return self._meta.model.objects.get(id=id)


class AccountSubscriptionCreditQuery(graphene.ObjectType):
    account_subscription_credits = DjangoFilterConnectionField(AccountSubscriptionCreditNode)
    account_subscription_credit = graphene.relay.Node.Field(AccountSubscriptionCreditNode)

    def resolve_account_subscription_credits(self, info, account_subscription, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountsubscriptioncredit')
        rid = get_rid(account_subscription)

        # return everything:
        return AccountSubscriptionCredit.objects.filter(account_subscription__id=rid.id).order_by('-created_at')


class CreateAccountSubscriptionCredit(graphene.relay.ClientIDMutation):
    class Input:
        account_subscription = graphene.ID(required=True)
        mutation_type = graphene.String(required=True)
        mutation_amount = graphene.Float(required=True)
        description = graphene.String(required=False, default_value="")

    account_subscription_credit = graphene.Field(AccountSubscriptionCreditNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountsubscriptioncredit')

        # Validate input
        result = validate_create_update_input(input, update=False)

        account_subscription_credit = AccountSubscriptionCredit(
            account_subscription=result['account_subscription'],
            mutation_type=input['mutation_type'],
            mutation_amount=input['mutation_amount'],
            description=input['description']
        )

        account_subscription_credit.save()

        return CreateAccountSubscriptionCredit(account_subscription_credit=account_subscription_credit)


class UpdateAccountSubscriptionCredit(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        mutation_type = graphene.String(required=True)
        mutation_amount = graphene.Float(required=True)
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

        result = validate_create_update_input(input, update=True)

        account_subscription_credit.mutation_type = input['mutation_type']
        account_subscription_credit.mutation_amount = input['mutation_amount']
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

        ok = account_subscription_credit.delete()

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

        print(input)
        year = input['year']
        month = input['month']

        task = account_subscription_credits_add_for_month.delay(year, month)
        print(task)
        ok = True

        # rid = get_rid(input['id'])
        # account_subscription = AccountSubscription.objects.filter(id=rid.id).first()
        # if not account_subscription:
        #     raise Exception('Invalid Account Subscription ID!')
        #
        # ok = account_subscription.delete()

        return CreateAccountSubscriptionCreditForMonth(ok=ok)


class AccountSubscriptionCreditMutation(graphene.ObjectType):
    create_account_subscription_credit = CreateAccountSubscriptionCredit.Field()
    create_account_subscription_credit_for_month = CreateAccountSubscriptionCreditForMonth.Field()
    delete_account_subscription_credit = DeleteAccountSubscriptionCredit.Field()
    update_account_subscription_credit = UpdateAccountSubscriptionCredit.Field()
