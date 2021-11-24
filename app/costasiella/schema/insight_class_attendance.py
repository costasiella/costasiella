import datetime


from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q, FilteredRelation, OuterRef, Subquery

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..dudes import Insight
from ..models import ScheduleItem

from ..modules.gql_tools import get_rid, require_login_and_permission


class ClassAttendanceYearCountType(graphene.ObjectType):
    description = graphene.String()
    data = graphene.List(graphene.Decimal)
    year = graphene.Int()
    schedule_item = graphene.ID()

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


class InsightRevenueQuery(graphene.ObjectType):
    insight_class_attendance_count_year = graphene.Field(RevenueTotalType,
                                                         year=graphene.Int(),
                                                         schedule_item=graphene.ID())


    def resolve_insight_revenue_total(self,
                                      info,
                                      year=graphene.Int(required=True, default_value=timezone.now().year),
                                      schedule_item=graphene.ID(required=True)):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemattendance')

        rid = get_rid(input['schedule_item'])
        schedule_item = ScheduleItem.objects.filter(id=rid.id).first()
        if not schedule_item:
            raise Exception('Invalid ScheduleItem ID!')

        class_attendance_year_count = ClassAttendanceYearCountType()
        class_attendance_year_count.year = year
        class_attendance_year_count.schedule_item = schedule_item

        return class_attendance_year_count
