from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import OrganizationClasspass, OrganizationMembership, FinanceCostCenter, FinanceGLAccount, FinanceTaxRate 
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

    # Check OrganizationMembership
    if 'organization_membership' in input:
        if input['organization_membership']:
            rid = get_rid(input['organization_membership'])
            organization_membership = OrganizationMembership.objects.filter(id=rid.id).first()
            result['organization_membership'] = organization_membership
            if not organization_membership:
                raise Exception(_('Invalid Organization Membership ID!'))            

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


class OrganizationClasspassNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    price_display = graphene.String()
    validity_unit_display = graphene.String()


class OrganizationClasspassNode(DjangoObjectType):   
    class Meta:
        model = OrganizationClasspass
        filter_fields = ['archived', 'display_shop']
        interfaces = (graphene.relay.Node, OrganizationClasspassNodeInterface)

    def resolve_price_display(self, info):
        from ..modules.finance_tools import display_float_as_amount
        return display_float_as_amount(self.price)

    def resolve_validity_unit_display(self, info):
        from ..modules.validity_tools import display_validity_unit
        return display_validity_unit(self.validity_unit, self.validity)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationclasspass')

        # Return only public non-archived memberships
        return self._meta.model.objects.get(id=id)


class OrganizationClasspassQuery(graphene.ObjectType):
    organization_classpasses = DjangoFilterConnectionField(OrganizationClasspassNode)
    organization_classpass = graphene.relay.Node.Field(OrganizationClasspassNode)

    def resolve_organization_classpasses(self, info, **kwargs):
        user = info.context.user
        # Has permission: return everything

        order_by = 'name'
        archived = kwargs.get('archived', False)
        display_shop = kwargs.get('display_shop', None)

        objects = OrganizationClasspass.objects

        if display_shop:
            # Only show public passes in the shop... always!
            return objects.filter(
                display_shop=True,
                archived=False
            ).order_by(order_by)

        # Check if user has view permission; if not; only show active passes
        if user.has_perm('costasiella.view_organizationclasspass'): 
            objects = OrganizationClasspass.objects.filter(
                archived=archived
            )

            if display_shop is not None:
                objects = objects.filter(display_shop=display_shop)

        else:
            # Non logged in user or user without permission
            # only display public classpasses
            objects = OrganizationClasspass.objects.filter(
                archived=False,
                display_public=True
            )

        return objects.order_by('name')


class CreateOrganizationClasspass(graphene.relay.ClientIDMutation):
    class Input:
        display_public = graphene.Boolean(required=True, default_value=True)
        display_shop = graphene.Boolean(required=True, default_value=True)
        trial_pass = graphene.Boolean(required=False, default_value=True)
        trial_times = graphene.String(required=False)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        price = graphene.Decimal(required=True, default_value=0)
        finance_tax_rate = graphene.ID(required=True)
        validity = graphene.Int(required=True, default_value=1)
        validity_unit = graphene.String(required=True)
        classes = graphene.Int(required=True, default_value=1)
        unlimited = graphene.Boolean(required=True, default_value=False)
        organization_membership = graphene.ID(required=False, default_value="")
        quick_stats_amount = graphene.Decimal(required=False, default_value=0)
        finance_glaccount = graphene.ID(required=False, default_value="")
        finance_costcenter = graphene.ID(required=False, default_value="")

    organization_classpass = graphene.Field(OrganizationClasspassNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationclasspass')

        # Validate input
        result = validate_create_update_input(input, update=False)

        classpass = OrganizationClasspass(
            display_public=input['display_public'],
            display_shop=input['display_shop'],
            trial_pass=input['trial_pass'],
            name=input['name'], 
            description=input['description'],
            price=input['price'],
            finance_tax_rate=result['finance_tax_rate'],
            validity=input['validity'],
            validity_unit=input['validity_unit'],
            classes=input['classes'],
            unlimited=input['unlimited'],
            quick_stats_amount=input.get('quick_stats_amount', None)
        )

        if 'trial_times' in input:
            classpass.trial_times = input['trial_times']

        if 'organization_membership' in result:
            classpass.organization_membership = result['organization_membership']

        if 'finance_glaccount' in result:
            classpass.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            classpass.finance_costcenter = result['finance_costcenter']

        classpass.save()

        return CreateOrganizationClasspass(organization_classpass = classpass)


class UpdateOrganizationClasspass(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        display_public = graphene.Boolean(required=True, default_value=True)
        display_shop = graphene.Boolean(required=True, default_value=True)
        trial_pass = graphene.Boolean(required=False)
        trial_times = graphene.String(required=False)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        price = graphene.Decimal(required=True, default_value=0)
        finance_tax_rate = graphene.ID(required=True)
        validity = graphene.Int(required=True, default_value=1)
        validity_unit = graphene.String(required=True)
        classes = graphene.Int(required=True, default_value=1)
        unlimited = graphene.Boolean(required=True, default_value=False)
        organization_membership = graphene.ID(required=False, default_value="")
        quick_stats_amount = graphene.Decimal(required=False, default_value=0)
        finance_glaccount = graphene.ID(required=False, default_value="")
        finance_costcenter = graphene.ID(required=False, default_value="")

    organization_classpass = graphene.Field(OrganizationClasspassNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationclasspass')
    
        rid = get_rid(input['id'])
        classpass = OrganizationClasspass.objects.filter(id=rid.id).first()
        if not classpass:
            raise Exception('Invalid Organization Class pass ID!')

        result = validate_create_update_input(input, update=True)

        classpass.display_public=input['display_public']
        classpass.display_shop=input['display_shop']
        classpass.name=input['name']
        classpass.description=input['description']
        classpass.price=input['price']
        classpass.finance_tax_rate=result['finance_tax_rate']
        classpass.validity=input['validity']
        classpass.validity_unit=input['validity_unit']
        classpass.classes=input['classes']
        classpass.unlimited=input['unlimited']
        classpass.quick_stats_amount=input['quick_stats_amount']

        if 'trial_pass' in input:
            classpass.trial_pass = input['trial_pass']

        if 'trial_times' in input:
            classpass.trial_times = input['trial_times']

        if 'organization_membership' in result:
            classpass.organization_membership = result['organization_membership']

        if 'finance_glaccount' in result:
            classpass.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            classpass.finance_costcenter = result['finance_costcenter']

        classpass.save(force_update=True)

        return UpdateOrganizationClasspass(organization_classpass=classpass)


class ArchiveOrganizationClasspass(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_classpass = graphene.Field(OrganizationClasspassNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationclasspass')

        rid = get_rid(input['id'])
        classpass = OrganizationClasspass.objects.filter(id=rid.id).first()
        if not classpass:
            raise Exception('Invalid Organization Classpass ID!')

        classpass.archived = input['archived']
        classpass.save(force_update=True)

        return ArchiveOrganizationClasspass(organization_classpass=classpass)


class OrganizationClasspassMutation(graphene.ObjectType):
    archive_organization_classpass = ArchiveOrganizationClasspass.Field()
    create_organization_classpass = CreateOrganizationClasspass.Field()
    update_organization_classpass = UpdateOrganizationClasspass.Field()