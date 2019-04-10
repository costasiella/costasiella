from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from .gql_tools import get_rid
import validators

from ..models import SchoolClasscard, SchoolMembership, FinanceCostCenter, FinanceGLAccount, FinanceTaxRate 
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


class SchoolClasscardNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    price_display = graphene.String()
    validity_unit_display = graphene.String()


class SchoolClasscardNode(DjangoObjectType):   
    class Meta:
        model = SchoolClasscard
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, SchoolClasscardNodeInterface)

    def resolve_price_display(self, info):
        from ..modules.finance_tools import display_float_as_amount
        return display_float_as_amount(self.price)

    def resolve_validity_unit_display(self, info):
        from ..modules.validity_tools import display_validity_unit
        return display_validity_unit(self.validity_unit)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_schoolclasscard')

        # Return only public non-archived memberships
        return self._meta.model.objects.get(id=id)


class SchoolClasscardQuery(graphene.ObjectType):
    school_classcards = DjangoFilterConnectionField(SchoolClasscardNode)
    school_classcard = graphene.relay.Node.Field(SchoolClasscardNode)


    def resolve_school_classcards(self, info, archived, **kwargs):
        user = info.context.user
        # Has permission: return everything
        if user.has_perm('costasiella.view_schoolclasscard'):
            print('user has view permission')
            return SchoolClasscard.objects.filter(archived = archived).order_by('name')

        # Return only public non-archived locations
        return SchoolClasscard.objects.filter(display_public = True, archived = False).order_by('name')


class CreateSchoolClasscard(graphene.relay.ClientIDMutation):
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

    school_classcard = graphene.Field(SchoolClasscardNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_schoolclasscard')

        # Validate input
        result = validate_create_update_input(input, update=False)

        classcard = SchoolClasscard(
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
            classcard.school_membership = result['school_membership']

        if 'finance_glaccount' in result:
            classcard.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            classcard.finance_costcenter = result['finance_costcenter']

        classcard.save()

        return CreateSchoolClasscard(school_classcard = classcard)


# class UpdateSchoolMembership(graphene.relay.ClientIDMutation):
#     class Input:
#         id = graphene.ID(required=True)
#         display_public = graphene.Boolean(required=True, default_value=True)
#         display_shop = graphene.Boolean(required=True, default_value=True)
#         name = graphene.String(required=True)
#         description = graphene.String(required=False, default_value="")
#         price = graphene.Float(rquired=True, default_value=0)
#         finance_tax_rate = graphene.ID(required=True)
#         validity = graphene.Int(required=True, default_value=1)
#         validity_unit = graphene.String(required=True)
#         terms_and_conditions = graphene.String(required=False, default_value="")
#         finance_glaccount = graphene.ID(required=False, default_value="")
#         finance_costcenter = graphene.ID(required=False, default_value="")

#     school_membership = graphene.Field(SchoolMembershipNode)

#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.change_schoolclasscard')

    
#         rid = get_rid(input['id'])
#         membership = SchoolMembership.objects.filter(id=rid.id).first()
#         if not membership:
#             raise Exception('Invalid School Membership ID!')

#         result = validate_create_update_input(input, update=True)

#         membership.display_public=input['display_public']
#         membership.display_shop=input['display_shop']
#         membership.name=input['name']
#         membership.description=input['description']
#         membership.price=input['price']
#         membership.finance_tax_rate=result['finance_tax_rate']
#         membership.validity=input['validity']
#         membership.validity_unit=input['validity_unit']
#         membership.terms_and_conditions=input['terms_and_conditions']

#         if 'finance_glaccount' in result:
#             membership.finance_glaccount = result['finance_glaccount']

#         if 'finance_costcenter' in result:
#             membership.finance_costcenter = result['finance_costcenter']

#         membership.save(force_update=True)

#         return UpdateSchoolMembership(school_membership=membership)


# class ArchiveSchoolMembership(graphene.relay.ClientIDMutation):
#     class Input:
#         id = graphene.ID(required=True)
#         archived = graphene.Boolean(required=True)

#     school_membership = graphene.Field(SchoolMembershipNode)

#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.delete_schoolclasscard')

#         rid = get_rid(input['id'])
#         membership = SchoolMembership.objects.filter(id=rid.id).first()
#         if not membership:
#             raise Exception('Invalid School Membership ID!')

#         membership.archived = input['archived']
#         membership.save(force_update=True)

#         return ArchiveSchoolMembership(school_membership=membership)


class SchoolClasscardMutation(graphene.ObjectType):
    # archive_school_membership = ArchiveSchoolMembership.Field()
    create_school_classcard = CreateSchoolClasscard.Field()
    # update_school_membership = UpdateSchoolMembership.Field()