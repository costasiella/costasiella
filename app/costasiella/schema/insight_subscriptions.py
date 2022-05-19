from django.utils.translation import gettext as _
from django.utils import timezone
import graphene

from ..modules.gql_tools import require_login_and_permission, require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages
from ..dudes import InsightAccountSubscriptionsDude


m = Messages()


class AccountSubscriptionsSoldType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Int)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("account_subscriptions_sold")

    def resolve_data(self, info):       
        insight_account_subscriptions_dude = InsightAccountSubscriptionsDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_account_subscriptions_dude.get_subscriptions_sold_year_summary_count(year)

        return data


class AccountSubscriptionsActiveType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Int)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("account_subscriptions_active")

    def resolve_data(self, info):       
        insight_account_subscriptions_dude = InsightAccountSubscriptionsDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_account_subscriptions_dude.get_subscriptions_active_year_summary_count(year)

        return data


class InsightSubscriptionsQuery(graphene.ObjectType):
    insight_account_subscriptions_sold = graphene.Field(AccountSubscriptionsSoldType, year=graphene.Int())
    insight_account_subscriptions_active = graphene.Field(AccountSubscriptionsActiveType, year=graphene.Int())


    def resolve_insight_account_subscriptions_sold(self,
                                                   info,
                                                   year=graphene.Int(required=True,
                                                                     default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightsubscriptions')

        print(year)

        account_subscriptions_sold = AccountSubscriptionsSoldType()
        account_subscriptions_sold.year = year

        return account_subscriptions_sold

    def resolve_insight_account_subscriptions_active(self,
                                                     info,
                                                     year=graphene.Int(required=True,
                                                                       default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightsubscriptions')

        print(year)

        account_subscriptions_active = AccountSubscriptionsActiveType()
        account_subscriptions_active.year = year

        return account_subscriptions_active
