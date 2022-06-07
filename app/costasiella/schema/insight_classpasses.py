from django.utils.translation import gettext as _
from django.utils import timezone

import graphene

from ..modules.gql_tools import require_login_and_permission
from ..modules.messages import Messages

from ..dudes import InsightAccountClasspassesDude

m = Messages()


class InsightClasspassesMonthType(graphene.ObjectType):
    month = graphene.Int()
    sold = graphene.Int()
    active = graphene.Int()


class InsightClasspassesYearType(graphene.ObjectType):
    year = graphene.Int()
    months = graphene.List(InsightClasspassesMonthType)

    def resolve_months(self, info):
        insight_account_classpasses_dude = InsightAccountClasspassesDude()

        unprocessed_data = insight_account_classpasses_dude.get_data(self.year)

        months = []
        for item in unprocessed_data:
            insight_classpasses_month_type = InsightClasspassesMonthType()
            insight_classpasses_month_type.month = item['month']
            insight_classpasses_month_type.sold = item['sold']
            insight_classpasses_month_type.active = item['active']

            months.append(insight_classpasses_month_type)

        return months


class InsightClasspassesQuery(graphene.ObjectType):
    insight_account_classpasses = graphene.Field(InsightClasspassesYearType, year=graphene.Int())

    def resolve_insight_account_classpasses(self,
                                            info,
                                            year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightclasspasses')

        account_classpasses_year = InsightClasspassesYearType()
        account_classpasses_year.year = year

        return account_classpasses_year

