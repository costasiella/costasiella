from django.utils.translation import gettext as _
from django.utils import timezone

import graphene

from ..dudes import InsightRevenueDude
from ..modules.gql_tools import require_login_and_permission
from ..modules.finance_tools import display_float_as_amount


class InsightRevenueTotalMonthType(graphene.ObjectType):
    month = graphene.Int()
    total = graphene.Decimal()
    total_display = graphene.String()
    subtotal = graphene.Decimal()
    tax = graphene.Decimal()


class InsightRevenueTotalYearType(graphene.ObjectType):
    year = graphene.Int()
    months = graphene.List(InsightRevenueTotalMonthType)

    def resolve_months(self, info):
        insight_revenue_dude = InsightRevenueDude()

        unprocessed_data = insight_revenue_dude.get_data(self.year)

        months = []
        for item in unprocessed_data:
            insight_revenue_total_month_type = InsightRevenueTotalMonthType()
            insight_revenue_total_month_type.month = item['month']
            insight_revenue_total_month_type.total = item['total']
            insight_revenue_total_month_type.total_display = display_float_as_amount(item['total'])
            insight_revenue_total_month_type.subtotal = item['subtotal']
            insight_revenue_total_month_type.tax = item['tax']

            months.append(insight_revenue_total_month_type)

        return months

#
# class RevenueTotalType(graphene.ObjectType):
#     description = graphene.String()
#     year = graphene.Int()
#     total = graphene.List(graphene.Decimal)
#     total_display = graphene.List(graphene.String)
#     subtotal = graphene.List(graphene.Decimal)
#     tax = graphene.List(graphene.Decimal)
#
#     def resolve_description(self, info):
#         return _("revenue_total")
#
#     def resolve_total(self, info):
#         insight_revenue_dude = InsightRevenueDude()
#         year = self.year
#         if not year:
#             year = timezone.now().year
#
#         data = insight_revenue_dude.get_revenue_total_year(year)
#         amounts = []
#         for month in data:
#             amounts.append(data[month])
#
#         return amounts
#
#     def resolve_total_display(self, info):
#         insight_revenue_dude = InsightRevenueDude()
#         year = self.year
#         if not year:
#             year = timezone.now().year
#
#         data = insight_revenue_dude.get_revenue_total_year(year)
#         amounts = []
#         for month in data:
#             amounts.append(display_float_as_amount(data[month]))
#
#         return amounts
#
#     def resolve_subtotal(self, info):
#         insight_revenue_dude = InsightRevenueDude()
#         year = self.year
#         if not year:
#             year = timezone.now().year
#
#         data = insight_revenue_dude.get_revenue_subtotal_year(year)
#         amounts = []
#         for month in data:
#             amounts.append(data[month])
#
#         return amounts
#
#     def resolve_tax(self, info):
#         insight_revenue_dude = InsightRevenueDude()
#         year = self.year
#         if not year:
#             year = timezone.now().year
#
#         data = insight_revenue_dude.get_revenue_tax_year(self.year)
#         amounts = []
#         for month in data:
#             amounts.append(data[month])
#
#         return amounts


class InsightRevenueQuery(graphene.ObjectType):
    insight_revenue_total = graphene.Field(InsightRevenueTotalYearType, year=graphene.Int())

    def resolve_insight_revenue_total(self,
                                      info,
                                      year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_total_year = InsightRevenueTotalYearType()
        revenue_total_year.year = year

        return revenue_total_year
