from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from .gql_tools import get_rid
import validators

from ..models import SchoolClasspass, SchoolMembership, FinanceCostCenter, FinanceGLAccount, FinanceTaxRate 
from ..modules.gql_tools import require_login_and_permission
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

    # Check SchoolMembership
    if 'school_membership' in input:
        if input['school_membership']:
            rid = get_rid(input['school_membership'])
            school_membership = SchoolMembership.objects.filter(id=rid.id).first()
            result['school_membership'] = school_membership
            if not school_membership:
                raise Exception(_('Invalid School Membership ID!'))            

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


class SchoolClasspassNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    price_display = graphene.String()
    validity_unit_display = graphene.String()


class SchoolClasspassNode(DjangoObjectType):   
    class Meta:
        model = SchoolClasspass
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, SchoolClasspassNodeInterface)

    def resolve_price_display(self, info):
        from ..modules.finance_tools import display_float_as_amount
        return display_float_as_amount(self.price)

    def resolve_validity_unit_display(self, info):
        from ..modules.validity_tools import display_validity_unit
        return display_validity_unit(self.validity_unit)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_schoolclasspass')

        # Return only public non-archived memberships
        return self._meta.model.objects.get(id=id)


class SchoolClasspassQuery(graphene.ObjectType):
    school_classpasses = DjangoFilterConnectionField(SchoolClasspassNode)
    school_classpass = graphene.relay.Node.Field(SchoolClasspassNode)


    def resolve_school_classpasses(self, info, archived, **kwargs):
        user = info.context.user
        # Has permission: return everything
        if user.has_perm('costasiella.view_schoolclasspass'):
            print('user has view permission')
            return SchoolClasspass.objects.filter(archived = archived).order_by('name')

        # Return only public non-archived locations
        return SchoolClasspass.objects.filter(display_public = True, archived = False).order_by('name')


class CreateSchoolClasspass(graphene.relay.ClientIDMutation):
    class Input:
        display_public = graphene.Boolean(required=True, default_value=True)
        display_shop = graphene.Boolean(required=True, default_value=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        price = graphene.Float(required=True, default_value=0)
        finance_tax_rate = graphene.ID(required=True)
        validity = graphene.Int(required=True, default_value=1)
        validity_unit = graphene.String(required=True)
        classes = graphene.Int(required=True, default_value=1)
        unlimited = graphene.Boolean(required=True, default_value=False)
        school_membership = graphene.ID(required=False, default_value="")
        quick_stats_amount = graphene.Float(required=False, default_value=0)
        finance_glaccount = graphene.ID(required=False, default_value="")
        finance_costcenter = graphene.ID(required=False, default_value="")

    school_classpass = graphene.Field(SchoolClasspassNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_schoolclasspass')

        # Validate input
        result = validate_create_update_input(input, update=False)

        classpass = SchoolClasspass(
            display_public=input['display_public'],
            display_shop=input['display_shop'],
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

        if 'school_membership' in result:
            classpass.school_membership = result['school_membership']

        if 'finance_glaccount' in result:
            classpass.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            classpass.finance_costcenter = result['finance_costcenter']

        classpass.save()

        return CreateSchoolClasspass(school_classpass = classpass)


class UpdateSchoolClasspass(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        display_public = graphene.Boolean(required=True, default_value=True)
        display_shop = graphene.Boolean(required=True, default_value=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        price = graphene.Float(required=True, default_value=0)
        finance_tax_rate = graphene.ID(required=True)
        validity = graphene.Int(required=True, default_value=1)
        validity_unit = graphene.String(required=True)
        classes = graphene.Int(required=True, default_value=1)
        unlimited = graphene.Boolean(required=True, default_value=False)
        school_membership = graphene.ID(required=False, default_value="")
        quick_stats_amount = graphene.Float(required=False, default_value=0)
        finance_glaccount = graphene.ID(required=False, default_value="")
        finance_costcenter = graphene.ID(required=False, default_value="")

    school_classpass = graphene.Field(SchoolClasspassNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_schoolclasspass')

    
        rid = get_rid(input['id'])
        classpass = SchoolClasspass.objects.filter(id=rid.id).first()
        if not classpass:
            raise Exception('Invalid School Class pass ID!')

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

        if 'school_membership' in result:
            classpass.school_membership = result['school_membership']

        if 'finance_glaccount' in result:
            classpass.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            classpass.finance_costcenter = result['finance_costcenter']

        classpass.save(force_update=True)

        return UpdateSchoolClasspass(school_classpass=classpass)


class ArchiveSchoolClasspass(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    school_classpass = graphene.Field(SchoolClasspassNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_schoolclasspass')

        rid = get_rid(input['id'])
        classpass = SchoolClasspass.objects.filter(id=rid.id).first()
        if not classpass:
            raise Exception('Invalid School Classpass ID!')

        classpass.archived = input['archived']
        classpass.save(force_update=True)

        return ArchiveSchoolClasspass(school_classpass=classpass)


class SchoolClasspassMutation(graphene.ObjectType):
    archive_school_classpass = ArchiveSchoolClasspass.Field()
    create_school_classpass = CreateSchoolClasspass.Field()
    update_school_classpass = UpdateSchoolClasspass.Field()