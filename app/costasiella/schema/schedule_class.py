from django.utils.translation import gettext as _
from django.db.models import Q, FilteredRelation, OuterRef, Subquery

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import ScheduleItem, ScheduleItemWeeklyOTC, OrganizationClasstype, OrganizationLevel, OrganizationLocationRoom
from ..modules.gql_tools import require_login_and_permission, require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages
from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper
from .account import AccountNode
from .organization_classtype import OrganizationClasstypeNode
from .organization_level import OrganizationLevelNode
from .organization_location_room import OrganizationLocationRoomNode
from .schedule_item import ScheduleItemNode


m = Messages()

import datetime


def _get_resolve_classes_filter_query(self):
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
    if self.filter_id_organization_classtype:
        where += 'AND (CASE WHEN csiotc.organization_classtype_id IS NULL \
                        THEN csi.organization_classtype_id  \
                        ELSE csiotc.organization_classtype_id END) = '
        where += str(self.filter_id_organization_classtype) + ' '
    if self.filter_id_organization_location_room:
        where += 'AND (CASE WHEN csiotc.organization_location_room_id IS NULL \
                        THEN csi.organization_location_room_id  \
                        ELSE csiotc.organization_location_room_id END) = '
        where += str(self.filter_id_organization_location_room) + ' '
    if self.filter_id_organization_level:
        where += 'AND (CASE WHEN csiotc.organization_level_id IS NULL \
                        THEN csi.organization_level_id  \
                        ELSE csiotc.organization_level_id END) = '
        where += str(self.filter_id_organization_level) + ' '
    if self.filter_public:
        where += "AND csi.display_public = 1 "
        # where += "AND sl.AllowAPI = 'T' "
        # where += "AND sct.AllowAPI = 'T' "
    # if self.filter_starttime_from:
    #     where += 'AND ((CASE WHEN cotc.Starttime IS NULL \
    #                     THEN cla.Starttime  \
    #                     ELSE cotc.Starttime END) >= '
    #     where += "'" + str(self.filter_starttime_from) + "') "

    return where


# ScheduleClassType
class ScheduleClassType(graphene.ObjectType):
    schedule_item_id = graphene.ID()
    frequency_type = graphene.String()
    date = graphene.types.datetime.Date()
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


# ScheduleClassDayType
class ScheduleClassesDayType(graphene.ObjectType):
    date = graphene.types.datetime.Date()
    iso_week_day = graphene.Int()
    order_by = graphene.String()
    filter_id_organization_classtype = graphene.String()
    filter_id_organization_level = graphene.String()
    filter_id_organization_location = graphene.String()
    classes = graphene.List(ScheduleClassType)

    def resolve_iso_week_day(self, info):
        return self.date.isoweekday()

    def resolve_order_by(self, info):       
        return self.order_by

    def resolve_classes(self, info):
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
            if self.filter_id_organization_classtype:
                where += 'AND (CASE WHEN csiotc.organization_classtype_id IS NULL \
                                THEN csi.organization_classtype_id  \
                                ELSE csiotc.organization_classtype_id END) = '
                where += str(self.filter_id_organization_classtype) + ' '
            if self.filter_id_organization_location:
                where += 'AND (CASE WHEN csiotc.organization_location_id IS NULL \
                                THEN csi_olr.organization_location_id  \
                                ELSE csiotc.organization_location_id END) = '
                where += str(self.filter_id_organization_location) + ' '
            if self.filter_id_organization_level:
                where += 'AND (CASE WHEN csiotc.organization_level_id IS NULL \
                                THEN csi.organization_level_id  \
                                ELSE csiotc.organization_level_id END) = '
                where += str(self.filter_id_organization_level) + ' '
            # if self.filter_public:
            #     where += "AND csi.display_public = 1 "
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
        if not sorting: # Default to sort by location, then time
            sorting = "location"

        # # Set sorting
        # if sorting == "location":
        #     # Location | Location room | Start time
        #     schedule_items = schedule_items.order_by(
        #         'organization_location_room__organization_location__name',
        #         'organization_location_room__name',
        #         'time_start'
        #     )
        # else:
        #     # Start time | Location | Location room
        #     schedule_items = schedule_items.order_by(
        #         'time_start',
        #         'organization_location_room__organization_location__name',
        #         'organization_location_room__name',
        #     )

        if sorting == 'location':
            order_by_sql = 'organization_location_name, time_start'
        else: # sorting == 'starttime'
            order_by_sql = 'time_start, organization_location_name'

        query = """
            SELECT 
                csi.id,
                csi.frequency_type,
                CASE
                    WHEN csiotc.status = "CANCELLED" 
                        THEN csiotc.status
                    WHEN csiotc.status = "OPEN" 
                        THEN csiotc.status
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
                    ELSE csit.account_id
                    END AS account_id,
               CASE 
                    WHEN csiotc.status = "OPEN"
                        THEN NULL
                    WHEN csiotc.account_id IS NOT NULL
                        THEN csiotc.role
                    ELSE csit.role
                    END AS role,
               CASE 
                    WHEN csiotc.status = "OPEN"
                        THEN NULL
                    WHEN csiotc.account_2_id IS NOT NULL
                        THEN csiotc.account_2_id
                    ELSE csit.account_2_id
                    END AS account_2_id,
               CASE WHEN csiotc.status = "OPEN"
                        THEN NULL
                    WHEN csiotc.account_2_id IS NOT NULL
                        THEN csiotc.role_2
                    ELSE csit.role_2
                    END AS role_2
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
                    otc_olr.organization_location_id,
                    otc_ol.name as organization_location_name
                  FROM costasiella_scheduleitemweeklyotc otc 
                  LEFT JOIN costasiella_organizationlocationroom otc_olr ON otc.organization_location_room_id = otc_olr.id
                  LEFT JOIN costasiella_organizationlocation otc_ol ON otc_olr.organization_location_id = otc_ol.id
                  WHERE date = "{class_date}" 
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
                FROM costasiella_scheduleitemteacher
                WHERE date_start <= "{class_date}" AND (
                      date_end >= "{class_date}" OR date_end IS NULL)
                LIMIT 1
                ) csit
                ON csit.schedule_item_id = csi.id
            WHERE csi.schedule_item_type = "CLASS" 
                AND (
                        (csi.frequency_type = "SPECIFIC" AND csi.date_start = "{class_date}" ) OR
                        ( csi.frequency_type = "WEEKLY" AND 
                          csi.frequency_interval = {iso_week_day} AND 
                          csi.date_start <= "{class_date}" AND
                         (csi.date_end >= "{class_date}" OR csi.date_end IS NULL)
                        ) 
                    )
                {where_sql}
            ORDER BY {order_by_sql}
        """.format(
            class_date = self.date,
            iso_week_day = iso_week_day,
            where_sql = _get_where_query(),
            order_by_sql = order_by_sql
        )

        # print(query)

        ## 
        # At this time 27 Aug 2019, params don't seem to be working from a dictionary
        # https://docs.djangoproject.com/en/2.2/topics/db/sql/
        # the query should be formatted using "%(class_date)s" 
        ##
        # params = {
        #     "class_date": self.date, 
        #     "iso_week_day": iso_week_day
        # }

        schedule_items = ScheduleItem.objects.raw(query)
        # print(schedule_items.query)

        # # Set sorting
        # if sorting == "location":
        #     # Location | Location room | Start time
        #     schedule_items = schedule_items.order_by(
        #         'organization_location_room__organization_location__name',
        #         'organization_location_room__name',
        #         'time_start'
        #     )
        # else:
        #     # Start time | Location | Location room
        #     schedule_items = schedule_items.order_by(
        #         'time_start',
        #         'organization_location_room__organization_location__name',
        #         'organization_location_room__name',
        #     )

        classes_list = []
        for item in schedule_items:

            print("#############")
            print(item)
            print(item.status)
            print(item.description)
            print(item.account)
            print(item.account_id)
            print(item.role)

            classes_list.append(
                ScheduleClassType(
                    schedule_item_id=to_global_id('ScheduleItemNode', item.pk),
                    date=self.date,
                    status=item.status,
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
                    display_public=item.display_public
                )
            )
    
        return classes_list


def validate_schedule_classes_query_date_input(date_from, 
                                               date_until, 
                                               order_by, 
                                               organization_classtype,
                                               organization_level,
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


    print("###########")
    print(organization_location)

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
    schedule_classes = graphene.List(
        ScheduleClassesDayType,
        date_from=graphene.types.datetime.Date(), 
        date_until=graphene.types.datetime.Date(),
        order_by=graphene.String(),
        organization_classtype=graphene.String(),
        organization_level=graphene.String(),
        organization_location=graphene.String(),   
    )

    def resolve_schedule_items(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitem')

        ## return everything:
        return ScheduleItem.objects.filter()


    def resolve_schedule_classes(self, 
                                 info, 
                                 date_from=graphene.types.datetime.Date(), 
                                 date_until=graphene.types.datetime.Date(),
                                 order_by=None,
                                 organization_classtype=None,
                                 organization_level=None,
                                 organization_location=None,
                                 ):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleclass')

        print('############ resolve')
        print(locals())
        print(organization_location)

        validation_result = validate_schedule_classes_query_date_input(
            date_from, 
            date_until, 
            order_by,
            organization_classtype,
            organization_level,
            organization_location,
        )


        print(validation_result)

        delta = datetime.timedelta(days=1)
        date = date_from
        return_list = []
        while date <= date_until:
            day = ScheduleClassesDayType()
            day.date = date

            if order_by:
                day.order_by = order_by

            if 'organization_classtype_id' in validation_result:
                day.filter_id_organization_classtype = \
                    validation_result['organization_classtype_id']

            if 'organization_level_id' in validation_result:
                day.filter_id_organization_level = \
                    validation_result['organization_level_id']

            if 'organization_location_id' in validation_result:
                day.filter_id_organization_location = \
                    validation_result['organization_location_id']

            return_list.append(day)
            date += delta

        return return_list


def validate_schedule_class_create_update_input(input, update=False):
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
            print('processing')
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
        display_public = graphene.Boolean(required=True, default_value=False)

    schedule_item = graphene.Field(ScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleclass')

        print(input)

        result = validate_schedule_class_create_update_input(input)

        schedule_item = ScheduleItem(
            schedule_item_type="CLASS", 
            frequency_type=input['frequency_type'], 
            frequency_interval=input['frequency_interval'],
            date_start=input['date_start'],
            time_start=input['time_start'],
            time_end=input['time_end'],   
            display_public=input['display_public']
        )

        # Optional fields
        date_end = input.get('date_end', None)
        if date_end:
            schedule_item.date_end = date_end

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
        frequency_type = graphene.String(required=True)
        frequency_interval = graphene.Int(required=True)
        organization_location_room = graphene.ID(required=True)
        organization_classtype = graphene.ID(required=True)
        organization_level = graphene.ID(required=False, default_value=None)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        time_start = graphene.types.datetime.Time(required=True)
        time_end = graphene.types.datetime.Time(required=True)
        display_public = graphene.Boolean(required=True, default_value=False)

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

        schedule_item.frequency_type = input['frequency_type']
        schedule_item.frequency_interval=input['frequency_interval']
        schedule_item.date_start=input['date_start']
        schedule_item.time_start=input['time_start']
        schedule_item.time_end=input['time_end']
        schedule_item.display_public=input['display_public']


        # Optional fields
        date_end = input.get('date_end', None)
        if date_end:
            schedule_item.date_end = date_end

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

        ok = schedule_item.delete()

        return DeleteScheduleClass(ok=ok)


class ScheduleClassMutation(graphene.ObjectType):
    create_schedule_class = CreateScheduleClass.Field()
    update_schedule_class = UpdateScheduleClass.Field()
    delete_schedule_class = DeleteScheduleClass.Field()