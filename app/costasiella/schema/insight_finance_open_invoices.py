import datetime
from decimal import Decimal

from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q, FilteredRelation, OuterRef, Subquery

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..dudes import InsightFinanceOpenInvoicesDude
from ..models import ScheduleItem
from ..modules.finance_tools import display_float_as_amount
from .finance_invoice import FinanceInvoiceNode

from ..modules.gql_tools import get_rid, require_login_and_permission


class FinanceOpenInvoicesType(graphene.ObjectType):
    date = graphene.types.datetime.Date()
    finance_invoices = graphene.List(FinanceInvoiceNode)

    def resolve_finance_invoices(self, info):
        insight_finance_open_invoices_dude = InsightFinanceOpenInvoicesDude()
        open_invoices = insight_finance_open_invoices_dude.get_open_invoices_on_date(self.date)

        # data = []
        # for finance_tax_rate in result:
        #     data.append(
        #         FinanceTaxRateSummaryDataType(
        #             finance_tax_rate=finance_tax_rate,
        #             subtotal=finance_tax_rate.sum_subtotal or Decimal(0),
        #             tax=finance_tax_rate.sum_tax or Decimal(0)
        #         )
        #     )

        return open_invoices

# def validate_input(date_start, date_end):
#     """
#     Validate input
#     """
#     result = {}
#
#     if date_end < date_start:
#         raise Exception(_('dateEnd should be >= dateStart'))
#
#     return result


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
