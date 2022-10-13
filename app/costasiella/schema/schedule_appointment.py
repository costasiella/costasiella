from django.utils.translation import gettext as _
from django.db.models import Q

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import ScheduleItem, OrganizationAppointment, OrganizationLocationRoom
from ..modules.gql_tools import require_login_and_permission, require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages
from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper
from .organization_appointment import OrganizationAppointmentNode
from .organization_location_room import OrganizationLocationRoomNode
from .schedule_item import ScheduleItemNode


m = Messages()

import datetime


# ScheduleAppointmentType
class ScheduleAppointmentType(graphene.ObjectType):
    schedule_item_id = graphene.ID()
    frequency_type = graphene.String()
    date = graphene.types.datetime.Date()
    organization_location_room = graphene.Field(OrganizationLocationRoomNode)
    organization_appointment = graphene.Field(OrganizationAppointmentNode)
    time_start = graphene.types.datetime.Time()
    time_end = graphene.types.datetime.Time()
    display_public = graphene.Boolean()


# ScheduleAppointmentDayType
class ScheduleAppointmentsDayType(graphene.ObjectType):
    date = graphene.types.datetime.Date()
    iso_week_day = graphene.Int()
    order_by = graphene.String()
    filter_id_organization_location = graphene.String()
    appointments = graphene.List(ScheduleAppointmentType)

    def resolve_iso_week_day(self, info):
        return self.date.isoweekday()

    def resolve_order_by(self, info):       
        return self.order_by

    def resolve_appointments(self, info):
        iso_week_day = self.resolve_iso_week_day(info)
        sorting = self.order_by
        if not sorting: # Default to sort by location, then time
            sorting = "location"

        schedule_filter = Q(schedule_item_type = 'APPOINTMENT') & \
            (
                # Appointmentes on this day (Specific)
                (
                    Q(frequency_type = 'SPECIFIC') & \
                    Q(date_start = self.date)
                ) | # OR
                # Weekly appointments
                ( 
                    Q(frequency_type = 'WEEKLY') &
                    Q(frequency_interval = iso_week_day) &
                    Q(date_start__lte = self.date) & 
                    (Q(date_end__gte = self.date) | Q(date_end__isnull = True ))
                )
            )
        
        # Filter locations
        if self.filter_id_organization_location:
            schedule_filter &= \
                Q(organization_location_room__organization_location__id = self.filter_id_organization_location)
            
        ## Query appointments table for self.date
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

        appointments_list = []
        for item in schedule_items:
            appointments_list.append(
                ScheduleAppointmentType(
                    schedule_item_id=to_global_id('ScheduleItemNode', item.pk),
                    date=self.date,
                    frequency_type=item.frequency_type,
                    organization_location_room=item.organization_location_room,
                    time_start=item.time_start,
                    time_end=item.time_end,
                    display_public=item.display_public
                )
            )
    
        return appointments_list


def validate_schedule_appointments_query_date_input(date_from, 
                                               date_until, 
                                               order_by, 
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

    if organization_location:
        rid = get_rid(organization_location)
        organization_location_id = rid.id
        result['organization_location_id'] = organization_location_id

    return result


class ScheduleAppointmentQuery(graphene.ObjectType):
    schedule_appointments = graphene.List(
        ScheduleAppointmentsDayType,
        date_from=graphene.types.datetime.Date(), 
        date_until=graphene.types.datetime.Date(),
        order_by=graphene.String(),
        organization_location=graphene.String(),
        
    )

    def resolve_schedule_appointments(self, 
                                 info, 
                                 date_from=graphene.types.datetime.Date(), 
                                 date_until=graphene.types.datetime.Date(),
                                 order_by=None,
                                 organization_location=None,
                                 ):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleappointment')

        validation_result = validate_schedule_appointments_query_date_input(
            date_from, 
            date_until, 
            order_by,
            organization_location,
        )

        delta = datetime.timedelta(days=1)
        date = date_from
        return_list = []
        while date <= date_until:
            day = ScheduleAppointmentsDayType()
            day.date = date

            if order_by:
                day.order_by = order_by

            if 'organization_location_id' in validation_result:
                day.filter_id_organization_location = \
                    validation_result['organization_location_id']

            return_list.append(day)
            date += delta

        return return_list


def validate_schedule_appointment_create_update_input(input, update=False):
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

    return result


class CreateScheduleAppointment(graphene.relay.ClientIDMutation):
    class Input:
        frequency_type = graphene.String(required=True)
        frequency_interval = graphene.Int(required=True)
        organization_location_room = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        time_start = graphene.types.datetime.Time(required=True)
        time_end = graphene.types.datetime.Time(required=True)
        display_public = graphene.Boolean(required=True, default_value=False)

    schedule_item = graphene.Field(ScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleappointment')

        result = validate_schedule_appointment_create_update_input(input)

        schedule_item = ScheduleItem(
            schedule_item_type="APPOINTMENT", 
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

        # ALl done, save it :).
        schedule_item.save()

        return CreateScheduleAppointment(schedule_item=schedule_item)


class UpdateScheduleAppointment(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        frequency_type = graphene.String(required=True)
        frequency_interval = graphene.Int(required=True)
        organization_location_room = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        time_start = graphene.types.datetime.Time(required=True)
        time_end = graphene.types.datetime.Time(required=True)
        display_public = graphene.Boolean(required=True, default_value=False)

    schedule_item = graphene.Field(ScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleappointment')

        result = validate_schedule_appointment_create_update_input(input)
        rid = get_rid(input['id'])

        schedule_item = ScheduleItem.objects.get(pk=rid.id)
        if not schedule_item:
            raise Exception('Invalid Schedule Item ID!')

        if schedule_item.frequency_type == "WEEKLY" and input['frequency_type'] == 'SPECIFIC':
            raise Exception('Unable to change weekly appointment into one time appointment')

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

        # ALl done, save it :).
        schedule_item.save()

        return UpdateScheduleAppointment(schedule_item=schedule_item)


class DeleteScheduleAppointment(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleappointment')

        rid = get_rid(input['id'])
        schedule_item = ScheduleItem.objects.filter(id=rid.id).first()
        if not schedule_item:
            raise Exception('Invalid Schedule Item ID!')

        ok = bool(schedule_item.delete())

        return DeleteScheduleAppointment(ok=ok)


class ScheduleAppointmentMutation(graphene.ObjectType):
    create_schedule_appointment = CreateScheduleAppointment.Field()
    update_schedule_appointment = UpdateScheduleAppointment.Field()
    delete_schedule_appointment = DeleteScheduleAppointment.Field()