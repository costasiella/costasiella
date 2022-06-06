from django.utils.translation import gettext as _

import datetime
import graphene
from decimal import Decimal

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationSubscription, OrganizationSubscriptionPrice, FinanceTaxRate
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.date_tools import last_day_month
from ..modules.messages import Messages

m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Fetch & check organization subscription
    if not update:
        rid = get_rid(input['organization_subscription'])
        organization_subscription = OrganizationSubscription.objects.filter(id=rid.id).first()
        result['organization_subscription'] = organization_subscription
        if not organization_subscription:
            raise Exception(_('Invalid Organization Subscription ID!'))
    

    # Fetch & check tax rate
    rid = get_rid(input['finance_tax_rate'])
    finance_tax_rate = FinanceTaxRate.objects.filter(id=rid.id).first()
    result['finance_tax_rate'] = finance_tax_rate
    if not finance_tax_rate:
        raise Exception(_('Invalid Finance Tax Rate ID!'))

    # Check date_end > date_start, if date_end and make sure date start and end align
    # with start & end of a month
    if not input['date_start']:
        raise Exception(_('dateStart is required!'))

    ##
    # Date start is always first day of the month
    ##
    result['date_start'] = datetime.date(
        input['date_start'].year,
        input['date_start'].month,
        1
    )

    ##
    # Date end is always last day of the month
    ##
    if 'date_end' in input:
        if input['date_end']:
            result['date_end'] = datetime.date(
                input['date_end'].year,
                input['date_end'].month,
                last_day_month(input['date_end'])
            )
            if result['date_start'] > result['date_end']:
                raise Exception(_('dateStart has to be > dateEnd!'))


    return result


class OrganizationSubscriptionPriceNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    price_display = graphene.String()


class OrganizationSubscriptionPriceNode(DjangoObjectType):
    class Meta:
        model = OrganizationSubscriptionPrice
        fields = (
            'organization_subscription',
            'price',
            'finance_tax_rate',
            'date_start',
            'date_end'
        )
        filter_fields = {
            'organization_subscription': ['exact'],
            'date_start': ['lte'],
            'date_end': ['gte', 'isnull']
        }
        interfaces = (graphene.relay.Node, OrganizationSubscriptionPriceNodeInterface)

    def resolve_price_display(self, info):
        from ..modules.finance_tools import display_float_as_amount
        return display_float_as_amount(self.price)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationsubscriptionprice')

        return self._meta.model.objects.get(id=id)


class OrganizationSubscriptionPriceQuery(graphene.ObjectType):
    organization_subscription_prices = DjangoFilterConnectionField(OrganizationSubscriptionPriceNode)
    organization_subscription_price = graphene.relay.Node.Field(OrganizationSubscriptionPriceNode)

    def resolve_organization_subscription_prices(self, info, organization_subscription, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationsubscriptionprice')

        rid = get_rid(organization_subscription)
        return OrganizationSubscriptionPrice.objects.filter(organization_subscription=rid.id).order_by('-date_start')


class CreateOrganizationSubscriptionPrice(graphene.relay.ClientIDMutation):
    class Input:
        organization_subscription = graphene.ID(required=True)
        price = graphene.Decimal(required=True, default_value=Decimal(0))
        finance_tax_rate = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        

    organization_subscription_price = graphene.Field(OrganizationSubscriptionPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationsubscriptionprice')

        result = validate_create_update_input(input, update=False)
        organization_subscription_price = OrganizationSubscriptionPrice(
            organization_subscription = result['organization_subscription'],
            price = input['price'],
            finance_tax_rate = result['finance_tax_rate'],
            date_start = result['date_start'],
            date_end = result.get('date_end', None)
        )
        

        organization_subscription_price.save()

        return CreateOrganizationSubscriptionPrice(organization_subscription_price=organization_subscription_price)


class UpdateOrganizationSubscriptionPrice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        price = graphene.Decimal(required=True, default_value=Decimal(0))
        finance_tax_rate = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        
    organization_subscription_price = graphene.Field(OrganizationSubscriptionPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationsubscriptionprice')

        rid = get_rid(input['id'])
        organization_subscription_price = OrganizationSubscriptionPrice.objects.filter(id=rid.id).first()
        if not organization_subscription_price:
            raise Exception('Invalid Organization Subscription ID!')

        result = validate_create_update_input(input, update=True)

        organization_subscription_price.price = input['price']
        organization_subscription_price.finance_tax_rate = result['finance_tax_rate']
        organization_subscription_price.date_start = result['date_start']
        organization_subscription_price.date_end = result.get('date_end', None)
        organization_subscription_price.save()

        return UpdateOrganizationSubscriptionPrice(organization_subscription_price=organization_subscription_price)


class DeleteOrganizationSubscriptionPrice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    # organization_subscription_price = graphene.Field(OrganizationSubscriptionPriceNode)
    ok = graphene.Boolean()
    

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationsubscriptionprice')

        rid = get_rid(input['id'])

        organization_subscription_price = OrganizationSubscriptionPrice.objects.filter(id=rid.id).first()
        if not organization_subscription_price:
            raise Exception('Invalid Organization Subscription ID!')

        ok = bool(organization_subscription_price.delete())

        return DeleteOrganizationSubscriptionPrice(ok=ok)


class OrganizationSubscriptionPriceMutation(graphene.ObjectType):
    delete_organization_subscription_price = DeleteOrganizationSubscriptionPrice.Field()
    create_organization_subscription_price = CreateOrganizationSubscriptionPrice.Field()
    update_organization_subscription_price = UpdateOrganizationSubscriptionPrice.Field()
    