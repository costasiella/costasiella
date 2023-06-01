from django.utils.translation import gettext as _
from django.conf import settings

import validators
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..dudes import FinanceExpenseDude
from ..models import Business, FinanceExpense, FinanceGLAccount, FinanceCostCenter
from ..modules.gql_tools import require_login_and_permission, get_rid, get_content_file_from_base64_str
from ..modules.finance_tools import display_float_as_amount
from ..modules.messages import Messages

m = Messages()


class FinanceExpenseNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    url_protected_document = graphene.String()
    amount_display = graphene.String()
    tax_display = graphene.String()
    subtotal_display = graphene.String()
    total_amount_display = graphene.String()
    total_tax_display = graphene.String()
    total_display = graphene.String()
    percentage_display = graphene.String()


class FinanceExpenseNode(DjangoObjectType):
    class Meta:
        model = FinanceExpense
        fields = (
            'date',
            'summary',
            'description',
            'amount',
            'tax',
            'subtotal',
            'percentage',
            'total_amount',
            'total_tax',
            'total',
            'supplier',
            'finance_glaccount',
            'finance_costcenter',
            'document'
        )
        filter_fields = {
            'date': ['exact', 'gte', 'lte'],
            'summary': ['icontains'], 
            'description': ['icontains'],
            'supplier': ['exact'],
            'finance_glaccount': ['exact'], 
            'finance_costcenter': ['exact']
        }
        interfaces = (graphene.relay.Node, FinanceExpenseNodeInterface, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeexpense')

        return self._meta.model.objects.get(id=id)

    def resolve_url_protected_document(self, info):
        # This is here for compatibility reasons.
        # TODO: Update frontend to query document.url field instead
        if self.document:
            return self.document.url
        else:
            return ''

    def resolve_amount_display(self, info):
        return display_float_as_amount(self.amount)

    def resolve_tax_display(self, info):
        return display_float_as_amount(self.tax)

    def resolve_subtotal_display(self, info):
        return display_float_as_amount(self.subtotal)

    def resolve_total_amount_display(self, info):
        return display_float_as_amount(self.total_amount)

    def resolve_total_tax_display(self, info):
        return display_float_as_amount(self.total_tax)

    def resolve_total_display(self, info):
        return display_float_as_amount(self.total)

    def resolve_percentage_display(self, info):
        return f"{self.percentage} %"


class FinanceExpenseQuery(graphene.ObjectType):
    finance_expenses = DjangoFilterConnectionField(FinanceExpenseNode)
    finance_expense = graphene.relay.Node.Field(FinanceExpenseNode)

    def resolve_finance_expenses(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeexpense')

        return FinanceExpense.objects.all().order_by('-date')


def validate_create_update_input(input):
    """
    Validate input
    """
    result = {}

    if 'document' in input or 'document_file_name' in input:
        if not (input.get('document', None) and input.get('document_file_name', None)):
            raise Exception(_('When setting "document" or "documentFileName", both fields need to be present and set'))

    # Check supplier (business)
    if 'supplier' in input:
        if input['supplier']:
            rid = get_rid(input['supplier'])
            supplier = Business.objects.get(id=rid.id)
            result['supplier'] = supplier
            if not supplier:
                raise Exception('Invalid Supplier (Business) ID!')

    # Check finance costcenter
    if 'finance_costcenter' in input:
        if input['finance_costcenter']:
            rid = get_rid(input['finance_costcenter'])
            finance_costcenter = FinanceCostCenter.objects.get(id=rid.id)
            result['finance_costcenter'] = finance_costcenter
            if not finance_costcenter:
                raise Exception('Invalid Finance Cost Center ID!')

    # Check account
    if 'finance_glaccount' in input:
        if input['finance_glaccount']:
            rid = get_rid(input['finance_glaccount'])
            finance_glaccount = FinanceGLAccount.objects.get(id=rid.id)
            result['finance_glaccount'] = finance_glaccount
            if not finance_glaccount:
                raise Exception('Invalid Finance GL Account ID!')

    return result


class CreateFinanceExpense(graphene.relay.ClientIDMutation):
    class Input:
        date = graphene.types.datetime.Date(required=True)
        summary = graphene.String(required=True)
        description = graphene.String(required=False)
        amount = graphene.Decimal(required=True)
        tax = graphene.Decimal(required=True)
        percentage = graphene.Decimal(required=False, default_vaule=100)
        supplier = graphene.ID(required=False)
        finance_glaccount = graphene.ID(required=False)
        finance_costcenter = graphene.ID(required=False)
        document_file_name = graphene.String(required=True)
        document = graphene.String(required=True)  # File als base64 encoded string

    finance_expense = graphene.Field(FinanceExpenseNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeexpense')

        result = validate_create_update_input(input)

        finance_expense = FinanceExpense(
            date=input['date'],
            summary=input['summary'],
            amount=input['amount'],
            tax=input['tax'],
            document=get_content_file_from_base64_str(data_str=input['document'],
                                             file_name=input['document_file_name'])
        )

        if 'percentage' in input:
            finance_expense.percentage = input['percentage']

        if 'description' in input:
            finance_expense.description = input['description']

        if 'supplier' in result:
            finance_expense.supplier = result['supplier']

        if 'finance_glaccount' in result:
            finance_expense.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            finance_expense.finance_costcenter = result['finance_costcenter']

        finance_expense.save()

        return CreateFinanceExpense(finance_expense=finance_expense)


class UpdateFinanceExpense(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        date = graphene.types.datetime.Date(required=False)
        summary = graphene.String(required=False)
        description = graphene.String(required=False)
        amount = graphene.Decimal(required=False)
        tax = graphene.Decimal(required=False)
        percentage = graphene.Decimal(required=False)
        supplier = graphene.ID(required=False)
        finance_glaccount = graphene.ID(required=False)
        finance_costcenter = graphene.ID(required=False)
        document_file_name = graphene.String(required=False)
        document = graphene.String(required=False)  # File als base64 encoded string
        
    finance_expense = graphene.Field(FinanceExpenseNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeexpense')

        rid = get_rid(input['id'])

        finance_expense = FinanceExpense.objects.filter(id=rid.id).first()
        if not finance_expense:
            raise Exception('Invalid Finance Expense ID!')

        result = validate_create_update_input(input)

        if 'date' in input:
            finance_expense.date = input['date']

        if 'summary' in input:
            finance_expense.summary = input['summary']

        if 'description' in input:
            finance_expense.description = input['description']

        if 'amount' in input:
            finance_expense.amount = input['amount']

        if 'tax' in input:
            finance_expense.tax = input['tax']

        if 'percentage' in input:
            finance_expense.percentage = input['percentage']

        if 'supplier' in result:
            finance_expense.supplier = result['supplier']

        if 'finance_glaccount' in result:
            finance_expense.finance_glaccount = result['finance_glaccount']

        if 'finance_costcenter' in result:
            finance_expense.finance_costcenter = result['finance_costcenter']

        if 'document' in input:
            finance_expense.document = get_content_file_from_base64_str(
                data_str=input['document'],
                file_name=input['document_file_name']
            )

        finance_expense.save()

        return UpdateFinanceExpense(finance_expense=finance_expense)


class DeleteFinanceExpense(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financeexpense')

        rid = get_rid(input['id'])
        finance_expense = FinanceExpense.objects.filter(id=rid.id).first()
        if not finance_expense:
            raise Exception('Invalid Finance Expense ID!')

        ok = bool(finance_expense.delete())

        return DeleteFinanceExpense(ok=ok)

class DuplicateFinanceExpense(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    finance_expense = graphene.Field(FinanceExpenseNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeexpense')

        rid = get_rid(input['id'])
        finance_expense = FinanceExpense.objects.filter(id=rid.id).first()
        if not finance_expense:
            raise Exception('Invalid Finance Expense ID!')

        # Duplicate finance expense
        finance_expense_dude = FinanceExpenseDude()
        new_finance_expense = finance_expense_dude.duplicate(finance_expense)

        # Return duplicated schedule event
        return DuplicateFinanceExpense(finance_expense=new_finance_expense)


class FinanceExpenseMutation(graphene.ObjectType):
    delete_finance_expense = DeleteFinanceExpense.Field()
    create_finance_expense = CreateFinanceExpense.Field()
    update_finance_expense = UpdateFinanceExpense.Field()
    duplicate_finance_expense = DuplicateFinanceExpense.Field()
