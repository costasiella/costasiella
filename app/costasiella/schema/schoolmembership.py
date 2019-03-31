from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from .gql_tools import get_rid
import validators

from ..models import SchoolMembership, FinanceCostCenter, FinanceGLAccount, FinanceTaxRate 
from ..modules.gql_tools import require_login_and_permission
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail

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


class SchoolMembershipNode(DjangoObjectType):   
    class Meta:
        model = SchoolMembership
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_schoolmembership')

        # Return only public non-archived memberships
        return self._meta.model.objects.get(id=id)


class SchoolMembershipQuery(graphene.ObjectType):
    school_memberships = DjangoFilterConnectionField(SchoolMembershipNode)
    school_membership = graphene.relay.Node.Field(SchoolMembershipNode)


    def resolve_school_memberships(self, info, archived, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_schoolmembership')

        ## return everything:
        # if user.has_perm('costasiella.view_schoolmembership'):
        return SchoolMembership.objects.filter(archived = archived).order_by('name')


class CreateSchoolMembership(graphene.relay.ClientIDMutation):
    class Input:
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

    school_membership = graphene.Field(SchoolMembershipNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_schoolmembership')

        # Validate input
        result = validate_create_update_input(input, update=False)

        school_membership = SchoolMembership(
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
            school_membership.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            school_membership.finance_costcenter = result['finance_costcenter']

        school_membership.save()

        return CreateSchoolMembership(school_membership = school_membership)


class UpdateSchoolMembership(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        display_public = graphene.Boolean(required=True, default_value=True)
        url_website = graphene.String(required=False, default_value="")

    school_membership = graphene.Field(SchoolMembershipNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_schoolmembership')

        rid = get_rid(input['id'])
        membership = SchoolMembership.objects.filter(id=rid.id).first()
        if not membership:
            raise Exception('Invalid School Membership ID!')

        url_website = input['url_website']
        if url_website:
            if not validators.url(url_website, public=True):
                raise GraphQLError(_('Invalid URL, make sure it starts with "http"'))
            else:
                membership.url_website = url_website

        membership.name = input['name']
        membership.description = input['description']
        membership.display_public = input['display_public']
        membership.save(force_update=True)

        return UpdateSchoolMembership(school_membership=membership)


class UploadSchoolMembershipImage(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        image = graphene.String(required=True)


    school_membership = graphene.Field(SchoolMembershipNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_schoolmembership')

        import base64
        from django.core.files.base import ContentFile

        def base64_file(data, name=None):
            _format, _img_str = data.split(';base64,')
            _name, ext = _format.split('/')
            if not name:
                name = _name.split(":")[-1]
            return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))

        rid = get_rid(input['id'])
        membership = SchoolMembership.objects.filter(id=rid.id).first()
        if not membership:
            raise Exception('Invalid School Membership ID!')

        b64_enc_image = input['image']
        # print(b64_enc_image)
        (image_type, image_file) = b64_enc_image.split(',')
        # print(image_type)

        
        membership.image = base64_file(data=b64_enc_image)
        membership.save(force_update=True)

        print('new image')
        img = membership.image
        print(img.name)
        print(img.path)
        print(img.url)

        return UpdateSchoolMembership(school_membership=membership)


class ArchiveSchoolMembership(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    school_membership = graphene.Field(SchoolMembershipNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_schoolmembership')

        rid = get_rid(input['id'])
        membership = SchoolMembership.objects.filter(id=rid.id).first()
        if not membership:
            raise Exception('Invalid School Membership ID!')

        membership.archived = input['archived']
        membership.save(force_update=True)

        return ArchiveSchoolMembership(school_membership=membership)


class SchoolMembershipMutation(graphene.ObjectType):
    # archive_school_membership = ArchiveSchoolMembership.Field()
    create_school_membership = CreateSchoolMembership.Field()
    # update_school_membership = UpdateSchoolMembership.Field()
    # upload_school_membership_image = UploadSchoolMembershipImage.Field()