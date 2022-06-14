from django.utils.translation import gettext as _
from django.utils import timezone
import graphene

from ..dudes import InsightRevenueDude
from ..modules.gql_tools import require_login_and_permission
from ..modules.finance_tools import display_float_as_amount


class InsightRevenueClasspassesMonthType(graphene.ObjectType):
    month = graphene.Int()
    total = graphene.Decimal()
    total_display = graphene.String()
    subtotal = graphene.Decimal()
    tax = graphene.Decimal()


class InsightRevenueClasspassesYearType(graphene.ObjectType):
    year = graphene.Int()
    months = graphene.List(InsightRevenueClasspassesMonthType)

    def resolve_months(self, info):
        insight_revenue_dude = InsightRevenueDude()

        unprocessed_data = insight_revenue_dude.get_data_in_category(self.year, 'CLASSPASSES')

        months = []
        for item in unprocessed_data:
            insight_revenue_classpasses_month_type = InsightRevenueClasspassesMonthType()
            insight_revenue_classpasses_month_type.month = item['month']
            insight_revenue_classpasses_month_type.total = item['total']
            insight_revenue_classpasses_month_type.total_display = display_float_as_amount(item['total'])
            insight_revenue_classpasses_month_type.subtotal = item['subtotal']
            insight_revenue_classpasses_month_type.tax = item['tax']

            months.append(insight_revenue_classpasses_month_type)

        return months


class InsightRevenueClasspassesQuery(graphene.ObjectType):
    insight_revenue_classpasses = graphene.Field(InsightRevenueClasspassesYearType, year=graphene.Int())

    def resolve_insight_revenue_classpasses(self,
                                            info,
                                            year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_classpasses_year = InsightRevenueClasspassesYearType()
        revenue_classpasses_year.year = year

        return revenue_classpasses_year
