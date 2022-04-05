from django.utils.translation import gettext as _
from django.utils import timezone
import graphene

from ..dudes import InsightRevenueDude
from ..modules.gql_tools import require_login_and_permission


class RevenueTotalClasspassesType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_total_classpasses")

    def resolve_data(self, info):       
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_total_in_category_for_year(year, 'CLASSPASSES')
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class RevenueSubTotalClasspassesType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_subtotal_classpasses")

    def resolve_data(self, info):
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_subtotal_in_category_for_year(year, 'CLASSPASSES')
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class RevenueTaxClasspassesType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_tax_classpasses")

    def resolve_data(self, info):
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_tax_in_category_for_year(year, 'CLASSPASSES')
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class InsightRevenueClasspassesQuery(graphene.ObjectType):
    insight_revenue_total_classpasses = graphene.Field(RevenueTotalClasspassesType,
                                                         year=graphene.Int())
    insight_revenue_subtotal_classpasses = graphene.Field(RevenueSubTotalClasspassesType,
                                                            year=graphene.Int())
    insight_revenue_tax_classpasses = graphene.Field(RevenueTaxClasspassesType,
                                                       year=graphene.Int())

    def resolve_insight_revenue_total_classpasses(self,
                                                    info,
                                                    year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_total_classpasses = RevenueTotalClasspassesType()
        revenue_total_classpasses.year = year

        return revenue_total_classpasses

    def resolve_insight_revenue_subtotal_classpasses(self, info,
                                         year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_subtotal_classpasses = RevenueSubTotalClasspassesType()
        revenue_subtotal_classpasses.year = year

        return revenue_subtotal_classpasses

    def resolve_insight_revenue_tax_classpasses(self, info,
                                    year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_tax_classpasses = RevenueTaxClasspassesType()
        revenue_tax_classpasses.year = year

        return revenue_tax_classpasses
