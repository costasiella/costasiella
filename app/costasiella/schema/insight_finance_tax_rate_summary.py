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

from ..dudes import InsightFinanceTaxSummaryDude
from ..models import ScheduleItem
from ..modules.finance_tools import display_float_as_amount
from .finance_tax_rate import FinanceTaxRateNode

from ..modules.gql_tools import get_rid, require_login_and_permission


class FinanceTaxRateSummaryDataType(graphene.ObjectType):
    finance_tax_rate = graphene.Field(FinanceTaxRateNode)
    subtotal = graphene.Decimal()
    subtotal_display = graphene.String()
    tax = graphene.Decimal()
    tax_display = graphene.String()

    def resolve_subtotal_display(self, info):
        return display_float_as_amount(self.subtotal)

    def resolve_tax_display(self, info):
        return display_float_as_amount(self.tax)


class FinanceTaxRateSummaryType(graphene.ObjectType):
    date_start = graphene.types.datetime.Date()
    date_end = graphene.types.datetime.Date()
    data = graphene.List(FinanceTaxRateSummaryDataType)

    def resolve_data(self, info):
        insight_tax_summary_dude = InsightFinanceTaxSummaryDude()
        result = insight_tax_summary_dude.get_tax_rate_summary(self.date_start, self.date_end)

        data = []
        for finance_tax_rate in result:
            data.append(
                FinanceTaxRateSummaryDataType(
                    finance_tax_rate=finance_tax_rate,
                    subtotal=finance_tax_rate.sum_subtotal or Decimal(0),
                    tax=finance_tax_rate.sum_tax or Decimal(0)
                )
            )

        return data


def validate_input(date_start, date_end):
    """
    Validate input
    """
    result = {}

    if date_end < date_start:
        raise Exception(_('dateEnd should be >= dateStart'))

    return result


class InsightFinanceTaxRateSummaryQuery(graphene.ObjectType):
    insight_finance_tax_rate_summary = graphene.Field(FinanceTaxRateSummaryType,
                                                      date_start=graphene.types.datetime.Date(),
                                                      date_end=graphene.types.datetime.Date())

    def resolve_insight_finance_tax_rate_summary(
            self,
            info,
            date_start=graphene.types.datetime.Date(required=True),
            date_end=graphene.types.datetime.Date(required=True)
    ):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightfinancetaxratesummary')

        validate_input(date_start, date_end)

        finance_tax_summary = FinanceTaxRateSummaryType()
        finance_tax_summary.date_start = date_start
        finance_tax_summary.date_end = date_end

        return finance_tax_summary
