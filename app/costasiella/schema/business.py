from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Business
from ..modules.gql_tools import require_login_and_permission, get_rid, get_content_file_from_base64_str
from ..modules.messages import Messages

m = Messages()


class BusinessNode(DjangoObjectType):
    class Meta:
        model = Business
        filter_fields = ['archived', 'id']
        interfaces = (graphene.relay.Node,)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_business')

        return self._meta.model.objects.get(id=id)


class BusinessQuery(graphene.ObjectType):
    businesses = DjangoFilterConnectionField(BusinessNode)
    business = graphene.relay.Node.Field(BusinessNode)

    def resolve_business(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_business')

        # return everything:
        return Business.objects.filter(archived=archived).order_by('name')


# def validate_create_update_input(input):
#     """
#     Validate input
#     """
#     result = {}
#
#     return result


class CreateBusiness(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String()
        address = graphene.String(required=False)
        postcode = graphene.String(required=False)
        city = graphene.String(required=False)
        country = graphene.String(required=False)
        phone = graphene.String(required=False)
        mobile = graphene.String(required=False)
        email = graphene.String(required=False)
        registration = graphene.String(required=False)
        tax_registration = graphene.String(required=False)

    business = graphene.Field(BusinessNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_business')

        validate_create_update_input(input)

        business = Business(
            name=input['name'],
        )

        if 'address' in input:
            business.address = input['address']
            
        if 'city' in input:
            business.city = input['city']
            
        if 'postcode' in input:
            business.postcode = input['postcode']
            
        if 'country' in input:
            business.country = input['country']

        if 'phone' in input:
            business.phone = input['phone']
            
        if 'mobile' in input:
            business.mobile = input['mobile']

        if 'email' in input:
            business.email = input['email']

        if 'registration' in input:
            business.registration = input['registration']

        if 'tax_registration' in input:
            business.tax_registration = input['tax_registration']

        business.save()

        return CreateBusiness(business=business)


class UpdateBusiness(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        address = graphene.String(required=False)
        postcode = graphene.String(required=False)
        city = graphene.String(required=False)
        country = graphene.String(required=False)
        phone = graphene.String(required=False)
        mobile = graphene.String(required=False)
        email = graphene.String(required=False)
        registration = graphene.String(required=False)
        tax_registration = graphene.String(required=False)
        
    business = graphene.Field(BusinessNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_business')

        rid = get_rid(input['id'])

        business = Business.objects.filter(id=rid.id).first()
        if not business:
            raise Exception('Invalid Business ID!')

        validate_create_update_input(input)

        if 'name' in input:
            business.name = input['name']

        if 'address' in input:
            business.address = input['address']

        if 'city' in input:
            business.city = input['city']

        if 'postcode' in input:
            business.postcode = input['postcode']

        if 'country' in input:
            business.country = input['country']

        if 'phone' in input:
            business.phone = input['phone']

        if 'mobile' in input:
            business.mobile = input['mobile']

        if 'email' in input:
            business.email = input['email']

        if 'registration' in input:
            business.registration = input['registration']

        if 'tax_registration' in input:
            business.tax_registration = input['tax_registration']

        business.save()

        return UpdateBusiness(business=business)


class ArchiveBusiness(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    business = graphene.Field(BusinessNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_business')

        rid = get_rid(input['id'])

        business = Business.objects.filter(id=rid.id).first()
        if not business:
            raise Exception('Invalid Business ID!')

        business.archived = input['archived']
        business.save()

        return ArchiveBusiness(business=business)


class BusinessMutation(graphene.ObjectType):
    create_business = CreateBusiness.Field()
    update_business = UpdateBusiness.Field()
    archive_business = ArchiveBusiness.Field()
