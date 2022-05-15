import graphene
from decimal import Decimal

from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, AccountFinancePaymentBatchCategoryItem, FinancePaymentBatchCategory
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..dudes.system_setting_dude import SystemSettingDude

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

    # Check for create & update
    rid = get_rid(input['finance_payment_batch_category'])
    finance_payment_batch_category = FinancePaymentBatchCategory.objects.filter(id=rid.id).first()
    result['finance_payment_batch_category'] = finance_payment_batch_category
    if not finance_payment_batch_category:
        raise Exception(_('Invalid Finance Payment Batch Category ID!'))

    return result


class AccountFinancePaymentBatchCategoryItemNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    amount_display = graphene.String()


class AccountFinancePaymentBatchCategoryItemNode(DjangoObjectType):
    class Meta:
        model = AccountFinancePaymentBatchCategoryItem
        # Fields to include
        fields = (
            'account',
            'finance_payment_batch_category',
            'year',
            'month',
            'amount',
            'description',
            'created_at',
            'updated_at'
        )
        filter_fields = ['account']
        interfaces = (graphene.relay.Node, AccountFinancePaymentBatchCategoryItemNodeInterface, )

    def resolve_amount_display(self, info):
        from ..modules.finance_tools import display_float_as_amount
        return display_float_as_amount(self.amount)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountfinancepaymentbatchcategoryitem')

        return self._meta.model.objects.get(id=id)


class AccountFinancePaymentBatchCategoryItemQuery(graphene.ObjectType):
    account_finance_payment_batch_category_items = DjangoFilterConnectionField(
        AccountFinancePaymentBatchCategoryItemNode
    )
    account_finance_payment_batch_category_item = graphene.relay.Node.Field(AccountFinancePaymentBatchCategoryItemNode)

    def resolve_account_finance_payment_batch_category_items(self, info, account, **kwargs):
        """
        Return bank accounts for an account
        - Require login
        - Always return users' own info when no view_accountbank_account permission
        - Allow user to specify the account
        :param info:
        :param account:
        :param kwargs:
        :return:
        """
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountfinancepaymentbatchcategoryitem')

        # Allow user to specify account
        rid = get_rid(account)
        return AccountFinancePaymentBatchCategoryItem.objects.filter(account=rid.id).order_by('-year', '-month')


class CreateAccountFinancePaymentBatchCategoryItem(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        finance_payment_batch_category = graphene.ID(required=True)
        year = graphene.Int(required=True)
        month = graphene.Int(required=True)
        amount = graphene.Decimal(required=True, default_value=Decimal(0))
        description = graphene.String(required=False)

    account_finance_payment_batch_category_item = graphene.Field(AccountFinancePaymentBatchCategoryItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountfinancepaymentbatchcategoryitem')

        # Validate input
        result = validate_create_update_input(input, update=False)

        account_finance_payment_batch_category_item = AccountFinancePaymentBatchCategoryItem(
            account=result['account'],
            finance_payment_batch_category=result['finance_payment_batch_category'],
            year=input['year'],
            month=input['month'],
            amount=input['amount']
        )

        if 'description' in input:
            account_finance_payment_batch_category_item.description = input['description']

        account_finance_payment_batch_category_item.save()

        return CreateAccountFinancePaymentBatchCategoryItem(
            account_finance_payment_batch_category_item=account_finance_payment_batch_category_item
        )


class UpdateAccountFinancePaymentBatchCategoryItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        finance_payment_batch_category = graphene.ID(required=False)
        year = graphene.Int(required=False)
        month = graphene.Int(required=False)
        amount = graphene.Decimal(required=False)
        description = graphene.String(required=False)
        
    account_finance_payment_batch_category_item = graphene.Field(AccountFinancePaymentBatchCategoryItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountfinancepaymentbatchcategoryitem')
    
        rid = get_rid(input['id'])
        account_finance_payment_batch_category_item = AccountFinancePaymentBatchCategoryItem.objects.filter(
            id=rid.id
        ).first()
        if not account_finance_payment_batch_category_item:
            raise Exception('Invalid Account Finance Payment Batch Category Item ID!')

        result = validate_create_update_input(input, update=True)
        
        if 'finance_payment_batch_category' in result:
            account_finance_payment_batch_category_item.finance_payment_batch_category = \
                result['finance_payment_batch_category']
            
        if 'year' in input:
            account_finance_payment_batch_category_item.year = input['year']

        if 'month' in input:
            account_finance_payment_batch_category_item.month = input['month']

        if 'amount' in input:
            account_finance_payment_batch_category_item.amount = input['amount']

        if 'description' in input:
            account_finance_payment_batch_category_item.description = input['description']
        
        account_finance_payment_batch_category_item.save()

        return UpdateAccountFinancePaymentBatchCategoryItem(
            account_finance_payment_batch_category_item=account_finance_payment_batch_category_item
        )


class DeleteAccountFinancePaymentBatchCategoryItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountfinancepaymentbatchcategoryitem')

        rid = get_rid(input['id'])
        account_finance_payment_batch_category_item = AccountFinancePaymentBatchCategoryItem.objects.filter(
            id=rid.id
        ).first()
        if not account_finance_payment_batch_category_item:
            raise Exception('Invalid Account Finance Payment Batch Category Item ID!')

        ok = bool(account_finance_payment_batch_category_item.delete())

        return DeleteAccountFinancePaymentBatchCategoryItem(ok=ok)


class AccountFinancePaymentBatchCategoryItemMutation(graphene.ObjectType):
    create_account_finance_payment_batch_category_item = CreateAccountFinancePaymentBatchCategoryItem.Field()
    update_account_finance_payment_batch_category_item = UpdateAccountFinancePaymentBatchCategoryItem.Field()
    delete_account_finance_payment_batch_category_item = DeleteAccountFinancePaymentBatchCategoryItem.Field()
