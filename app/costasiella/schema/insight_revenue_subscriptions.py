from django.utils.translation import gettext as _
from django.utils import timezone
import graphene

from ..dudes import InsightRevenueDude
from ..modules.gql_tools import require_login_and_permission


class RevenueTotalSubscriptionsType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_total_subscriptions")

    def resolve_data(self, info):       
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_total_in_category_for_year(year, 'SUBSCRIPTIONS')
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class RevenueSubTotalSubscriptionsType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_subtotal")

    def resolve_data(self, info):
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_subtotal_in_category_for_year(self.year, 'SUBSCRIPTIONS')
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class RevenueTaxSubscriptionsType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_tax")

    def resolve_data(self, info):
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_tax_in_category_for_year(self.year, 'SUBSCRIPTIONS')
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class InsightRevenueSubscriptionsQuery(graphene.ObjectType):
    insight_revenue_total_subscriptions = graphene.Field(RevenueTotalSubscriptionsType,
                                                         year=graphene.Int())
    insight_revenue_subtotal_subscriptions = graphene.Field(RevenueSubTotalSubscriptionsType,
                                                            year=graphene.Int())
    insight_revenue_tax_subscriptions = graphene.Field(RevenueTaxSubscriptionsType,
                                                       year=graphene.Int())

    def resolve_insight_revenue_total_subscriptions(self,
                                                    info,
                                                    year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_total_subscriptions = RevenueTotalSubscriptionsType()
        revenue_total_subscriptions.year = year

        return revenue_total_subscriptions

    def resolve_insight_revenue_subtotal_subscriptions(self, info,
                                         year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_subtotal_subscriptions = RevenueSubTotalSubscriptionsType()
        revenue_subtotal_subscriptions.year = year

        return revenue_subtotal_subscriptions

    def resolve_insight_revenue_tax_subscriptions(self, info,
                                    year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_tax_subscriptions = RevenueTaxSubscriptionsType()
        revenue_tax_subscriptions.year = year

        return revenue_tax_subscriptions
