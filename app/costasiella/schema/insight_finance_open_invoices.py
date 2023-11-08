import graphene

from ..dudes import InsightFinanceOpenInvoicesDude
from ..modules.finance_tools import display_float_as_amount
from .finance_invoice import FinanceInvoiceNode

from ..modules.gql_tools import require_login_and_permission


class FinanceOpenInvoicesType(graphene.ObjectType):
    date = graphene.types.datetime.Date()
    finance_invoices = graphene.List(FinanceInvoiceNode)
    total_open_on_date = graphene.Decimal()
    total_open_on_date_display = graphene.String()

    def resolve_finance_invoices(self, info):
        insight_finance_open_invoices_dude = InsightFinanceOpenInvoicesDude()
        open_invoices = insight_finance_open_invoices_dude.get_open_invoices_on_date(self.date)

        return open_invoices

    def resolve_total_open_on_date(self, info):
        total_open = 0
        for finance_invoice in self.resolve_finance_invoices(info):
            total_open += finance_invoice.balance

        return total_open

    def resolve_total_open_on_date_display(self, info):
        return display_float_as_amount(self.resolve_total_open_on_date(info))


class InsightFinanceOpenInvoicesQuery(graphene.ObjectType):
    insight_finance_open_invoices = graphene.Field(FinanceOpenInvoicesType,
                                                   date=graphene.types.datetime.Date())

    def resolve_insight_finance_open_invoices(
            self,
            info,
            date=graphene.types.datetime.Date(required=True)
    ):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightfinanceinvoicesopenondate')

        finance_open_invoices = FinanceOpenInvoicesType()
        finance_open_invoices.date = date

        return finance_open_invoices
