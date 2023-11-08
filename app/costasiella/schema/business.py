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
        fields = (
            'archived',
            'b2b',
            'supplier',
            'vip',
            'name',
            'address',
            'postcode',
            'city',
            'country',
            'phone',
            'phone_2',
            'email_contact',
            'email_billing',
            'registration',
            'tax_registration',
            'mollie_customer_id',
            'created_at',
            'updated_at'
        )
        filter_fields = {
            'name': ['icontains', 'exact'],
            'b2b': ['exact'],
            'supplier': ['exact'],
            'archived': ['exact'],
            'id': ['exact'],
        }
        interfaces = (graphene.relay.Node,)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        business = self._meta.model.objects.get(id=id)

        allowed_pathnames = [
            "FinanceInvoiceNode",
        ]

        # Allow returning data when coming from AccountSubscription
        if info.path.typename in allowed_pathnames:
            return business

        require_login_and_permission(user, 'costasiella.view_business')

        return business


class BusinessQuery(graphene.ObjectType):
    businesses = DjangoFilterConnectionField(BusinessNode)
    business = graphene.relay.Node.Field(BusinessNode)

    def resolve_businesses(self, info, archived=False, **kwargs):
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
        b2b = graphene.Boolean(required=False)
        supplier = graphene.Boolean(required=False)
        vip = graphene.Boolean(required=False)
        address = graphene.String(required=False)
        postcode = graphene.String(required=False)
        city = graphene.String(required=False)
        country = graphene.String(required=False)
        phone = graphene.String(required=False)
        phone_2 = graphene.String(required=False)
        email_contact = graphene.String(required=False)
        email_billing = graphene.String(required=False)
        registration = graphene.String(required=False)
        tax_registration = graphene.String(required=False)

    business = graphene.Field(BusinessNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_business')

        # validate_create_update_input(input))

        business = Business(
            name=input['name'],
        )

        if 'b2b' in input:
            business.b2b = input['b2b']

        if 'supplier' in input:
            business.supplier = input['supplier']

        if 'vip' in input:
            business.vip = input['vip']

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
            
        if 'phone_2' in input:
            business.phone_2 = input['phone_2']

        if 'email_contact' in input:
            business.email_contact = input['email_contact']

        if 'email_billing' in input:
            business.email_billing = input['email_billing']

        if 'registration' in input:
            business.registration = input['registration']

        if 'tax_registration' in input:
            business.tax_registration = input['tax_registration']

        business.save()

        return CreateBusiness(business=business)


class UpdateBusiness(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=False)
        b2b = graphene.Boolean(required=False)
        supplier = graphene.Boolean(required=False)
        vip = graphene.Boolean(required=False)
        name = graphene.String(required=False)
        address = graphene.String(required=False)
        postcode = graphene.String(required=False)
        city = graphene.String(required=False)
        country = graphene.String(required=False)
        phone = graphene.String(required=False)
        phone_2 = graphene.String(required=False)
        email_contact = graphene.String(required=False)
        email_billing = graphene.String(required=False)
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

        # validate_create_update_input(input)
        if 'archived' in input:
            business.archived = input['archived']

        if 'b2b' in input:
            business.b2b = input['b2b']

        if 'supplier' in input:
            business.supplier = input['supplier']

        if 'vip' in input:
            business.vip = input['vip']

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

        if 'phone_2' in input:
            business.phone_2 = input['phone_2']

        if 'email_contact' in input:
            business.email_contact = input['email_contact']

        if 'email_billing' in input:
            business.email_billing = input['email_billing']

        if 'registration' in input:
            business.registration = input['registration']

        if 'tax_registration' in input:
            business.tax_registration = input['tax_registration']

        business.save()

        return UpdateBusiness(business=business)


class DeleteBusiness(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_business')

        rid = get_rid(input['id'])
        business = Business.objects.filter(id=rid.id).first()
        if not business:
            raise Exception('Invalid Account ID!')

        ok = bool(business.delete())

        return DeleteBusiness(ok=ok)


class BusinessMutation(graphene.ObjectType):
    create_business = CreateBusiness.Field()
    update_business = UpdateBusiness.Field()
    delete_business = DeleteBusiness.Field()
