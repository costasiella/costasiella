from django.utils.translation import gettext as _
from django.utils import timezone
from django.conf import settings
from django.db.models import Q, FilteredRelation, OuterRef, Subquery

import datetime
import pytz

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import ScheduleItem, ScheduleItemWeeklyOTC, OrganizationShift, OrganizationLocationRoom
from ..modules.gql_tools import \
    check_if_user_has_permission, \
    require_login_and_permission, \
    require_login_and_one_of_permissions, \
    get_rid
from ..modules.messages import Messages
from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper
from .account import AccountNode
from .organization_shift import OrganizationShiftNode
from .organization_location_room import OrganizationLocationRoomNode
from .schedule_item import ScheduleItemNode


m = Messages()


def _get_resolve_shifts_filter_query(self):
    """
        Returns the filter query for the schedule
    """
    where = ''

    # if self.filter_id_teacher:
    #     where += 'AND ((CASE WHEN cotc.auth_teacher_id IS NULL \
    #                     THEN clt.auth_teacher_id  \
    #                     ELSE cotc.auth_teacher_id END) = '
    #     where += str(self.filter_id_teacher) + ' '
    #     where += 'OR (CASE WHEN cotc.auth_teacher_id2 IS NULL \
    #                     THEN clt.auth_teacher_id2  \
    #                     ELSE cotc.auth_teacher_id2 END) = '
    #     where += str(self.filter_id_teacher) + ') '
    if self.filter_id_organization_shift:
        where += 'AND (CASE WHEN csiotc.organization_shift_id IS NULL \
                        THEN csi.organization_shift_id  \
                        ELSE csiotc.organization_shift_id END) = '
        where += str(self.filter_id_organization_shift) + ' '
    if self.filter_id_organization_location_room:
        where += 'AND (CASE WHEN csiotc.organization_location_room_id IS NULL \
                        THEN csi.organization_location_room_id  \
                        ELSE csiotc.organization_location_room_id END) = '
        where += str(self.filter_id_organization_location_room) + ' '
    # if self.public_only:
    #     where += "AND csi.display_public = 1 "
        # where += "AND sl.AllowAPI = 'T' "
        # where += "AND sct.AllowAPI = 'T' "
    # if self.filter_starttime_from:
    #     where += 'AND ((CASE WHEN cotc.Starttime IS NULL \
    #                     THEN cla.Starttime  \
    #                     ELSE cotc.Starttime END) >= '
    #     where += "'" + str(self.filter_starttime_from) + "') "

    return where


# ScheduleClassType
class ScheduleShiftType(graphene.ObjectType):
    schedule_item_id = graphene.ID()
    frequency_type = graphene.String()
    date = graphene.types.datetime.Date()
    holiday = graphene.Boolean()
    holiday_name = graphene.String()
    status = graphene.String()
    description = graphene.String()
    account = graphene.Field(AccountNode)
    account_2 = graphene.Field(AccountNode)
    organization_location_room = graphene.Field(OrganizationLocationRoomNode)
    organization_shift = graphene.Field(OrganizationShiftNode)
    time_start = graphene.types.datetime.Time()
    time_end = graphene.types.datetime.Time()


class ScheduleShiftsDayType(graphene.ObjectType):
    date = graphene.types.datetime.Date()
    iso_week_day = graphene.Int()
    order_by = graphene.String()
    filter_id_organization_shift = graphene.String()
    filter_id_organization_location = graphene.String()
    shifts = graphene.List(ScheduleShiftType)

    def resolve_iso_week_day(self, info):
        return self.date.isoweekday()

    def resolve_order_by(self, info):       
        return self.order_by

    def resolve_shifts(self, info):

        def _get_where_query():
            """
                Returns the filter query for the schedule
            """
            where = ''

            # if self.filter_id_teacher:
            #     where += 'AND ((CASE WHEN cotc.auth_teacher_id IS NULL \
            #                     THEN clt.auth_teacher_id  \
            #                     ELSE cotc.auth_teacher_id END) = '
            #     where += str(self.filter_id_teacher) + ' '
            #     where += 'OR (CASE WHEN cotc.auth_teacher_id2 IS NULL \
            #                     THEN clt.auth_teacher_id2  \
            #                     ELSE cotc.auth_teacher_id2 END) = '
            #     where += str(self.filter_id_teacher) + ') '
            if self.filter_id_organization_shift:
                where += 'AND (CASE WHEN csiotc.organization_shift_id IS NULL \
                                THEN csi.organization_shift_id  \
                                ELSE csiotc.organization_shift_id END) = '
                where += '%(filter_id_organization_shift)s '
            if self.filter_id_organization_location:
                where += 'AND (CASE WHEN csiotc.organization_location_id IS NULL \
                                THEN csi_olr.organization_location_id  \
                                ELSE csiotc.organization_location_id END) = '
                where += '%(filter_id_organization_location)s '
                # where += "AND sl.AllowAPI = 'T' "
                # where += "AND sct.AllowAPI = 'T' "
            # if self.filter_starttime_from:
            #     where += 'AND ((CASE WHEN cotc.Starttime IS NULL \
            #                     THEN cla.Starttime  \
            #                     ELSE cotc.Starttime END) >= '
            #     where += "'" + str(self.filter_starttime_from) + "') "

            return where

        iso_week_day = self.resolve_iso_week_day(info)
        sorting = self.order_by
        if not sorting:  # Default to sort by location, then time
            sorting = "location"

        if sorting == 'location':
            order_by_sql = 'organization_location_name, time_start'
        else:  # sorting == 'starttime'
            order_by_sql = 'time_start, organization_location_name'

        query = """
            SELECT 
                csi.id,
                csi.frequency_type,
                CASE
                    WHEN csiotc.status = "CANCELLED"
                        THEN "CANCELLED"            
                    WHEN coho.id IS NOT NULL
                        THEN "CANCELLED"
                    WHEN csiotc.status = "OPEN" 
                        THEN csiotc.status
                    WHEN csiotc.status 
                        THEN csiotc.status                
                    ELSE ""
                END AS status,
                csiotc.description as description,
                CASE WHEN csiotc.organization_location_id IS NOT NULL
                     THEN csiotc.organization_location_id
                     ELSE csi_olr.organization_location_id
                     END AS organization_location_id,
                CASE WHEN csiotc.organization_location_id IS NOT NULL
                     THEN csiotc.organization_location_name
                     ELSE csi_ol.name
                     END AS organization_location_name,
                CASE WHEN csiotc.organization_location_room_id IS NOT NULL
                     THEN csiotc.organization_location_room_id
                     ELSE csi.organization_location_room_id
                     END AS organization_location_room_id,
                CASE WHEN csiotc.organization_shift_id IS NOT NULL
                     THEN csiotc.organization_shift_id
                     ELSE csi.organization_shift_id
                     END AS organization_shift_id,
                CASE WHEN csiotc.time_start IS NOT NULL
                     THEN csiotc.time_start
                     ELSE csi.time_start
                     END AS time_start,
                CASE WHEN csiotc.time_end IS NOT NULL
                     THEN csiotc.time_end
                     ELSE csi.time_end
                     END AS time_end,
               CASE     
                    WHEN csiotc.status = "OPEN"
                        THEN NULL
                    WHEN csiotc.account_id IS NOT NULL
                        THEN csiotc.account_id
                    ELSE csia.account_id
                    END AS account_id,
               CASE 
                    WHEN csiotc.status = "OPEN"
                        THEN NULL
                    WHEN csiotc.account_2_id IS NOT NULL
                        THEN csiotc.account_2_id
                    ELSE csia.account_2_id
                    END AS account_2_id,
               coho.id AS organization_holiday_id,
               coho.name AS organization_holiday_name
            FROM costasiella_scheduleitem csi
            LEFT JOIN costasiella_organizationlocationroom csi_olr ON csi.organization_location_room_id = csi_olr.id
            LEFT JOIN costasiella_organizationlocation csi_ol ON csi_olr.organization_location_id = csi_ol.id
            LEFT JOIN
                ( SELECT 
                    otc.id,
                    otc.schedule_item_id,
                    otc.date,
                    otc.status,
                    otc.description,
                    otc.account_id,
                    otc.account_2_id,
                    otc.organization_location_room_id,
                    otc.organization_shift_id,
                    otc.time_start,
                    otc.time_end,
                    otc_olr.organization_location_id,
                    otc_ol.name as organization_location_name
                  FROM costasiella_scheduleitemweeklyotc otc 
                  LEFT JOIN costasiella_organizationlocationroom otc_olr ON otc.organization_location_room_id = otc_olr.id
                  LEFT JOIN costasiella_organizationlocation otc_ol ON otc_olr.organization_location_id = otc_ol.id
                  WHERE date = %(shift_date)s 
                ) csiotc
                ON csi.id = csiotc.schedule_item_id
            LEFT JOIN
                ( SELECT 
                    id,
                    schedule_item_id,
                    account_id,
                    account_2_id
                  FROM costasiella_scheduleitemaccount
                  WHERE date_start <= %(shift_date)s AND 
                        (date_end >= %(shift_date)s OR date_end IS NULL)
                  ORDER BY date_start
                ) csia
                ON csia.schedule_item_id = csi.id
            LEFT JOIN
                ( SELECT coh.id, coh.name, cohl.organization_location_id
                  FROM costasiella_organizationholiday coh
                  LEFT JOIN
                    costasiella_organizationholidaylocation cohl
                    ON cohl.organization_holiday_id = coh.id
                  WHERE coh.date_start <= %(shift_date)s AND
                        coh.date_end >= %(shift_date)s) coho
                ON coho.organization_location_id = csi_ol.id
            WHERE csi.schedule_item_type = "SHIFT" 
                AND (
                        /* Selection on specific days */
                        (csi.frequency_type = "SPECIFIC" AND csi.date_start = %(shift_date)s ) OR
                        /* Weekly selection */
                        ( csi.frequency_type = "WEEKLY" AND 
                          csi.frequency_interval = %(iso_week_day)s AND 
                          csi.date_start <= %(shift_date)s AND
                         (csi.date_end >= %(shift_date)s OR csi.date_end IS NULL)
                        )            
                    )
                {where_sql}
            ORDER BY {order_by_sql}
        """.format(
            where_sql=_get_where_query(),
            order_by_sql=order_by_sql
        )

        #
        # print(query)

        ## 
        # At this time 27 Aug 2019, params don't seem to be working from a dictionary
        # https://docs.djangoproject.com/en/3.0/topics/db/sql/
        # the query should be formatted using %(shift_date)s 
        ##
        params = {
            "shift_date": str(self.date),
            "iso_week_day": iso_week_day,
            "filter_id_organization_shift": self.filter_id_organization_shift,
            "filter_id_organization_location": self.filter_id_organization_location,
        }
        schedule_items = ScheduleItem.objects.raw(query, params=params)

        shifts_list = []
        for item in schedule_items:
            holiday = False
            holiday_name = ""
            if item.organization_holiday_id:
                holiday = True
                holiday_name = item.organization_holiday_name

            schedule_item_id = to_global_id('ScheduleItemNode', item.pk)

            shifts_list.append(
                ScheduleShiftType(
                    schedule_item_id=schedule_item_id,
                    date=self.date,
                    status=item.status,
                    holiday=holiday,
                    holiday_name=holiday_name,
                    description=item.description,
                    frequency_type=item.frequency_type,
                    account=item.account,
                    account_2=item.account_2,
                    organization_location_room=item.organization_location_room,
                    organization_shift=item.organization_shift,
                    time_start=item.time_start,
                    time_end=item.time_end
                )
            )
    
        return shifts_list


def validate_schedule_shifts_query_date_input(date_from,
                                              date_until,
                                              order_by,
                                              organization_shift,
                                              organization_location,
                                              ):
    """
    Check if date_until >= date_start
    Check if delta between dates <= 7 days
    """
    result = {}

    if date_until < date_from:
        raise Exception(_("dateUntil has to be bigger then dateFrom"))

    days_between = (date_until - date_from).days
    if days_between > 6:
        raise Exception(_("dateFrom and dateUntil can't be more then 7 days apart")) 
    
    if order_by:
        sort_options = [
            'location',
            'starttime'
        ]  
        if order_by not in sort_options:
            raise Exception(_("orderBy can only be 'location' or 'starttime'"))

    if organization_shift:
        rid = get_rid(organization_shift)
        organization_shift_id = rid.id
        result['organization_shift_id'] = organization_shift_id

    if organization_location:
        rid = get_rid(organization_location)
        organization_location_id = rid.id
        result['organization_location_id'] = organization_location_id

    return result


class ScheduleShiftQuery(graphene.ObjectType):
    schedule_shift = graphene.Field(ScheduleShiftType,
                                    schedule_item_id=graphene.ID(),
                                    date=graphene.types.datetime.Date())
    schedule_shifts = graphene.List(
        ScheduleShiftsDayType,
        date_from=graphene.types.datetime.Date(), 
        date_until=graphene.types.datetime.Date(),
        order_by=graphene.String(),
        organization_shift=graphene.ID(),
        organization_location=graphene.ID(),
    )

    def resolve_schedule_shift(self,
                               info,
                               schedule_item_id,
                               date):
        """
        Resolve schedule shift
        :param info:
        :param schedule_item_id:
        :param date:
        :return:
        """
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleshift')

        rid = get_rid(schedule_item_id)
        schedule_item = ScheduleItem.objects.get(pk=rid.id)
        if not schedule_item:
            raise Exception('Invalid Schedule Item ID!')

        sih = ScheduleItemHelper()
        schedule_item = sih.schedule_item_with_otc_and_holiday_data(schedule_item, date)

        schedule_shift = ScheduleShiftType(
            date=date,
            schedule_item_id=to_global_id('ScheduleItemNode', schedule_item.pk),
            frequency_type=schedule_item.frequency_type,
            status=schedule_item.status or "",
            description=schedule_item.description or "",
            account=schedule_item.account,
            account_2=schedule_item.account_2,
            organization_location_room=schedule_item.organization_location_room,
            organization_shift=schedule_item.organization_shift,
            time_start=schedule_item.time_start,
            time_end=schedule_item.time_end,
        )

        return schedule_shift

    def resolve_schedule_shifts(self,
                                info,
                                date_from=graphene.types.datetime.Date(),
                                date_until=graphene.types.datetime.Date(),
                                order_by=None,
                                organization_shift=None,
                                organization_location=None,
                                ):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleshift')

        validation_result = validate_schedule_shifts_query_date_input(
            date_from, 
            date_until, 
            order_by,
            organization_shift,
            organization_location,
        )

        delta = datetime.timedelta(days=1)
        date = date_from
        return_list = []
        while date <= date_until:
            day = ScheduleShiftsDayType()
            day.date = date

            if order_by:
                day.order_by = order_by

            if 'organization_shift_id' in validation_result:
                day.filter_id_organization_shift = \
                    validation_result['organization_shift_id']

            if 'organization_location_id' in validation_result:
                day.filter_id_organization_location = \
                    validation_result['organization_location_id']

            return_list.append(day)
            date += delta

        return return_list


def validate_schedule_shift_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Check OrganizationLocationRoom
    if 'organization_location_room' in input:
        if input['organization_location_room']:
            rid = get_rid(input['organization_location_room'])
            organization_location_room = OrganizationLocationRoom.objects.filter(id=rid.id).first()
            result['organization_location_room'] = organization_location_room
            if not organization_location_room:
                raise Exception(_('Invalid Organization Location Room ID!'))            

    # Check OrganizationShift
    if 'organization_shift' in input:
        if input['organization_shift']:
            rid = get_rid(input['organization_shift'])
            organization_shift = OrganizationShift.objects.get(id=rid.id)
            result['organization_shift'] = organization_shift
            if not organization_shift:
                raise Exception(_('Invalid Organization Shift ID!'))

    return result


class CreateScheduleShift(graphene.relay.ClientIDMutation):
    class Input:
        frequency_type = graphene.String(required=True)
        frequency_interval = graphene.Int(required=True)
        organization_location_room = graphene.ID(required=True)
        organization_shift = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        time_start = graphene.types.datetime.Time(required=True)
        time_end = graphene.types.datetime.Time(required=True)

    schedule_item = graphene.Field(ScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleshift')

        result = validate_schedule_shift_create_update_input(input)

        schedule_item = ScheduleItem(
            schedule_item_type="SHIFT",
            frequency_type=input['frequency_type'], 
            frequency_interval=input['frequency_interval'],
            date_start=input['date_start'],
            time_start=input['time_start'],
            time_end=input['time_end'],
            organization_location_room=result['organization_location_room'],
            organization_shift=result['organization_shift']
        )

        # Optional fields
        date_end = input.get('date_end', None)
        if date_end:
            schedule_item.date_end = date_end

        # All done, save it :).
        schedule_item.save()

        return CreateScheduleShift(schedule_item=schedule_item)


class UpdateScheduleShift(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        frequency_type = graphene.String(required=False)
        frequency_interval = graphene.Int(required=False)
        organization_location_room = graphene.ID(required=False)
        organization_shift = graphene.ID(required=False)
        date_start = graphene.types.datetime.Date(required=False)
        date_end = graphene.types.datetime.Date(required=False)
        time_start = graphene.types.datetime.Time(required=True)
        time_end = graphene.types.datetime.Time(required=True)

    schedule_item = graphene.Field(ScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleshift')

        result = validate_schedule_shift_create_update_input(input)
        rid = get_rid(input['id'])

        schedule_item = ScheduleItem.objects.get(pk=rid.id)
        if not schedule_item:
            raise Exception('Invalid Schedule Item ID!')

        if schedule_item.frequency_type == "WEEKLY" and input['frequency_type'] == 'SPECIFIC':
            raise Exception('Unable to change weekly class into one time class')

        if 'frequency_type' in input:
            schedule_item.frequency_type = input['frequency_type']

        if 'frequency_interval' in input:
            schedule_item.frequency_interval = input['frequency_interval']

        if 'date_start' in input:
            schedule_item.date_start = input['date_start']

        if 'date_end' in input:
            schedule_item.date_end = input['date_end']

        if 'time_start' in input:
            schedule_item.time_start = input['time_start']

        if 'time_end' in input:
            schedule_item.time_end = input['time_end']

        # Fields requiring additional validation
        if result['organization_location_room']:
            schedule_item.organization_location_room = result['organization_location_room']

        if result['organization_shift']:
            schedule_item.organization_shift = result['organization_shift']

        # ALl done, save it :).
        schedule_item.save()

        return UpdateScheduleShift(schedule_item=schedule_item)


class DeleteScheduleShift(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleshift')

        rid = get_rid(input['id'])
        schedule_item = ScheduleItem.objects.filter(id=rid.id).first()
        if not schedule_item:
            raise Exception('Invalid Schedule Item ID!')

        ok = bool(schedule_item.delete())

        return DeleteScheduleShift(ok=ok)


class ScheduleShiftMutation(graphene.ObjectType):
    create_schedule_shift = CreateScheduleShift.Field()
    update_schedule_shift = UpdateScheduleShift.Field()
    delete_schedule_shift = DeleteScheduleShift.Field()