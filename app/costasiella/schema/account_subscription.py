from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import Account, AccountSubscription, FinancePaymentMethod, OrganizationSubscription
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail

m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Fetch & check account
    rid = get_rid(input['account'])
    account = Account.objects.filter(id=rid.id).first()
    result['account'] = account
    if not account:
        raise Exception(_('Invalid Account ID!'))

    # Fetch & check organization subscription
    rid = get_rid(input['organization_subscription'])
    organization_subscription = OrganizationSubscription.objects.get(pk=rid.id)
    result['organization_subscription'] = organization_subscription
    if not account:
        raise Exception(_('Invalid Organization Subscription ID!'))

    # Check finance payment method
    if 'finance_payment_method' in input:
        if input['finance_payment_method']:
            rid = get_rid(input['finance_payment_method'])
            finance_payment_method = FinancePaymentMethod.objects.filter(id=rid.id).first()
            result['finance_payment_method'] = finance_payment_method
            if not finance_payment_method:
                raise Exception(_('Invalid Finance Payment Method ID!'))


    return result


class AccountSubscriptionNode(DjangoObjectType):   
    class Meta:
        model = AccountSubscription
        filter_fields = ['account', 'date_start', 'date_end']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountsubscription')

        return self._meta.model.objects.get(id=id)


class AccountSubscriptionQuery(graphene.ObjectType):
    account_subscriptions = DjangoFilterConnectionField(AccountSubscriptionNode)
    account_subscription = graphene.relay.Node.Field(AccountSubscriptionNode)


    def resolve_account_subscriptions(self, info, account, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountsubscription')

        rid = get_rid(account)

        ## return everything:
        return AccountSubscription.objects.filter(account=rid.id).order_by('date_start')


class CreateAccountSubscription(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
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
        require_login_and_permission(user, 'costasiella.add_accountsubscription')

        # Validate input
        result = validate_create_update_input(input, update=False)

        account_subscription = AccountSubscription(
            account=result['account'],
            organization_subscription=result['organization_subscription'],
            date_start=input['date_start'], 
            note=input['note'], 
        )

        if 'registration_fee_paid' in input:
            account_subscription.registration_fee_paid = input['registration_fee_paid']

        if 'date_end' in input:
            account_subscription.date_end = input['date_end']

        if 'finance_payment_method' in result:
            account_subscription.finance_payment_method = result['finance_payment_method']

        account_subscription.save()

        return CreateAccountSubscription(account_subscription = account_subscription)


class UpdateAccountSubscription(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        account = graphene.ID(required=True)
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

        account_subscription.account=input['account']
        account_subscription.organization_subscription=input['organization_subscription']
        account_subscription.date_start=input['date_start']
        account_subscription.note=result['note']
        account_subscription.registration_fee_paid=result['registration_fee_paid']

        if 'registration_fee_paid' in input:
            account_subscription.registration_fee_paid = input['registration_fee_paid']

        if 'date_end' in input:
            account_subscription.date_end = input['date_end']

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