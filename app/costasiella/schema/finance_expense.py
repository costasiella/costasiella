from django.utils.translation import gettext as _

import validators
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import FinanceExpense
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class FinanceTaxRateNode(DjangoObjectType):
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
    finance_expenses = DjangoFilterConnectionField(FinanceTaxRateNode)
    finance_expense = graphene.relay.Node.Field(FinanceTaxRateNode)

    def resolve_finance_expenses(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeexpense')

        ## return everything:
        # if user.has_perm('costasiella.view_financeexpense'):
        return FinanceExpense.objects.filter(archived=archived).order_by('date')


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

        errors = []
        if not len(input['name']):
            raise GraphQLError(_('Name is required'))

        # if not input['percentage'] and not input['percentage'] == 0:
        #     raise GraphQLError(_('Percentage is required'))

        if not validators.between(input['percentage'], 0, 100):
            raise GraphQLError(_('Percentage has to be between 0 and 100'))

        finance_tax_rate = FinanceTaxRate(
            name=input['name'], 
            percentage=input['percentage'],
            rate_type=input['rateType']
        )
        if input['code']:
            finance_tax_rate.code = input['code']

        finance_tax_rate.save()

        return CreateFinanceTaxRate(finance_tax_rate=finance_tax_rate)


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