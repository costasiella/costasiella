from django.utils.translation import gettext as _
from django.utils import timezone

import graphene

from ..dudes import InsightRevenueDude
from ..modules.gql_tools import require_login_and_permission


class RevenueTotalType(graphene.ObjectType):
    description = graphene.String()
    year = graphene.Int()
    total = graphene.List(graphene.Decimal)
    subtotal = graphene.List(graphene.Decimal)
    tax = graphene.List(graphene.Decimal)

    def resolve_description(self, info):
        return _("revenue_total")

    def resolve_total(self, info):
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_total_year(year)
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts

    def resolve_subtotal(self, info):
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_subtotal_year(year)
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts

    def resolve_tax(self, info):
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_tax_year(self.year)
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class InsightRevenueQuery(graphene.ObjectType):
    insight_revenue_total = graphene.Field(RevenueTotalType, year=graphene.Int())

    def resolve_insight_revenue_total(self,
                                      info,
                                      year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_total = RevenueTotalType()
        revenue_total.year = year

        return revenue_total
