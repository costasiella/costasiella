from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import OrganizationSubscription, OrganizationSubscriptionPrice, FinanceTaxRate 
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages


m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}
    
    if not len(input['name']):
        print('validation error found')
        raise GraphQLError(_('Name is required'))

    # Fetch & check tax rate
    rid = get_rid(input['finance_tax_rate'])
    finance_tax_rate = FinanceTaxRate.objects.filter(id=rid.id).first()
    result['finance_tax_rate'] = finance_tax_rate
    if not finance_tax_rate:
        raise Exception(_('Invalid Finance Tax Rate ID!'))

    return result

class OrganizationSubscriptionPriceNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    price_display = graphene.String()


class OrganizationSubscriptionPriceNode(DjangoObjectType):   
    class Meta:
        model = OrganizationSubscriptionPrice
        filter_fields = [ 'archived', 'organization_subscription']
        interfaces = (graphene.relay.Node, OrganizationSubscriptionPriceNodeInterface)


    def resolve_price_display(self, info):
        from ..modules.finance_tools import display_float_as_amount
        return display_float_as_amount(self.price)


    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationsubscriptionprice')

        # Return only public non-archived memberships
        return self._meta.model.objects.get(id=id)


class OrganizationSubscriptionPriceQuery(graphene.ObjectType):
    organization_subscription_prices = DjangoFilterConnectionField(OrganizationSubscriptionPriceNode)
    organization_subscription_price = graphene.relay.Node.Field(OrganizationSubscriptionPriceNode)


    def resolve_organization_subscriptions(self, info, organization_subscription, archived, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationsubscriptionprice')

        rid = get_rid(organization_subscription)
        return OrganizationSubscriptionPrice.objects.filter(organization_subscription = rid.id, archived = archived).order_by('name')

        # # Has permission: return everything
        # if user.has_perm('costasiella.view_organizationsubscription'):
        #     print('user has view permission')
            

        # # Return only public non-archived locations
        # return OrganizationSubscriptionPrice.objects.filter(organization_subscription = rid.id, display_public = True, archived = False).order_by('name')


class CreateOrganizationSubscriptionPrice(graphene.relay.ClientIDMutation):
    class Input:
        organization_subscription = graphene.ID(required=True)
        price = graphene.Float(required=False, default_value=0)
        finance_taxrate = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default=None)

    organization_subscription = graphene.Field(OrganizationSubscriptionPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationsubscription')

        # Validate input
        result = validate_create_update_input(input, update=False)

        subscription = OrganizationSubscriptionPrice(
            display_public=input['display_public'],
            display_shop=input['display_shop'],
            name=input['name'], 
            description=input['description'],
            sort_order=input['sort_order'],
            min_duration=input['min_duration'],
            classes=input['classes'],
            subscription_unit=input['subscription_unit'],
            reconciliation_classes=input['reconciliation_classes'],
            credit_validity=input['credit_validity'],
            unlimited=input['unlimited'],
            terms_and_conditions=input['terms_and_conditions'],
            registration_fee=input['registration_fee'],
            quick_stats_amount=input.get('quick_stats_amount', None)
        )

        if 'organization_membership' in result:
            subscription.organization_membership = result['organization_membership']

        if 'finance_glaccount' in result:
            subscription.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            subscription.finance_costcenter = result['finance_costcenter']

        subscription.save()

        return CreateOrganizationSubscriptionPrice(organization_subscription = subscription)


class UpdateOrganizationSubscriptionPrice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        display_public = graphene.Boolean(required=True, default_value=True)
        display_shop = graphene.Boolean(required=True, default_value=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        sort_order = graphene.Int(required=True, default_value=1)
        min_duration = graphene.Int(required=True, default_value=1)
        classes = graphene.Int(required=True, default_value=1)
        subscription_unit = graphene.String(required=True)
        reconciliation_classes = graphene.Int(required=False, default_value=0)
        credit_validity = graphene.Int(required=False, default_value=0)
        unlimited = graphene.Boolean(required=True, default_value=False)
        terms_and_conditions = graphene.String(required=False, default_value="")
        registration_fee = graphene.Float(required=False, default_value=0)
        organization_membership = graphene.ID(required=False, default_value="")
        quick_stats_amount = graphene.Float(required=False, default_value=0)
        finance_glaccount = graphene.ID(required=False, default_value="")
        finance_costcenter = graphene.ID(required=False, default_value="")   

    organization_subscription = graphene.Field(OrganizationSubscriptionPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationsubscription')
    
        rid = get_rid(input['id'])
        subscription = OrganizationSubscriptionPrice.objects.filter(id=rid.id).first()
        if not subscription:
            raise Exception('Invalid Organization Class pass ID!')

        result = validate_create_update_input(input, update=True)

        subscription.display_public=input['display_public']
        subscription.display_shop=input['display_shop']
        subscription.name=input['name']
        subscription.description=input['description']
        subscription.sort_order=input['sort_order']
        subscription.min_duration=input['min_duration']
        subscription.classes=input['classes']
        subscription.subscription_unit=input['subscription_unit']
        subscription.reconciliation_classes=input['reconciliation_classes']
        subscription.credit_validity=input['credit_validity']
        subscription.unlimited=input['unlimited']
        subscription.terms_and_conditions=input['terms_and_conditions']
        subscription.registration_fee=input['registration_fee']      
        subscription.quick_stats_amount=input['quick_stats_amount']

        if 'organization_membership' in result:
            subscription.organization_membership = result['organization_membership']

        if 'finance_glaccount' in result:
            subscription.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            subscription.finance_costcenter = result['finance_costcenter']

        subscription.save(force_update=True)

        return UpdateOrganizationSubscriptionPrice(organization_subscription=subscription)


class ArchiveOrganizationSubscriptionPrice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_subscription = graphene.Field(OrganizationSubscriptionPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationsubscription')

        rid = get_rid(input['id'])
        subscription = OrganizationSubscriptionPrice.objects.filter(id=rid.id).first()
        if not subscription:
            raise Exception('Invalid Organization SubscriptionPrice ID!')

        subscription.archived = input['archived']
        subscription.save(force_update=True)

        return ArchiveOrganizationSubscriptionPrice(organization_subscription=subscription)


class OrganizationSubscriptionPriceMutation(graphene.ObjectType):
    archive_organization_subscription = ArchiveOrganizationSubscriptionPrice.Field()
    create_organization_subscription = CreateOrganizationSubscriptionPrice.Field()
    update_organization_subscription = UpdateOrganizationSubscriptionPrice.Field()