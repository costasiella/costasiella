from django.utils.translation import gettext as _
from django.utils import timezone
import graphene

from ..dudes import InsightRevenueDude
from ..modules.gql_tools import require_login_and_permission


class RevenueTotalOtherType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_total_other")

    def resolve_data(self, info):       
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_total_in_category_for_year(year, 'OTHER')
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class RevenueSubTotalOtherType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_subtotal_other")

    def resolve_data(self, info):
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_subtotal_in_category_for_year(year, 'OTHER')
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class RevenueTaxOtherType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_tax_other")

    def resolve_data(self, info):
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_tax_in_category_for_year(year, 'OTHER')
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class InsightRevenueOtherQuery(graphene.ObjectType):
    insight_revenue_total_other = graphene.Field(RevenueTotalOtherType,
                                                         year=graphene.Int())
    insight_revenue_subtotal_other = graphene.Field(RevenueSubTotalOtherType,
                                                            year=graphene.Int())
    insight_revenue_tax_other = graphene.Field(RevenueTaxOtherType,
                                                       year=graphene.Int())

    def resolve_insight_revenue_total_other(self,
                                            info,
                                            year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_total_other = RevenueTotalOtherType()
        revenue_total_other.year = year

        return revenue_total_other

    def resolve_insight_revenue_subtotal_other(self,
                                               info,
                                               year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_subtotal_other = RevenueSubTotalOtherType()
        revenue_subtotal_other.year = year

        return revenue_subtotal_other

    def resolve_insight_revenue_tax_other(self,
                                          info,
                                          year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_tax_other = RevenueTaxOtherType()
        revenue_tax_other.year = year

        return revenue_tax_other
