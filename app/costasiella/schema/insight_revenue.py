import datetime


from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q, FilteredRelation, OuterRef, Subquery

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..dudes import InsightRevenueDude

from ..modules.gql_tools import require_login_and_permission



class RevenueTotalType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_total")

    def resolve_data(self, info):       
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_total_year(self.year)
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class RevenueSubTotalType(graphene.ObjectType):
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

        data = insight_revenue_dude.get_revenue_subtotal_year(self.year)
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class RevenueTaxType(graphene.ObjectType):
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

        data = insight_revenue_dude.get_revenue_tax_year(self.year)
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class InsightRevenueQuery(graphene.ObjectType):
    insight_revenue_total = graphene.Field(RevenueTotalType, year=graphene.Int())
    insight_revenue_subtotal = graphene.Field(RevenueSubTotalType, year=graphene.Int())
    insight_revenue_tax = graphene.Field(RevenueTaxType, year=graphene.Int())


    def resolve_insight_revenue_total(self,
                                      info,
                                      year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_total = RevenueTotalType()
        revenue_total.year = year

        return revenue_total

    def resolve_insight_revenue_subtotal(self,
                                      info,
                                      year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_subtotal = RevenueSubTotalType()
        revenue_subtotal.year = year

        return revenue_subtotal

    def resolve_insight_revenue_tax(self,
                                      info,
                                      year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_tax = RevenueTaxType()
        revenue_tax.year = year

        return revenue_tax


    # def resolve_insight_account_classpasses_active(self,
    #                                                 info,
    #                                                 year=graphene.Int(required=True, default_value=timezone.now().year)):
    #     user = info.context.user
    #     require_login_and_permission(user, 'costasiella.view_insightclasspassesactive')
    #
    #     account_classpasses_active = AccountClasspassesActiveType()
    #     account_classpasses_active.year = year
    #
    #     return account_classpasses_active

