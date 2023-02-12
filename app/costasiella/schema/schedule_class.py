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

from ..models import Account, \
    ScheduleItem, \
    ScheduleItemAttendance, \
    ScheduleItemEnrollment, \
    ScheduleItemWeeklyOTC, \
    OrganizationClasstype, \
    OrganizationLevel, \
    OrganizationLocationRoom
from ..modules.gql_tools import \
    check_if_user_has_permission, \
    require_login_and_permission, \
    require_login_and_one_of_permissions, \
    get_rid
from ..modules.messages import Messages
from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper
from .account import AccountNode
from .organization_classtype import OrganizationClasstypeNode
from .organization_level import OrganizationLevelNode
from .organization_location_room import OrganizationLocationRoomNode
from .schedule_item import ScheduleItemNode


m = Messages()


# ScheduleClassType
class ScheduleClassType(graphene.ObjectType):
    schedule_item_id = graphene.ID()
    frequency_type = graphene.String()
    date = graphene.types.datetime.Date()
    holiday = graphene.Boolean()
    holiday_name = graphene.String()
    status = graphene.String()
    description = graphene.String()
    account = graphene.Field(AccountNode)
    role = graphene.String()
    account_2 = graphene.Field(AccountNode)
    role_2 = graphene.String()
    organization_location_room = graphene.Field(OrganizationLocationRoomNode)
    organization_classtype = graphene.Field(OrganizationClasstypeNode)
    organization_level = graphene.Field(OrganizationLevelNode)
    time_start = graphene.types.datetime.Time()
    time_end = graphene.types.datetime.Time()
    display_public = graphene.Boolean()
    info_mail_enabled = graphene.Boolean()
    info_mail_content = graphene.String()
    spaces = graphene.Int()
    enrollment_spaces = graphene.Int()
    count_booked = graphene.Int()
    count_attending = graphene.Int()
    count_attending_and_booked = graphene.Int()
    count_enrolled = graphene.Int()
    available_spaces_online = graphene.Int()
    available_spaces_total = graphene.Int()
    booking_open_on = graphene.types.datetime.Date()
    booking_status = graphene.String()
    url_booking = graphene.String()


# ScheduleClassDayType
class ScheduleClassesDayType(graphene.ObjectType):
    date = graphene.types.datetime.Date()
    booking_open_on = graphene.types.datetime.Date()
    iso_week_day = graphene.Int()
    order_by = graphene.String()
    filter_id_account = graphene.ID()
    filter_id_organization_classtype = graphene.ID()
    filter_id_organization_level = graphene.ID()
    filter_id_organization_location = graphene.ID()
    public_only = graphene.Boolean()
    classes = graphene.List(ScheduleClassType)

    def resolve_booking_open_on(self, info=None):
        """
            Returns False if no booking limit is defined, otherwise it returns the date from which
            bookings for this class will be accepted.
        """
        return calculate_booking_open_on(self.date)

    def resolve_iso_week_day(self, info):
        return self.date.isoweekday()

    def resolve_order_by(self, info):       
        return self.order_by

    def resolve_classes(self, info):
        def _get_count_attending_sql():
            """

            :return:
            """
            count_types = [
                'ATTENDING',
                'BOOKED',
                'ATTENDING_AND_BOOKED'
            ]

            count_attendance_sql = ""

            for count_type in count_types:
                count_attendance_sql += """( SELECT COUNT(csia.id) as count_sia 
                        FROM costasiella_scheduleitemattendance csia 
                        WHERE csia.schedule_item_id = csi.id AND
                              csia.date = %(class_date)s AND """

                if count_type == "ATTENDING":
                    count_attendance_sql += 'csia.booking_status = "ATTENDING" )'
                    count_attendance_sql += " AS count_attending,"
                if count_type == "BOOKED":
                    count_attendance_sql += 'csia.booking_status = "BOOKED" )'
                    count_attendance_sql += " AS count_booked,"
                if count_type == "ATTENDING_AND_BOOKED":
                    count_attendance_sql += 'csia.booking_status != "CANCELLED" )'
                    count_attendance_sql += " AS count_attending_and_booked "

            return count_attendance_sql

        def _get_where_query():
            """
                Returns the filter query for the schedule
            """
            where = ''

            # if self.filter_id_instructor:
            #     where += 'AND ((CASE WHEN cotc.auth_instructor_id IS NULL \
            #                     THEN clt.auth_instructor_id  \
            #                     ELSE cotc.auth_instructor_id END) = '
            #     where += str(self.filter_id_instructor) + ' '
            #     where += 'OR (CASE WHEN cotc.auth_instructor_id2 IS NULL \
            #                     THEN clt.auth_instructor_id2  \
            #                     ELSE cotc.auth_instructor_id2 END) = '
            #     where += str(self.filter_id_instructor) + ') '
            if self.filter_id_account:
                where += 'AND (CASE WHEN csiotc.account_id IS NULL \
                                THEN csia.account_id  \
                                ELSE csiotc.account_id END) = '
                where += '%(filter_id_account)s '
            if self.filter_id_organization_classtype:
                where += 'AND (CASE WHEN csiotc.organization_classtype_id IS NULL \
                                THEN csi.organization_classtype_id  \
                                ELSE csiotc.organization_classtype_id END) = '
                where += '%(filter_id_organization_classtype)s '
            if self.filter_id_organization_location:
                where += 'AND (CASE WHEN csiotc.organization_location_id IS NULL \
                                THEN csi_olr.organization_location_id  \
                                ELSE csiotc.organization_location_id END) = '
                where += '%(filter_id_organization_location)s '
            if self.filter_id_organization_level:
                where += 'AND (CASE WHEN csiotc.organization_level_id IS NULL \
                                THEN csi.organization_level_id  \
                                ELSE csiotc.organization_level_id END) = '
                where += '%(filter_id_organization_level)s '
            if self.public_only:
                where += "AND csi.display_public = 1 "
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
                    WHEN csia.account_id IS NULL AND csiotc.account_id IS NULL
                        THEN "OPEN" 
                    WHEN csia.account_id = "" AND csiotc.account_id = ""
                        THEN "OPEN"
                    WHEN csiotc.account_id IS NOT NULL AND csiotc.role = "SUB" 
                        THEN "SUB"
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
                CASE WHEN csiotc.organization_classtype_id IS NOT NULL
                     THEN csiotc.organization_classtype_id
                     ELSE csi.organization_classtype_id
                     END AS organization_classtype_id,
                CASE WHEN csiotc.organization_level_id IS NOT NULL
                     THEN csiotc.organization_level_id
                     ELSE csi.organization_level_id
                     END AS organization_level_id,
                CASE WHEN csiotc.time_start IS NOT NULL
                     THEN csiotc.time_start
                     ELSE csi.time_start
                     END AS time_start,
                CASE WHEN csiotc.time_end IS NOT NULL
                     THEN csiotc.time_end
                     ELSE csi.time_end
                     END AS time_end,
                csi.display_public,
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
                    WHEN csiotc.account_id IS NOT NULL
                        THEN csiotc.role
                    ELSE csia.role
                    END AS role,
               CASE 
                    WHEN csiotc.status = "OPEN"
                        THEN NULL
                    WHEN csiotc.account_2_id IS NOT NULL
                        THEN csiotc.account_2_id
                    ELSE csia.account_2_id
                    END AS account_2_id,
               CASE WHEN csiotc.status = "OPEN"
                        THEN NULL
                    WHEN csiotc.account_2_id IS NOT NULL
                        THEN csiotc.role_2
                    ELSE csia.role_2
                    END AS role_2,
               coho.id AS organization_holiday_id,
               coho.name AS organization_holiday_name,
               CASE WHEN csiotc.spaces IS NOT NULL
                     THEN csiotc.spaces
                     ELSE csi.spaces
                     END AS spaces,
               CASE WHEN csiotc.walk_in_spaces IS NOT NULL
                     THEN csiotc.walk_in_spaces
                     ELSE csi.walk_in_spaces
                     END AS walk_in_spaces,
               csi.enrollment_spaces as enrollment_spaces,
               {attendance_count_sql}
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
                    otc.role,
                    otc.account_2_id,
                    otc.role_2,
                    otc.organization_location_room_id,
                    otc.organization_classtype_id,
                    otc.organization_level_id,
                    otc.time_start,
                    otc.time_end,
                    otc.spaces,
                    otc.walk_in_spaces,
                    otc_olr.organization_location_id,
                    otc_ol.name as organization_location_name
                  FROM costasiella_scheduleitemweeklyotc otc 
                  LEFT JOIN costasiella_organizationlocationroom otc_olr ON otc.organization_location_room_id = otc_olr.id
                  LEFT JOIN costasiella_organizationlocation otc_ol ON otc_olr.organization_location_id = otc_ol.id
                  WHERE date = %(class_date)s 
                ) csiotc
                ON csi.id = csiotc.schedule_item_id
            LEFT JOIN
                ( SELECT 
                    id,
                    schedule_item_id,
                    account_id,
                    role,
                    account_2_id,
                    role_2
                FROM costasiella_scheduleitemaccount
                WHERE date_start <= %(class_date)s AND 
                      (date_end >= %(class_date)s OR date_end IS NULL)
                ORDER BY date_start
                # LIMIT 1
                ) csia
                ON csia.schedule_item_id = csi.id
            LEFT JOIN
                ( SELECT coh.id, coh.name, cohl.organization_location_id
                  FROM costasiella_organizationholiday coh
                  LEFT JOIN
                    costasiella_organizationholidaylocation cohl
                    ON cohl.organization_holiday_id = coh.id
                  WHERE coh.date_start <= %(class_date)s AND
                        coh.date_end >= %(class_date)s) coho
                ON coho.organization_location_id = csi_ol.id
            WHERE csi.schedule_item_type = "CLASS" 
                AND (
                        /* Selection on specific days */
                        (csi.frequency_type = "SPECIFIC" AND csi.date_start = %(class_date)s ) OR
                        /* Weekly selection */
                        ( csi.frequency_type = "WEEKLY" AND 
                          csi.frequency_interval = %(iso_week_day)s AND 
                          csi.date_start <= %(class_date)s AND
                         (csi.date_end >= %(class_date)s OR csi.date_end IS NULL)
                        ) OR
                        /* Last weekday of month */
                        ( csi.frequency_type = "LAST_WEEKDAY_OF_MONTH" AND
                          csi.frequency_interval = %(iso_week_day)s AND 
                           DATE_FORMAT(
                            LAST_DAY(%(class_date)s) - ((7 + WEEKDAY(LAST_DAY(%(class_date)s)) - ( %(iso_week_day)s - 1)) %% 7), 
                            %(date_format)s) = %(class_date)s AND 
                          csi.date_start <= %(class_date)s AND
                          (csi.date_end >= %(class_date)s OR csi.date_end IS NULL)
                        )
                    )
                {where_sql}
            ORDER BY {order_by_sql}
        """.format(
            where_sql=_get_where_query(),
            attendance_count_sql=_get_count_attending_sql(),
            order_by_sql=order_by_sql
        )

        params = {
            "class_date": str(self.date),
            "iso_week_day": iso_week_day,
            "filter_id_account": self.filter_id_account,
            "filter_id_organization_classtype": self.filter_id_organization_classtype,
            "filter_id_organization_location": self.filter_id_organization_location,
            "filter_id_organization_level": self.filter_id_organization_level,
            "date_format": "%Y-%m-%d"
        }
        schedule_items = ScheduleItem.objects.raw(query, params=params)

        classes_list = []
        for item in schedule_items:
            holiday = False
            holiday_name = ""
            if item.organization_holiday_id:
                holiday = True
                holiday_name = item.organization_holiday_name

            total_spaces = item.spaces or 0
            walk_in_spaces = item.walk_in_spaces or 0
            enrollment_spaces = item.enrollment_spaces or 0
            count_attending = item.count_attending or 0
            count_booked = item.count_booked or 0
            count_attending_and_booked = item.count_attending_and_booked or 0
            count_enrolled = item.count_enrolled or 0
            available_online_spaces = calculate_available_spaces_online(
                total_spaces, walk_in_spaces, count_attending_and_booked
            )
            booking_open_on = self.resolve_booking_open_on()
            schedule_item_id = to_global_id('ScheduleItemNode', item.pk)

            classes_list.append(
                ScheduleClassType(
                    schedule_item_id=schedule_item_id,
                    date=self.date,
                    status=item.status,
                    holiday=holiday,
                    holiday_name=holiday_name,
                    description=item.description,
                    frequency_type=item.frequency_type,
                    account=item.account,
                    role=item.role,
                    account_2=item.account_2,
                    role_2=item.role_2,
                    organization_location_room=item.organization_location_room,
                    organization_classtype=item.organization_classtype,
                    organization_level=item.organization_level,
                    time_start=item.time_start,
                    time_end=item.time_end,
                    display_public=item.display_public,
                    spaces=total_spaces,
                    enrollment_spaces=enrollment_spaces,
                    count_attending=count_attending,
                    count_booked=count_booked,
                    count_attending_and_booked=count_attending_and_booked,
                    count_enrolled=count_enrolled,
                    available_spaces_online=available_online_spaces,
                    available_spaces_total=calculate_available_spaces_total(total_spaces, count_attending_and_booked),
                    booking_open_on=booking_open_on,
                    booking_status=get_booking_status(item, self.date, booking_open_on, available_online_spaces),
                    url_booking=get_url_booking(info, schedule_item_id, self.date)
                )
            )
    
        return classes_list


def get_url_booking(info, schedule_item_id, date):
    """
    Get URL pointing to shop booking
    :param schedule_item_id: global ID of class
    :param date: datetime.date object of class
    :return: String - booking url
    """
    try:
        scheme = info.context.scheme
        host = info.context.get_host()

        url_booking = "{scheme}://{host}/#/shop/classes/book/{schedule_item_id}/{date}".format(
            scheme=scheme,
            host=host,
            schedule_item_id=schedule_item_id,
            date=str(date)
        )
    except AttributeError:
        # Eg. When calling from another part piece of code instead of the API, info.context won't be available
        url_booking = ""

    return url_booking


def get_booking_status(schedule_item, date, booking_open_on, available_online_spaces):
    """
        :param schedule_item: schedule_item object
        :return: String: booking status
    """
    ## Start test for class booking status

    # https://docs.djangoproject.com/en/3.1/topics/i18n/timezones/#usage
    local_tz = pytz.timezone(settings.TIME_ZONE)
    now = timezone.localtime(timezone.now())
    dt_start = datetime.datetime(date.year,
                                 date.month,
                                 date.day,
                                 int(schedule_item.time_start.hour),
                                 int(schedule_item.time_start.minute))

    dt_start = local_tz.localize(dt_start)

    dt_end = datetime.datetime(date.year,
                               date.month,
                               date.day,
                               int(schedule_item.time_end.hour),
                               int(schedule_item.time_end.minute))

    dt_end = local_tz.localize(dt_end)

    status = "FINISHED"
    if schedule_item.organization_holiday_id:
        status = 'HOLIDAY'
    elif schedule_item.status == "CANCELLED":
        status = 'CANCELLED'
    elif dt_start <= now and dt_end >= now:
        # check start time
        status = 'ONGOING'
    elif dt_start >= now:
        if now.date() < booking_open_on:
            status = 'NOT_YET_OPEN'
        else:
            # check spaces for online bookings
            if available_online_spaces < 1:
                status = 'FULL'
            else:
                status = 'OK'

    return status

    # dt_end = datetime.datetime(self.date.year,
    #                            self.date.month,
    #                            self.date.day,
    #                            int(row.classes.Endtime.hour),
    #                            int(row.classes.Endtime.minute))
    # dt_end = local_tz.localize(dt_end)

    ## End test for class booking status

    # Everything below here in this fn is OpenStudio code to be ported
    # pytz = current.globalenv['pytz']
    # TIMEZONE = current.TIMEZONE
    # NOW_LOCAL = current.NOW_LOCAL
    # TODAY_LOCAL = current.TODAY_LOCAL
    #
    # local_tz = pytz.timezone(TIMEZONE)
    #
    # dt_start = datetime.datetime(self.date.year,
    #                              self.date.month,
    #                              self.date.day,
    #                              int(row.classes.Starttime.hour),
    #                              int(row.classes.Starttime.minute))
    # dt_start = local_tz.localize(dt_start)
    # dt_end = datetime.datetime(self.date.year,
    #                            self.date.month,
    #                            self.date.day,
    #                            int(row.classes.Endtime.hour),
    #                            int(row.classes.Endtime.minute))
    # dt_end = local_tz.localize(dt_end)
    #
    # status = 'finished'
    # if row.classes_otc.Status == 'cancelled' or row.school_holidays.id:
    #     status = 'cancelled'
    # elif dt_start <= NOW_LOCAL and dt_end >= NOW_LOCAL:
    #     # check start time
    #     status = 'ongoing'
    # elif dt_start >= NOW_LOCAL:
    #     if not self.bookings_open == False and TODAY_LOCAL < self.bookings_open:
    #         status = 'not_yet_open'
    #     else:
    #         # check spaces for online bookings
    #         spaces = self._get_day_list_booking_spaces(row)
    #         if spaces < 1:
    #             status = 'full'
    #         else:
    #             status = 'ok'
    #
    # return status


def calculate_booking_open_on(date):
    """
    Calculate when bookings for a class should open
    :param date: datetime.date
    :return: date
    """
    from ..dudes import SystemSettingDude

    system_setting_dude = SystemSettingDude()
    workflow_class_book_days_advance = system_setting_dude.get("workflow_class_book_days_advance")
    if not workflow_class_book_days_advance:
        # Set a default value of 30 days in advance to open class bookings
        workflow_class_book_days_advance = 30

    delta = datetime.timedelta(days=int(workflow_class_book_days_advance))

    return date - delta


def calculate_available_spaces_online(total_spaces, walk_in_spaces, count_attendance):
    # Spaces available for online booking
    online_spaces = total_spaces - walk_in_spaces

    # Subtract attendance
    available_spaces_online = online_spaces - count_attendance
    # Never return negatives, just 0
    if available_spaces_online < 1:
        available_spaces_online = 0

    return available_spaces_online


def calculate_available_spaces_total(total_spaces, count_attendance):
    available_spaces_total = total_spaces - count_attendance
    # Never return negatives, just 0
    if available_spaces_total < 1:
        available_spaces_total = 0

    return available_spaces_total


def validate_schedule_classes_query_date_input(date_from, 
                                               date_until, 
                                               order_by,
                                               instructor,
                                               organization_classtype,
                                               organization_level,
                                               organization_location
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

    if instructor:
        rid = get_rid(instructor)
        account_id = rid.id
        result['account_id'] = account_id

    if organization_classtype:
        rid = get_rid(organization_classtype)
        organization_classtype_id = rid.id
        result['organization_classtype_id'] = organization_classtype_id

    if organization_level:
        rid = get_rid(organization_level)
        organization_level_id = rid.id
        result['organization_level_id'] = organization_level_id

    if organization_location:
        rid = get_rid(organization_location)
        organization_location_id = rid.id
        result['organization_location_id'] = organization_location_id

    return result


class ScheduleClassQuery(graphene.ObjectType):
    schedule_class = graphene.Field(ScheduleClassType,
                                    schedule_item_id=graphene.ID(),
                                    date=graphene.types.datetime.Date())
    schedule_classes = graphene.List(
        ScheduleClassesDayType,
        date_from=graphene.types.datetime.Date(), 
        date_until=graphene.types.datetime.Date(),
        order_by=graphene.String(),
        instructor=graphene.ID(),
        organization_classtype=graphene.ID(),
        organization_level=graphene.ID(),
        organization_location=graphene.ID(),
        public_only=graphene.Boolean(),
    )

    def resolve_schedule_class(self,
                               info,
                               schedule_item_id,
                               date):
        """
        Resolve schedule class
        :param info:
        :param schedule_item_id:
        :param date:
        :return:
        """
        rid = get_rid(schedule_item_id)
        schedule_item = ScheduleItem.objects.get(pk=rid.id)
        if not schedule_item:
            raise Exception('Invalid Schedule Item ID!')

        count_attending = ScheduleItemAttendance.objects.filter(
            schedule_item=schedule_item,
            date=date,
            booking_status="ATTENDING"
        ).count()

        count_booked = ScheduleItemAttendance.objects.filter(
            schedule_item=schedule_item,
            date=date,
            booking_status="BOOKED"
        ).count()

        count_enrolled = ScheduleItemEnrollment.objects.filter(
            Q(schedule_item = schedule_item),
            Q(date_start__gte = date),
            (Q(date_end__lte = date) | Q(date_end__isnull = True)),
        ).count()

        sih = ScheduleItemHelper()
        schedule_item = sih.schedule_item_with_otc_and_holiday_data(schedule_item, date)

        booking_open_on = calculate_booking_open_on(date)

        total_spaces = schedule_item.spaces or 0
        walk_in_spaces = schedule_item.walk_in_spaces or 0
        enrollment_spaces = schedule_item.enrollment_spaces or 0
        count_attending_and_booked = count_attending + count_booked
        available_online_spaces = calculate_available_spaces_online(
            total_spaces, walk_in_spaces, count_attending_and_booked
        )

        schedule_class = ScheduleClassType(
            date=date,
            schedule_item_id=to_global_id('ScheduleItemNode', schedule_item.pk),
            display_public=schedule_item.display_public,
            frequency_type=schedule_item.frequency_type,
            status=schedule_item.status or "",
            description=schedule_item.description or "",
            account=schedule_item.account,
            role=schedule_item.role,
            account_2=schedule_item.account_2,
            organization_location_room=schedule_item.organization_location_room,
            organization_classtype=schedule_item.organization_classtype,
            organization_level=schedule_item.organization_level,
            time_start=schedule_item.time_start,
            time_end=schedule_item.time_end,
            info_mail_enabled=schedule_item.info_mail_enabled,
            info_mail_content=schedule_item.info_mail_content,
            spaces=total_spaces,
            enrollment_spaces=enrollment_spaces,
            count_attending=count_attending,
            count_booked=count_booked,
            count_attending_and_booked=count_attending_and_booked,
            count_enrolled=count_enrolled,
            available_spaces_online=available_online_spaces,
            available_spaces_total=calculate_available_spaces_total(total_spaces, count_attending_and_booked),
            booking_open_on=booking_open_on,
            booking_status=get_booking_status(schedule_item, date, booking_open_on, available_online_spaces)
        )

        return schedule_class

    def resolve_schedule_classes(self, 
                                 info, 
                                 date_from=graphene.types.datetime.Date(), 
                                 date_until=graphene.types.datetime.Date(),
                                 order_by=None,
                                 instructor=None,
                                 organization_classtype=None,
                                 organization_level=None,
                                 organization_location=None,
                                 public_only=True,
                                 ):
        user = info.context.user
        user_has_view_permission = check_if_user_has_permission(user, [
            'costasiella.view_scheduleclass',
            'costasiella.view_selfcheckin'
        ])

        validation_result = validate_schedule_classes_query_date_input(
            date_from, 
            date_until, 
            order_by,
            instructor,
            organization_classtype,
            organization_level,
            organization_location,
        )

        delta = datetime.timedelta(days=1)
        date = date_from
        return_list = []
        while date <= date_until:
            day = ScheduleClassesDayType()
            day.date = date

            if order_by:
                day.order_by = order_by

            if 'account_id' in validation_result:
                day.filter_id_account = \
                    validation_result['account_id']

            if 'organization_classtype_id' in validation_result:
                day.filter_id_organization_classtype = \
                    validation_result['organization_classtype_id']

            if 'organization_level_id' in validation_result:
                day.filter_id_organization_level = \
                    validation_result['organization_level_id']

            if 'organization_location_id' in validation_result:
                day.filter_id_organization_location = \
                    validation_result['organization_location_id']

            day.public_only = True
            if user_has_view_permission:
                day.public_only = public_only

            return_list.append(day)
            date += delta

        return return_list


def validate_schedule_class_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # If frequency type = LAST_WEEKDAY_OF_MONTH, should be checked that delta start & end date is at least 31 days.
    if 'frequency_type' in input:
        frequency_type = input['frequency_type']
        if frequency_type == 'LAST_WEEKDAY_OF_MONTH':
            if 'date_end' in input:
                date_end = input['date_end']
                if date_end is not None:
                    date_start = input['date_start']
                    delta = date_end - date_start
                    if delta.days < 31:
                        raise Exception(_('There should be at least 31 days between start and end dates!'))
        elif frequency_type == "WEEKLY":
            if 'date_end' in input:
                date_end = input['date_end']
                if date_end is not None:
                    date_start = input['date_start']
                    delta = date_end - date_start
                    if delta.days < 7:
                        raise Exception(_('There should be at least 7 days between start and end dates!'))

    # Check OrganizationLocationRoom
    if 'organization_location_room' in input:
        if input['organization_location_room']:
            rid = get_rid(input['organization_location_room'])
            organization_location_room = OrganizationLocationRoom.objects.filter(id=rid.id).first()
            result['organization_location_room'] = organization_location_room
            if not organization_location_room:
                raise Exception(_('Invalid Organization Location Room ID!'))            

    # Check OrganizationClasstype
    if 'organization_classtype' in input:
        if input['organization_classtype']:
            rid = get_rid(input['organization_classtype'])
            organization_classtype = OrganizationClasstype.objects.get(id=rid.id)
            result['organization_classtype'] = organization_classtype
            if not organization_classtype:
                raise Exception(_('Invalid Organization Classtype ID!'))            

    # Check OrganizationLevel
    if 'organization_level' in input:
        if input['organization_level']:
            rid = get_rid(input['organization_level'])
            organization_level = OrganizationLevel.objects.get(id=rid.id)
            result['organization_level'] = organization_level
            if not organization_level:
                raise Exception(_('Invalid Organization Level ID!'))            

    return result


class CreateScheduleClass(graphene.relay.ClientIDMutation):
    class Input:
        frequency_type = graphene.String(required=True)
        frequency_interval = graphene.Int(required=True)
        organization_location_room = graphene.ID(required=True)
        organization_classtype = graphene.ID(required=True)
        organization_level = graphene.ID(required=False, default_value=None)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        time_start = graphene.types.datetime.Time(required=True)
        time_end = graphene.types.datetime.Time(required=True)
        spaces = graphene.types.Int(required=True)
        walk_in_spaces = graphene.Int(required=True)
        enrollment_spaces = graphene.Int(required=False)
        display_public = graphene.Boolean(required=True, default_value=False)
        info_mail_enabled = graphene.Boolean(required=False)
        info_mail_content = graphene.String()

    schedule_item = graphene.Field(ScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleclass')

        result = validate_schedule_class_create_update_input(input)

        schedule_item = ScheduleItem(
            schedule_item_type="CLASS", 
            frequency_type=input['frequency_type'], 
            frequency_interval=input['frequency_interval'],
            date_start=input['date_start'],
            time_start=input['time_start'],
            time_end=input['time_end'],   
            display_public=input['display_public'],
            spaces=input['spaces'],
            walk_in_spaces=input['walk_in_spaces'],
        )

        # Optional fields
        if 'date_end' in input:
            schedule_item.date_end = input['date_end']

        if 'info_mail_content' in input:
            schedule_item.info_mail_content = input['info_mail_content']

        if 'info_mail_enabled' in input:
            schedule_item.info_mail_enabled = input['info_mail_enabled']

        if 'enrollment_spaces' in input:
            schedule_item.enrollment_spaces = input['enrollment_spaces']

        # Fields requiring additional validation
        if result['organization_location_room']:
            schedule_item.organization_location_room = result['organization_location_room']

        if result['organization_classtype']:
            schedule_item.organization_classtype = result['organization_classtype']

        if 'organization_level' in result:
            schedule_item.organization_level = result['organization_level']

        # ALl done, save it :).
        schedule_item.save()

        helper = ScheduleItemHelper()
        helper.add_all_subscription_groups(schedule_item.id)
        helper.add_all_classpass_groups(schedule_item.id)

        return CreateScheduleClass(schedule_item=schedule_item)


class UpdateScheduleClass(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        frequency_type = graphene.String(required=False)
        frequency_interval = graphene.Int(required=False)
        organization_location_room = graphene.ID(required=False)
        organization_classtype = graphene.ID(required=False)
        organization_level = graphene.ID(required=False)
        date_start = graphene.types.datetime.Date(required=False)
        date_end = graphene.types.datetime.Date(required=False)
        time_start = graphene.types.datetime.Time(required=False)
        time_end = graphene.types.datetime.Time(required=False)
        spaces = graphene.types.Int(required=False)
        walk_in_spaces = graphene.Int(required=False)
        enrollment_spaces = graphene.Int(required=False)
        display_public = graphene.Boolean(required=False)
        info_mail_enabled = graphene.Boolean(required=False)
        info_mail_content = graphene.String(default_value="")

    schedule_item = graphene.Field(ScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleclass')

        result = validate_schedule_class_create_update_input(input)
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

        if 'display_public' in input:
            schedule_item.display_public = input['display_public']

        if 'spaces' in input:
            schedule_item.spaces = input['spaces']

        if 'walk_in_spaces' in input:
            schedule_item.walk_in_spaces = input['walk_in_spaces']

        if 'enrollment_spaces' in input:
            schedule_item.enrollment_spaces = input['enrollment_spaces']

        if 'info_mail_enabled' in input:
            schedule_item.info_mail_enabled = input['info_mail_enabled']

        if 'info_mail_content' in input:
            schedule_item.info_mail_content = input['info_mail_content']

        # Fields requiring additional validation
        if result['organization_location_room']:
            schedule_item.organization_location_room = result['organization_location_room']

        if result['organization_classtype']:
            schedule_item.organization_classtype = result['organization_classtype']

        if 'organization_level' in result:
            schedule_item.organization_level = result['organization_level']

        # ALl done, save it :).
        schedule_item.save()

        return UpdateScheduleClass(schedule_item=schedule_item)


class DeleteScheduleClass(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleclass')

        rid = get_rid(input['id'])
        schedule_item = ScheduleItem.objects.filter(id=rid.id).first()
        if not schedule_item:
            raise Exception('Invalid Schedule Item ID!')

        ok = bool(schedule_item.delete())

        return DeleteScheduleClass(ok=ok)


class ScheduleClassMutation(graphene.ObjectType):
    create_schedule_class = CreateScheduleClass.Field()
    update_schedule_class = UpdateScheduleClass.Field()
    delete_schedule_class = DeleteScheduleClass.Field()
