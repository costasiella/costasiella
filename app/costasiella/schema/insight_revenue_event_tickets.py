from django.utils.translation import gettext as _
from django.utils import timezone
import graphene

from ..dudes import InsightRevenueDude
from ..modules.gql_tools import require_login_and_permission


class RevenueTotalEventTicketsType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_total_event_tickets")

    def resolve_data(self, info):       
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_total_in_category_for_year(year, 'EVENTTICKETS')
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class RevenueSubTotalEventTicketsType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_subtotal_event_tickets")

    def resolve_data(self, info):
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_subtotal_in_category_for_year(year, 'EVENTTICKETS')
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class RevenueTaxEventTicketsType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()

    def resolve_description(self, info):
        return _("revenue_tax_event_tickets")

    def resolve_data(self, info):
        insight_revenue_dude = InsightRevenueDude()
        year = self.year
        if not year:
            year = timezone.now().year

        data = insight_revenue_dude.get_revenue_tax_in_category_for_year(year, 'EVENTTICKETS')
        amounts = []
        for month in data:
            amounts.append(data[month])

        return amounts


class InsightRevenueEventTicketsQuery(graphene.ObjectType):
    insight_revenue_total_event_tickets = graphene.Field(RevenueTotalEventTicketsType,
                                                         year=graphene.Int())
    insight_revenue_subtotal_event_tickets = graphene.Field(RevenueSubTotalEventTicketsType,
                                                            year=graphene.Int())
    insight_revenue_tax_event_tickets = graphene.Field(RevenueTaxEventTicketsType,
                                                       year=graphene.Int())

    def resolve_insight_revenue_total_event_tickets(self,
                                                    info,
                                                    year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_total_event_tickets = RevenueTotalEventTicketsType()
        revenue_total_event_tickets.year = year

        return revenue_total_event_tickets

    def resolve_insight_revenue_subtotal_event_tickets(self, info,
                                         year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_subtotal_event_tickets = RevenueSubTotalEventTicketsType()
        revenue_subtotal_event_tickets.year = year

        return revenue_subtotal_event_tickets

    def resolve_insight_revenue_tax_event_tickets(self, info,
                                    year=graphene.Int(required=True, default_value=timezone.now().year)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightrevenue')

        revenue_tax_event_tickets = RevenueTaxEventTicketsType()
        revenue_tax_event_tickets.year = year

        return revenue_tax_event_tickets
