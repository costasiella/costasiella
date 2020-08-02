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


def validate_create_update_input(input):
    """
    Validate input
    """ 
    result = {}

    if not input['mutation_type'] in ['ADD', 'SUB']:
        raise Exception(_('Invalid mutation type; ADD and SUB are accepted'))

    # Fetch & check account subscription
    rid = get_rid(input['organization_subscription'])
    account_subscription = AccountSubscription.objects.get(pk=rid.id)
    result['account_subscription'] = account_subscription
    if not account_subscription:
        raise Exception(_('Invalid Account Subscription ID!'))

    return result


class AccountSubscriptionCreditNode(DjangoObjectType):
    class Meta:
        model = AccountSubscriptionCredit
        filter_fields = ['account_subscription']
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
        return AccountSubscription.objects.filter(account_subscription=rid.id).order_by('created_at')


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

        result = validate_create_update_input(input, update=True)

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

        ok = account_subscription.delete()

        return DeleteAccountSubscription(ok=ok)


class AccountSubscriptionMutation(graphene.ObjectType):
    create_account_subscription = CreateAccountSubscription.Field()
    delete_account_subscription = DeleteAccountSubscription.Field()
    update_account_subscription = UpdateAccountSubscription.Field()