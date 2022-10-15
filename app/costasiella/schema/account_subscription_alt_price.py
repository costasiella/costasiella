from django.utils.translation import gettext as _

import graphene
from decimal import Decimal

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError


from ..models import AccountSubscription, AccountSubscriptionAltPrice
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

from .custom_schema_validators import is_month, is_year
from ..modules.finance_tools import display_float_as_amount

m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    is_year(input['subscription_year'])
    is_month(input['subscription_month'])

    # Fetch & check account subscription
    if not update:
        rid = get_rid(input['account_subscription'])
        account_subscription = AccountSubscription.objects.get(pk=rid.id)
        result['account_subscription'] = account_subscription
        if not account_subscription:
            raise Exception(_('Invalid Account Subscription ID!'))

    return result


class AccountSubscriptionAltPriceInterface(graphene.Interface):
    amount_display = graphene.String()


class AccountSubscriptionAltPriceNode(DjangoObjectType):
    class Meta:
        model = AccountSubscriptionAltPrice
        # Fields to include
        fields = (
            'account_subscription',
            'subscription_year',
            'subscription_month',
            'amount',
            'description',
            'note',
            'created_at',
            'updated_at'
        )
        filter_fields = {
            'account_subscription': ['exact'],
        }
        interfaces = (graphene.relay.Node, AccountSubscriptionAltPriceInterface,)

    def resolve_amount_display(self, info):
        return display_float_as_amount(self.amount)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountsubscriptionaltprice')

        return self._meta.model.objects.get(id=id)


class AccountSubscriptionAltPriceQuery(graphene.ObjectType):
    account_subscription_alt_prices = DjangoFilterConnectionField(AccountSubscriptionAltPriceNode)
    account_subscription_alt_price = graphene.relay.Node.Field(AccountSubscriptionAltPriceNode)

    def resolve_account_subscription_alt_prices(self, info, account_subscription, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountsubscriptionaltprice')
        rid = get_rid(account_subscription)

        # return everything:
        qs = AccountSubscriptionAltPrice.objects.filter(account_subscription__id=rid.id)
        return qs.order_by('-subscription_year', '-subscription_month')


class CreateAccountSubscriptionAltPrice(graphene.relay.ClientIDMutation):
    class Input:
        account_subscription = graphene.ID(required=True)
        subscription_year = graphene.Int(required=True)
        subscription_month = graphene.Int(required=True)
        amount = graphene.Decimal(required=False, default_value=Decimal(0))
        description = graphene.String(required=False, default_value="")
        note = graphene.String(required=False, default_value="")

    account_subscription_alt_price = graphene.Field(AccountSubscriptionAltPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountsubscriptionaltprice')

        # Validate input
        result = validate_create_update_input(input, update=False)

        account_subscription_alt_price = AccountSubscriptionAltPrice(
            account_subscription=result['account_subscription'],
            subscription_year=input['subscription_year'],
            subscription_month=input['subscription_month'],
            amount=input['amount'],
            description=input['description'],
            note=input['note']
        )

        account_subscription_alt_price.save()

        return CreateAccountSubscriptionAltPrice(account_subscription_alt_price=account_subscription_alt_price)


class UpdateAccountSubscriptionAltPrice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        subscription_year = graphene.Int(required=True)
        subscription_month = graphene.Int(required=True)
        amount = graphene.Decimal(required=False, default_value=Decimal(0))
        description = graphene.String(required=False, default_value="")
        note = graphene.String(required=False, default_value="")
        
    account_subscription_alt_price = graphene.Field(AccountSubscriptionAltPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountsubscriptionaltprice')

        rid = get_rid(input['id'])
        account_subscription_alt_price = AccountSubscriptionAltPrice.objects.filter(id=rid.id).first()
        if not account_subscription_alt_price:
            raise Exception('Invalid Account Subscription Alt Price ID!')

        result = validate_create_update_input(input, update=True)

        account_subscription_alt_price.subscription_year = input['subscription_year']
        account_subscription_alt_price.subscription_month = input['subscription_month']
        account_subscription_alt_price.amount = input['amount']
        account_subscription_alt_price.description = input['description']
        account_subscription_alt_price.note = input['note']

        account_subscription_alt_price.save()

        return UpdateAccountSubscriptionAltPrice(account_subscription_alt_price=account_subscription_alt_price)


class DeleteAccountSubscriptionAltPrice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountsubscriptionaltprice')

        rid = get_rid(input['id'])
        account_subscription_alt_price = AccountSubscriptionAltPrice.objects.filter(id=rid.id).first()
        if not account_subscription_alt_price:
            raise Exception('Invalid Account Subscription Alt Price ID!')

        ok = bool(account_subscription_alt_price.delete())

        return DeleteAccountSubscriptionAltPrice(ok=ok)


class AccountSubscriptionAltPriceMutation(graphene.ObjectType):
    create_account_subscription_alt_price = CreateAccountSubscriptionAltPrice.Field()
    delete_account_subscription_alt_price = DeleteAccountSubscriptionAltPrice.Field()
    update_account_subscription_alt_price = UpdateAccountSubscriptionAltPrice.Field()
