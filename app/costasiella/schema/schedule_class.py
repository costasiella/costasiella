from django.utils.translation import gettext as _
from django.db.models import Q

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import ScheduleItem, OrganizationClasstype, OrganizationLevel, OrganizationLocationRoom
from ..modules.gql_tools import require_login_and_permission, require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages
from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper
from .organization_classtype import OrganizationClasstypeNode
from .organization_level import OrganizationLevelNode
from .organization_location_room import OrganizationLocationRoomNode
from .schedule_item import ScheduleItemNode


m = Messages()

import datetime


# ScheduleClassType
class ScheduleClassType(graphene.ObjectType):
    schedule_item_id = graphene.ID()
    frequency_type = graphene.String()
    date = graphene.types.datetime.Date()
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
    filter_id_organization_classtype= graphene.String()
    filter_id_organization_level= graphene.String()
    filter_id_organization_location= graphene.String()
    classes = graphene.List(ScheduleClassType)

    def resolve_iso_week_day(self, info):
        return self.date.isoweekday()

    def resolve_order_by(self, info):       
        return self.order_by

    def resolve_classes(self, info):
        iso_week_day = self.resolve_iso_week_day(info)
        sorting = self.order_by
        if not sorting: # Default to sort by location, then time
            sorting = "location"

        ##
        # Use Filtered relations to link one time changes
        # https://docs.djangoproject.com/en/2.2/ref/models/querysets/#filteredrelation-objects
        ##

        schedule_filter = Q(schedule_item_type = 'CLASS') & \
            (
                # Classes on this day (Specific)
                (
                    Q(frequency_type = 'SPECIFIC') & \
                    Q(date_start = self.date)
                ) | # OR
                # Weekly classes
                ( 
                    Q(frequency_type = 'WEEKLY') &
                    Q(frequency_interval = iso_week_day) &
                    Q(date_start__lte = self.date) & 
                    (Q(date_end__gte = self.date) | Q(date_end__isnull = True ))
                )
            )
        
        # Filter classtypes
        if self.filter_id_organization_classtype:
            schedule_filter &= \
                Q(organization_classtype__id = self.filter_id_organization_classtype)
        
        # Filter level
        if self.filter_id_organization_level:
            schedule_filter &= \
                Q(organization_level__id = self.filter_id_organization_level)
        
        # Filter locations
        if self.filter_id_organization_location:
            schedule_filter &= \
                Q(organization_location_room__organization_location__id = self.filter_id_organization_location)
            
        ## Query classes table for self.date
        schedule_items = ScheduleItem.objects.select_related('organization_location_room__organization_location').filter(
            schedule_filter
        )

        # Set sorting
        if sorting == "location":
            # Location | Location room | Start time
            schedule_items = schedule_items.order_by(
                'organization_location_room__organization_location__name',
                'organization_location_room__name',
                'time_start'
            )
        else:
            # Start time | Location | Location room
            schedule_items = schedule_items.order_by(
                'time_start',
                'organization_location_room__organization_location__name',
                'organization_location_room__name',
            )

        classes_list = []
        for item in schedule_items:
            classes_list.append(
                ScheduleClassType(
                    schedule_item_id=to_global_id('ScheduleItemNode', item.pk),
                    date=self.date,
                    frequency_type=item.frequency_type,
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