import graphene
from decimal import Decimal

from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, AccountProduct, OrganizationProduct
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..dudes.sales_dude import SalesDude

from sorl.thumbnail import get_thumbnail

m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Fetch & check account
    if not update:
        # Create only
        rid = get_rid(input['account'])
        account = Account.objects.filter(id=rid.id).first()
        result['account'] = account
        if not account:
            raise Exception(_('Invalid Account ID!'))

    # Fetch & check organization product
    rid = get_rid(input['organization_product'])
    organization_product = OrganizationProduct.objects.get(pk=rid.id)
    result['organization_product'] = organization_product
    if not organization_product:
        raise Exception(_('Invalid Organization Product ID!'))

    return result


class AccountProductNode(DjangoObjectType):   
    class Meta:
        model = AccountProduct
        # Fields to include
        fields = (
            'account',
            'organization_product',
            'quantity',
            'created_at',
            'updated_at',
            # Reverse relations
            'invoice_items'
        )
        filter_fields = {
            'account': ['exact'],
        }
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountproduct')

        return self._meta.model.objects.get(id=id)


class AccountProductQuery(graphene.ObjectType):
    account_products = DjangoFilterConnectionField(AccountProductNode)
    account_product = graphene.relay.Node.Field(AccountProductNode)

    def resolve_account_products(self, info, **kwargs):
        """
        Return products for an account
        - Require login
        - Always return users' own info when no view_accountproduct permission
        - Allow user to specify the account
        :param info:
        :param account:
        :param kwargs:
        :return:
        """
        user = info.context.user
        require_login(user)

        if user.has_perm('costasiella.view_accountproduct') and 'account' in kwargs and kwargs['account']:
            rid = get_rid(kwargs.get('account', user.id))
            account_id = rid.id
            qs = AccountProduct.objects.filter(account=account_id)
        elif user.has_perm('costasiella.view_accountproduct'):
            qs = AccountProduct.objects.all()
        else:
            # A safeguard that ensures users without permission can only query their own products
            account_id = user.id
            qs = AccountProduct.objects.filter(account=account_id)

        # Allow user to specify account
        return qs.order_by('-created_at')


class CreateAccountProduct(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        organization_product = graphene.ID(required=True)
        quantity = graphene.Decimal(required=False, default_value=Decimal(1))

    account_product = graphene.Field(AccountProductNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountproduct')

        # Validate input
        result = validate_create_update_input(input, update=False)

        sales_dude = SalesDude()
        sales_result = sales_dude.sell_product(
            account=result['account'],
            organization_product=result['organization_product'],
            quantity=input['quantity'],
            create_invoice=True
        )

        account_product = sales_result['account_product']

        return CreateAccountProduct(account_product=account_product)


# class UpdateAccountProduct(graphene.relay.ClientIDMutation):
#     class Input:
#         id = graphene.ID(required=True)
#         organization_product = graphene.ID(required=True)
#         date_start = graphene.types.datetime.Date(required=True)
#         date_end = graphene.types.datetime.Date(required=False, default_value=None)
#         note = graphene.String(required=False, default_value="")
#
#     account_product = graphene.Field(AccountProductNode)
#
#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.change_accountproduct')
#
#         rid = get_rid(input['id'])
#         account_product = AccountProduct.objects.filter(id=rid.id).first()
#         if not account_product:
#             raise Exception('Invalid Account Product ID!')
#
#         result = validate_create_update_input(input, update=True)
#         account_product.organization_product = result['organization_product']
#         account_product.date_start = input['date_start']
#
#         if 'date_end' in input:
#             # Allow None as a value to be able to NULL date_end
#             account_product.date_end = input['date_end']
#
#         if 'note' in input:
#             account_product.note = input['note']
#
#         account_product.save(force_update=True)
#
#         return UpdateAccountProduct(account_product=account_product)


class DeleteAccountProduct(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountproduct')

        rid = get_rid(input['id'])
        account_product = AccountProduct.objects.filter(id=rid.id).first()
        if not account_product:
            raise Exception('Invalid Account Product ID!')

        ok = bool(account_product.delete())

        return DeleteAccountProduct(ok=ok)


class AccountProductMutation(graphene.ObjectType):
    create_account_product = CreateAccountProduct.Field()
    delete_account_product = DeleteAccountProduct.Field()
    # update_account_product = UpdateAccountProduct.Field()
