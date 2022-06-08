from django.utils.translation import gettext as _
from django.utils import timezone
import graphene

from ..dudes import InsightRevenueDude
from ..modules.gql_tools import require_login_and_permission
from ..modules.finance_tools import display_float_as_amount


class InsightRevenuSubscriptionsMonthType(graphene.ObjectType):
    month = graphene.Int()
    total = graphene.Decimal()
    total_display = graphene.String()
    subtotal = graphene.Decimal()
    tax = graphene.Decimal()


class InsightRevenueSubscriptionsYearType(graphene.ObjectType):
    year = graphene.Int()
    months = graphene.List(InsightRevenuSubscriptionsMonthType)

    def resolve_months(self, info):
        insight_revenue_dude = InsightRevenueDude()

        unprocessed_data = insight_revenue_dude.get_data_in_category(self.year, 'SUBSCRIPTIONS')

        months = []
        for item in unprocessed_data:
            insight_revenue_subscriptions_month_type = InsightRevenuSubscriptionsMonthType()
            insight_revenue_subscriptions_month_type.month = item['month']
            insight_revenue_subscriptions_month_type.total = item['total']
            insight_revenue_subscriptions_month_type.total_display = display_float_as_amount(item['total'])
            insight_revenue_subscriptions_month_type.subtotal = item['subtotal']
            insight_revenue_subscriptions_month_type.tax = item['tax']

            months.append(insight_revenue_subscriptions_month_type)

        return months


class InsightRevenueSubscriptionsQuery(graphene.ObjectType):
    insight_revenue_subscriptions = graphene.Field(InsightRevenueSubscriptionsYearType, year=graphene.Int())

    def resolve_insight_revenue_subscriptions(self,
                                              info,
                                              year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_subscriptions_year = InsightRevenueSubscriptionsYearType()
        revenue_subscriptions_year.year = year

        return revenue_subscriptions_year

