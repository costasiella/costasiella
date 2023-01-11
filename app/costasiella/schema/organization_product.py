from django.utils.translation import gettext as _

import graphene
from decimal import Decimal

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationProduct, FinanceCostCenter, FinanceGLAccount, FinanceTaxRate
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid, get_content_file_from_base64_str
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail


m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}
    
    if 'image' in input or 'image_file_name' in input:
        if not (input.get('image', None) and input.get('image_file_name', None)):
            raise Exception(_('When setting "image" or "imageFileName", both fields need to be present and set'))

    # Fetch & check tax rate
    if 'finance_tax_rate' in input:
        if input['finance_tax_rate']:
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


class OrganizationProductNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    price_display = graphene.String()
    url_image = graphene.String()
    url_image_thumbnail_small = graphene.String()
    url_image_thumbnail_large = graphene.String()


class OrganizationProductNode(DjangoObjectType):
    class Meta:
        model = OrganizationProduct
        fields = (
            'archived',
            'name',
            'description',
            'image',
            'price',
            'finance_tax_rate',
            'finance_glaccount',
            'finance_costcenter'
        )
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, OrganizationProductNodeInterface)

    def resolve_price_display(self, info):
        from ..modules.finance_tools import display_float_as_amount
        return display_float_as_amount(self.price)

    def resolve_url_image(self, info):
        if self.image:
            return self.image.url
        else:
            return ''

    def resolve_url_image_thumbnail_small(self, info):
        if self.image:
            return get_thumbnail(self.image, '50x50', crop='center', quality=99).url
        else:
            return ''

    def resolve_url_image_thumbnail_large(self, info):
        if self.image:
            return get_thumbnail(self.image, '400x400', crop='center', quality=99).url
        else:
            return ''

    @classmethod
    def get_node(self, info, id):
        user = info.context.user

        organization_product = self._meta.model.objects.get(id=id)

        # Allow users to view organization products, if they're added to their account
        if info.path.typename == "AccountProductNode":
            return organization_product

        require_login_and_permission(user, 'costasiella.view_organizationproduct')

        return organization_product


class OrganizationProductQuery(graphene.ObjectType):
    organization_products = DjangoFilterConnectionField(OrganizationProductNode)
    organization_product = graphene.relay.Node.Field(OrganizationProductNode)

    def resolve_organization_products(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationproduct')

        archived = kwargs.get('archived')
        if archived is None:
            archived = False

        objects = OrganizationProduct.objects.filter(
            archived=archived,
        )

        return objects.order_by('name')


class CreateOrganizationProduct(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        image = graphene.String(required=False)
        image_file_name = graphene.String(required=False)
        price = graphene.Decimal(required=False, default_value=Decimal(0))
        finance_tax_rate = graphene.ID(required=False)
        finance_glaccount = graphene.ID(required=False, default_value="")
        finance_costcenter = graphene.ID(required=False, default_value="")

    organization_product = graphene.Field(OrganizationProductNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationproduct')

        # Validate input
        result = validate_create_update_input(input, update=False)

        organization_product = OrganizationProduct(
            name=input['name'],
            description=input['description'],
            price=input['price'],
        )

        # This check works, because it'll throw an exception if either image or iamge_file_name is not set
        if 'image' in input:
            organization_product.image = get_content_file_from_base64_str(
                data_str=input['image'],
                file_name=input['image_file_name']
            )

        if 'finance_tax_rate' in result:
            organization_product.finance_tax_rate = result['finance_tax_rate']

        if 'finance_glaccount' in result:
            organization_product.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            organization_product.finance_costcenter = result['finance_costcenter']

        organization_product.save()

        return CreateOrganizationProduct(organization_product=organization_product)


class UpdateOrganizationProduct(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False, default_value="")
        image = graphene.String(required=False)
        image_file_name = graphene.String(required=False)
        price = graphene.Decimal(required=False, default_value=Decimal(0))
        finance_tax_rate = graphene.ID(required=False)
        finance_glaccount = graphene.ID(required=False, default_value="")
        finance_costcenter = graphene.ID(required=False, default_value="")

    organization_product = graphene.Field(OrganizationProductNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationproduct')

        rid = get_rid(input['id'])
        organization_product = OrganizationProduct.objects.filter(id=rid.id).first()
        if not organization_product:
            raise Exception('Invalid Organization Product ID!')

        result = validate_create_update_input(input, update=True)

        if 'name' in input:
            organization_product.name = input['name']

        if 'description' in input:
            organization_product.description = input['description']

        if 'price' in input:
            organization_product.price = input['price']

        # This check works, because it'll throw an exception if either image or image_file_name is not set
        if 'image' in input:
            organization_product.image = get_content_file_from_base64_str(
                data_str=input['image'],
                file_name=input['image_file_name']
            )

        if 'finance_tax_rate' in result:
            organization_product.finance_tax_rate = result['finance_tax_rate']

        if 'finance_glaccount' in result:
            organization_product.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            organization_product.finance_costcenter = result['finance_costcenter']

        organization_product.save()

        return UpdateOrganizationProduct(organization_product=organization_product)


class ArchiveOrganizationProduct(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_product = graphene.Field(OrganizationProductNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationproduct')

        rid = get_rid(input['id'])
        organization_product = OrganizationProduct.objects.filter(id=rid.id).first()
        if not organization_product:
            raise Exception('Invalid Organization Product ID!')

        organization_product.archived = input['archived']
        organization_product.save()

        return ArchiveOrganizationProduct(organization_product=organization_product)


class OrganizationProductMutation(graphene.ObjectType):
    archive_organization_product = ArchiveOrganizationProduct.Field()
    create_organization_product = CreateOrganizationProduct.Field()
    update_organization_product = UpdateOrganizationProduct.Field()
