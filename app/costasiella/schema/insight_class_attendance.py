import datetime


from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q, FilteredRelation, OuterRef, Subquery

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..dudes import InsightClassAttendanceDude
from ..models import ScheduleItem

from ..modules.gql_tools import get_rid, require_login_and_permission
from .schedule_item import ScheduleItemNode


class ClassAttendanceWeekCountType(graphene.ObjectType):
    week = graphene.Int()
    attendance_count_current_year = graphene.Int()
    attendance_count_previous_year = graphene.Int()


class InsightClassAttendanceYearType(graphene.ObjectType):
    year = graphene.Int()
    schedule_item = graphene.Field(ScheduleItemNode)
    weeks = graphene.List(ClassAttendanceWeekCountType)

    def resolve_weeks(self, info):
        insight_class_attendance_dude = InsightClassAttendanceDude()

        unprocessed_data = insight_class_attendance_dude.get_data(self.schedule_item, self.year)

        weeks = []
        for item in unprocessed_data:
            class_attendance_week_count_type = ClassAttendanceWeekCountType()
            class_attendance_week_count_type.week = item['week']
            class_attendance_week_count_type.attendance_count_current_year = item['attendance_count_current_year']
            class_attendance_week_count_type.attendance_count_previous_year = item['attendance_count_previous_year']

            weeks.append(class_attendance_week_count_type)

        return weeks


class InsightClassAttendanceQuery(graphene.ObjectType):
    insight_class_attendance_count_year = graphene.Field(InsightClassAttendanceYearType,
                                                         year=graphene.Int(),
                                                         schedule_item=graphene.ID())

    def resolve_insight_class_attendance_count_year(
            self,
            info,
            year=graphene.Int(required=True, default_value=timezone.now().year),
            schedule_item=graphene.ID(required=True)
    ):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemattendance')

        rid = get_rid(schedule_item)
        schedule_item = ScheduleItem.objects.filter(id=rid.id).first()
        if not schedule_item:
            raise Exception('Invalid ScheduleItem ID!')

        class_attendance_year_count = InsightClassAttendanceYearType()
        class_attendance_year_count.year = year
        class_attendance_year_count.schedule_item = schedule_item

        return class_attendance_year_count
