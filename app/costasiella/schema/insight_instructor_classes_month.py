import datetime


from django.utils.translation import gettext as _
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q, FilteredRelation, OuterRef, Subquery

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import ScheduleItem

from ..modules.gql_tools import get_rid, require_login_and_permission
from .schedule_class import ScheduleClassType, ScheduleClassesDayType
from .schedule_item import ScheduleItemNode


class InsightInstructorClassesMonthType(graphene.ObjectType):
    year = graphene.Int()
    month = graphene.Int()
    instructor = graphene.ID()
    classes = graphene.List(ScheduleClassType)

    def resolve_classes(self, info):
        from ..dudes import DateToolsDude

        date_dude = DateToolsDude()
        first_day_month = datetime.date(self.year, self.month, 1)
        last_day_month = date_dude.get_last_day_month(first_day_month)

        days = []
        delta = datetime.timedelta(days=1)
        date = first_day_month
        while date <= last_day_month:
            day = ScheduleClassesDayType()
            day.date = date
            day.public_only = False  # Show all classes (Don't filter anything from this overview)
            day.filter_id_account = self.instructor.id  # instructor filter ID
            # Call resolve classes manually
            day.classes = day.resolve_classes(info=None)

            days.append(day)
            date += delta

        # Flatten days into classes list
        classes = []
        for day in days:
            if day.classes:
                classes.extend(day.classes)

        return classes


class InsightInstructorClassesMonthQuery(graphene.ObjectType):
    insight_instructor_classes_month = graphene.Field(InsightInstructorClassesMonthType,
                                                      year=graphene.Int(),
                                                      month=graphene.Int(),
                                                      instructor=graphene.ID())

    def resolve_insight_instructor_classes_month(
            self,
            info,
            year=graphene.Int(required=True, default_value=timezone.now().year),
            month=graphene.Int(required=True, default_value=timezone.now().month),
            instructor=graphene.ID(required=True)
    ):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightinstructorclassesmonth')

        rid = get_rid(instructor)
        instructor_account = get_user_model().objects.filter(id=rid.id).first()
        if not instructor_account:
            raise Exception('Invalid account ID! (instructor)')

        insight_instructor_classes_month = InsightInstructorClassesMonthType()
        insight_instructor_classes_month.year = year
        insight_instructor_classes_month.month = month
        insight_instructor_classes_month.instructor = instructor_account
        # insight_instructor_classes_month.resolve_classes(None)

        return insight_instructor_classes_month
