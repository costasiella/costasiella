from django.utils.translation import gettext as _

import validators
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Business, FinanceExpense, FinanceGLAccount, FinanceCostCenter
from ..modules.gql_tools import require_login_and_permission, get_rid, get_content_file_from_base64_str
from ..modules.messages import Messages

m = Messages()


class FinanceExpenseNode(DjangoObjectType):
    class Meta:
        model = FinanceExpense
        fields = (
            'date',
            'summary',
            'description',
            'amount',
            'tax',
            'total',
            'finance_glaccount',
            'finance_costcenter',
            'document'
        )
        filter_fields = {
            'date': ['exact'], 
            'summary': ['icontains'], 
            'description': ['icontains'], 
            'finance_glaccount': ['exact'], 
            'finance_costcenter': ['exact']
        }
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeexpense')

        return self._meta.model.objects.get(id=id)


class FinanceExpenseQuery(graphene.ObjectType):
    finance_expenses = DjangoFilterConnectionField(FinanceExpenseNode)
    finance_expense = graphene.relay.Node.Field(FinanceExpenseNode)

    def resolve_finance_expenses(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeexpense')

        return FinanceExpense.objects.all().order_by('date')


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
            date=input['name'],
            summary=input['summary'],
            amount=input['amount'],
            tax=input['tax'],
            document=get_content_file_from_base64_str(data_str=input['document'],
                                             file_name=input['document_file_name'])
        )

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


class UpdateFinanceTaxRate(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        percentage = graphene.Decimal(required=True)
        rateType = graphene.String(required=True)
        code = graphene.String(default_value="")
        
    finance_tax_rate = graphene.Field(FinanceTaxRateNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeexpense')

        rid = get_rid(input['id'])

        finance_tax_rate = FinanceTaxRate.objects.filter(id=rid.id).first()
        if not finance_tax_rate:
            raise Exception('Invalid Finance Tax Rate ID!')

        if not validators.between(input['percentage'], 0, 100):
            raise GraphQLError(_('Percentage has to be between 0 and 100'))

        finance_tax_rate.name = input['name']
        finance_tax_rate.percentage = input['percentage']
        finance_tax_rate.rate_type = input['rateType']
        if input['code']:
            finance_tax_rate.code = input['code']
        finance_tax_rate.save(force_update=True)

        return UpdateFinanceTaxRate(finance_tax_rate=finance_tax_rate)


class ArchiveFinanceTaxRate(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    finance_tax_rate = graphene.Field(FinanceTaxRateNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financeexpense')

        rid = get_rid(input['id'])

        finance_tax_rate = FinanceTaxRate.objects.filter(id=rid.id).first()
        if not finance_tax_rate:
            raise Exception('Invalid Finance Tax Rate ID!')

        finance_tax_rate.archived = input['archived']
        finance_tax_rate.save()

        return ArchiveFinanceTaxRate(finance_tax_rate=finance_tax_rate)


class FinanceTaxRateMutation(graphene.ObjectType):
    archive_finance_tax_rate = ArchiveFinanceTaxRate.Field()
    create_finance_tax_rate = CreateFinanceTaxRate.Field()
    update_finance_tax_rate = UpdateFinanceTaxRate.Field()