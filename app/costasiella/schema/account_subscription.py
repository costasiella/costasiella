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
        display_public = graphene.Boolean(required=True, default_value=True)
        display_shop = graphene.Boolean(required=True, default_value=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        price = graphene.Float(required=True, default_value=0)
        finance_tax_rate = graphene.ID(required=True)
        validity = graphene.Int(required=True, default_value=1)
        validity_unit = graphene.String(required=True)
        terms_and_conditions = graphene.String(required=False, default_value="")
        finance_glaccount = graphene.ID(required=False, default_value="")
        finance_costcenter = graphene.ID(required=False, default_value="")

    account_subscription = graphene.Field(AccountSubscriptionNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountsubscription')

        # Validate input
        result = validate_create_update_input(input, update=False)

        membership = AccountSubscription(
            display_public=input['display_public'],
            display_shop=input['display_shop'],
            name=input['name'], 
            description=input['description'],
            price=input['price'],
            finance_tax_rate=result['finance_tax_rate'],
            validity=input['validity'],
            validity_unit=input['validity_unit'],
            terms_and_conditions=input['terms_and_conditions'],
        )

        if 'finance_glaccount' in result:
            membership.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            membership.finance_costcenter = result['finance_costcenter']

        membership.save()

        return CreateAccountSubscription(account_subscription = membership)


class UpdateAccountSubscription(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        display_public = graphene.Boolean(required=True, default_value=True)
        display_shop = graphene.Boolean(required=True, default_value=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        price = graphene.Float(rquired=True, default_value=0)
        finance_tax_rate = graphene.ID(required=True)
        validity = graphene.Int(required=True, default_value=1)
        validity_unit = graphene.String(required=True)
        terms_and_conditions = graphene.String(required=False, default_value="")
        finance_glaccount = graphene.ID(required=False, default_value="")
        finance_costcenter = graphene.ID(required=False, default_value="")

    account_subscription = graphene.Field(AccountSubscriptionNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountsubscription')

    
        rid = get_rid(input['id'])
        membership = AccountSubscription.objects.filter(id=rid.id).first()
        if not membership:
            raise Exception('Invalid Organization Membership ID!')

        result = validate_create_update_input(input, update=True)

        membership.display_public=input['display_public']
        membership.display_shop=input['display_shop']
        membership.name=input['name']
        membership.description=input['description']
        membership.price=input['price']
        membership.finance_tax_rate=result['finance_tax_rate']
        membership.validity=input['validity']
        membership.validity_unit=input['validity_unit']
        membership.terms_and_conditions=input['terms_and_conditions']

        if 'finance_glaccount' in result:
            membership.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            membership.finance_costcenter = result['finance_costcenter']

        membership.save(force_update=True)

        return UpdateAccountSubscription(account_subscription=membership)


class ArchiveAccountSubscription(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    account_subscription = graphene.Field(AccountSubscriptionNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountsubscription')

        rid = get_rid(input['id'])
        membership = AccountSubscription.objects.filter(id=rid.id).first()
        if not membership:
            raise Exception('Invalid Organization Membership ID!')

        membership.archived = input['archived']
        membership.save(force_update=True)

        return ArchiveAccountSubscription(account_subscription=membership)


class AccountSubscriptionMutation(graphene.ObjectType):
    archive_account_subscription = ArchiveAccountSubscription.Field()
    create_account_subscription = CreateAccountSubscription.Field()
    update_account_subscription = UpdateAccountSubscription.Field()