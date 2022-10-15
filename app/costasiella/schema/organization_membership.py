from django.utils.translation import gettext as _

import graphene
from decimal import Decimal

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import OrganizationMembership, FinanceCostCenter, FinanceGLAccount, FinanceTaxRate 
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail

m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}
    
    if not len(input['name']):
        raise GraphQLError(_('Name is required'))

    # Fetch & check tax rate
    rid = get_rid(input['finance_tax_rate'])
    finance_tax_rate = FinanceTaxRate.objects.filter(id=rid.id).first()
    result['finance_tax_rate'] = finance_tax_rate
    if not finance_tax_rate:
        raise Exception(_('Invalid Finance Tax Rate ID!'))

    # Check GLAccount
    if 'finance_glaccount' in input:
        if input['finance_glaccount']: 
            rid = get_rid(input['finance_glaccount'])
            finance_glaccount= FinanceGLAccount.objects.filter(id=rid.id).first()
            result['finance_glaccount'] = finance_glaccount
            if not finance_glaccount:
                raise Exception(_('Invalid Finance GLAccount ID!'))

    # Check Costcenter
    if 'finance_costcenter' in input:
        if input['finance_costcenter']:
            rid = get_rid(input['finance_costcenter'])
            finance_costcenter= FinanceCostCenter.objects.filter(id=rid.id).first()
            result['finance_costcenter'] = finance_costcenter
            if not finance_costcenter:
                raise Exception(_('Invalid Finance Costcenter ID!'))


    return result


class OrganizationMembershipNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    price_display = graphene.String()
    validity_unit_display = graphene.String()


class OrganizationMembershipNode(DjangoObjectType):   
    class Meta:
        model = OrganizationMembership
        fields = (
            'archived',
            'display_public',
            'display_shop',
            'name',
            'description',
            'price',
            'finance_tax_rate',
            'validity',
            'validity_unit',
            'terms_and_conditions',
            'finance_glaccount',
            'finance_costcenter'
        )
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, OrganizationMembershipNodeInterface)

    def resolve_price_display(self, info):
        from ..modules.finance_tools import display_float_as_amount
        return display_float_as_amount(self.price)

    def resolve_validity_unit_display(self, info):
        from ..modules.validity_tools import display_validity_unit
        return display_validity_unit(self.validity_unit, self.validity)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationmembership')

        # Return only public non-archived memberships
        return self._meta.model.objects.get(id=id)


class OrganizationMembershipQuery(graphene.ObjectType):
    organization_memberships = DjangoFilterConnectionField(OrganizationMembershipNode)
    organization_membership = graphene.relay.Node.Field(OrganizationMembershipNode)


    def resolve_organization_memberships(self, info, archived, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationmembership')

        ## return everything:
        # if user.has_perm('costasiella.view_organizationmembership'):
        return OrganizationMembership.objects.filter(archived = archived).order_by('name')


class CreateOrganizationMembership(graphene.relay.ClientIDMutation):
    class Input:
        display_public = graphene.Boolean(required=True, default_value=True)
        display_shop = graphene.Boolean(required=True, default_value=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        price = graphene.Decimal(required=True, default_value=Decimal(0))
        finance_tax_rate = graphene.ID(required=True)
        validity = graphene.Int(required=True, default_value=1)
        validity_unit = graphene.String(required=True)
        terms_and_conditions = graphene.String(required=False, default_value="")
        finance_glaccount = graphene.ID(required=False, default_value="")
        finance_costcenter = graphene.ID(required=False, default_value="")

    organization_membership = graphene.Field(OrganizationMembershipNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationmembership')

        # Validate input
        result = validate_create_update_input(input, update=False)

        membership = OrganizationMembership(
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

        return CreateOrganizationMembership(organization_membership = membership)


class UpdateOrganizationMembership(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        display_public = graphene.Boolean(required=True, default_value=True)
        display_shop = graphene.Boolean(required=True, default_value=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        price = graphene.Decimal(rquired=True, default_value=Decimal(0))
        finance_tax_rate = graphene.ID(required=True)
        validity = graphene.Int(required=True, default_value=1)
        validity_unit = graphene.String(required=True)
        terms_and_conditions = graphene.String(required=False, default_value="")
        finance_glaccount = graphene.ID(required=False, default_value="")
        finance_costcenter = graphene.ID(required=False, default_value="")

    organization_membership = graphene.Field(OrganizationMembershipNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationmembership')

    
        rid = get_rid(input['id'])
        membership = OrganizationMembership.objects.filter(id=rid.id).first()
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

        return UpdateOrganizationMembership(organization_membership=membership)


class ArchiveOrganizationMembership(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_membership = graphene.Field(OrganizationMembershipNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationmembership')

        rid = get_rid(input['id'])
        membership = OrganizationMembership.objects.filter(id=rid.id).first()
        if not membership:
            raise Exception('Invalid Organization Membership ID!')

        membership.archived = input['archived']
        membership.save()

        return ArchiveOrganizationMembership(organization_membership=membership)


class OrganizationMembershipMutation(graphene.ObjectType):
    archive_organization_membership = ArchiveOrganizationMembership.Field()
    create_organization_membership = CreateOrganizationMembership.Field()
    update_organization_membership = UpdateOrganizationMembership.Field()