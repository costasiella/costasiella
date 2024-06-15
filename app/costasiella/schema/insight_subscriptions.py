from django.utils.translation import gettext as _
from django.utils import timezone
import graphene

from ..modules.gql_tools import require_login_and_permission
from ..modules.messages import Messages
from ..dudes import InsightAccountSubscriptionsDude

m = Messages()


class InsightAccountSubscriptionsMonthType(graphene.ObjectType):
    month = graphene.Int()
    sold = graphene.Int()
    stopped = graphene.Int()
    active = graphene.Int()
    paused = graphene.Int()
    blocked = graphene.Int()


class InsightAccountSubscriptionsYearType(graphene.ObjectType):
    year = graphene.Int()
    months = graphene.List(InsightAccountSubscriptionsMonthType)

    def resolve_months(self, info):
        insight_account_subscriptions_dude = InsightAccountSubscriptionsDude()

        unprocessed_data = insight_account_subscriptions_dude.get_data(self.year)

        months = []
        for item in unprocessed_data:
            insight_subscriptions_month_type = InsightAccountSubscriptionsMonthType()
            insight_subscriptions_month_type.month = item['month']
            insight_subscriptions_month_type.sold = item['sold']
            insight_subscriptions_month_type.stopped = item['stopped']
            insight_subscriptions_month_type.active = item['active']
            insight_subscriptions_month_type.paused = item['paused']
            insight_subscriptions_month_type.blocked = item['blocked']

            months.append(insight_subscriptions_month_type)

        return months


class InsightSubscriptionsQuery(graphene.ObjectType):
    insight_account_subscriptions = graphene.Field(InsightAccountSubscriptionsYearType, year=graphene.Int())

    def resolve_insight_account_subscriptions(self,
                                              info,
                                              year=graphene.Int(required=True,
                                                                default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightsubscriptions')

        account_subscriptions_year = InsightAccountSubscriptionsYearType()
        account_subscriptions_year.year = year

        return account_subscriptions_year
