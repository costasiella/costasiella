from django.utils.translation import gettext as _
from django.db.models import Count, Q

import datetime
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import \
    Account, \
    ScheduleEvent, \
    ScheduleItem, \
    ScheduleItemAttendance, \
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


m = Messages()


class ScheduleItemNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    count_booked = graphene.Int()
    count_attending = graphene.Int()
    count_attending_and_booked = graphene.Int()


class ScheduleItemNode(DjangoObjectType):
    # Disable output like "A_3" by graphene automatically converting model choices
    # to an Enum field
    frequency_interval = graphene.Field(graphene.Int, source='frequency_interval')

    class Meta:
        model = ScheduleItem
        fields = (
            # model fields
            'schedule_event',
            'schedule_item_type',
            'frequency_type',
            'frequency_interval',
            'organization_location_room',
            'organization_classtype',
            'organization_level',
            'organization_shift',
            'name',
            'spaces',
            'walk_in_spaces',
            'enrollment_spaces',
            'date_start',
            'date_end',
            'time_start',
            'time_end',
            'display_public',
            'organization_classpass_groups',
            'organization_subscription_groups',
            'info_mail_enabled',
            'info_mail_content',
            'account',
            'account_2',
            'created_at',
            'updated_at',
            # reverse relations
            'attendances',
            'enrollments'
        )
        filter_fields = ['schedule_item_type', 'schedule_event']
        interfaces = (graphene.relay.Node, ScheduleItemNodeInterface)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user

        schedule_item = self._meta.model.objects.get(id=id)
        if schedule_item.display_public or info.path.typename == "ScheduleItemAttendanceNode":
            return schedule_item
        else:
            permissions = [
                'costasiella.view_scheduleitem',
                'costasiella.view_scheduleclass',
                'costasiella.view_scheduleevent',
                'costasiella.view_scheduleshift',
            ]
            require_login_and_one_of_permissions(user, permissions)
            return schedule_item

    def resolve_count_attending(self, info):
        count_attendance = ScheduleItemAttendance.objects.filter(
            Q(schedule_item_id=self.id) & Q(booking_status="ATTENDING")
        ).count()

        return count_attendance

    def resolve_count_booked(self, info):
        count_attendance = ScheduleItemAttendance.objects.filter(
            Q(schedule_item_id=self.id) & Q(booking_status="BOOKED")
        ).count()

        return count_attendance

    def resolve_count_attending_and_booked(self, info):
        count_attendance = ScheduleItemAttendance.objects.filter(
            Q(schedule_item_id=self.id) & ~Q(booking_status="CANCELLED")
        ).count()

        return count_attendance

    def resolve_attendances(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemattendance')

    def resolve_enrollments(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemenrollment')


class ScheduleItemQuery(graphene.ObjectType):
    schedule_items = DjangoFilterConnectionField(ScheduleItemNode)
    schedule_item = graphene.relay.Node.Field(ScheduleItemNode)

    def resolve_schedule_items(self, info, **kwargs):
        user = info.context.user

        if user:
            permissions = [
                'costasiella.view_scheduleitem',
                'costasiella.view_scheduleclass',
                'costasiella.view_scheduleevent',
                'costasiella.view_scheduleshift',
            ]
            permission = check_if_user_has_permission(user, permissions)
            if permission:
                return ScheduleItem.objects.filter().order_by('date_start', 'time_start')

        ## return everything:
        return ScheduleItem.objects.filter(display_public=True).order_by('date_start', 'time_start')


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Check ScheduleEvent
    if 'schedule_event' in input:
        if input['schedule_event']:
            rid = get_rid(input['schedule_event'])
            schedule_event = ScheduleEvent.objects.filter(id=rid.id).first()
            result['schedule_event'] = schedule_event
            if not schedule_event:
                raise Exception(_('Invalid Schedule Event ID!'))

            # Do some basic checks for schedule event activity input
            # account and account_2 fields are allowed to be empty
            if schedule_event:
                if 'name' not in input or input['name'] is None or input['name'] == "":
                    raise Exception(_('name should be set for event activities!'))

                if 'spaces' not in input or input['spaces'] is None or input['spaces'] == "":
                    raise Exception(_('spaces should be set for event activities!'))

                if not update:
                    if 'schedule_item_type' not in input or input['schedule_item_type'] != "EVENT_ACTIVITY":
                        raise Exception(_('scheduleEventType should be set to "EVENT_ACTIVITY" for event activities!'))

                    if 'frequency_type' not in input or input['frequency_type'] != "SPECIFIC":
                        raise Exception(_('frequencyType should be set to "SPECIFIC" for event activities!'))

                    if 'frequency_interval' not in input or input['frequency_interval'] != 0:
                        raise Exception(_('frequencyInterval should be set to 0 for event activities!'))

    # Check account
    if 'account' in input:
        if input['account']:
            rid = get_rid(input['account'])
            account = Account.objects.filter(id=rid.id).first()
            result['account'] = account
            if not account:
                raise Exception(_('Invalid Account ID!'))

    # Check account
    if 'account_2' in input:
        if input['account_2']:
            rid = get_rid(input['account_2'])
            account_2 = Account.objects.filter(id=rid.id).first()
            result['account_2'] = account_2
            if not account_2:
                raise Exception(_('Invalid Account ID (account2)!'))

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

    return result


class CreateScheduleItem(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=False)
        account_2 = graphene.ID(required=False)
        display_public = graphene.Boolean(required=False)
        name = graphene.String(required=False)
        spaces = graphene.Int(required=False)
        schedule_event = graphene.ID(required=False)
        schedule_item_type = graphene.String(required=True)
        frequency_type = graphene.String(required=True)
        frequency_interval = graphene.Int(required=True)
        organization_location_room = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        time_start = graphene.types.datetime.Time(required=True)
        time_end = graphene.types.datetime.Time(required=True)

    schedule_item = graphene.Field(ScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleitem')

        result = validate_create_update_input(input)

        schedule_item = ScheduleItem(
            organization_location_room=result['organization_location_room'],
            schedule_item_type=input['schedule_item_type'], 
            frequency_type=input['frequency_type'], 
            frequency_interval=input['frequency_interval'],
            date_start=input['date_start'],
            time_start=input['time_start'],
            time_end=input['time_end'],   
        )

        # Optional fields
        if "display_public" in input:
            schedule_item.display_public = input['display_public']

        if "account" in result:
            schedule_item.account = result['account']

        if "account_2" in result:
            schedule_item.account_2 = result['account_2']

        if "schedule_event" in result:
            schedule_item.schedule_event = result['schedule_event']

        if "name" in input:
            schedule_item.name = input['name']

        if "spaces" in input:
            schedule_item.spaces = input['spaces']

        if "date_end" in input:
            schedule_item.date_end = input['date_end']

        # ALl done, save it :).
        schedule_item.save()

        if schedule_item.schedule_item_type == "EVENT_ACTIVITY":
            sih = ScheduleItemHelper()
            # Add Schedule item to all tickets
            sih.add_schedule_item_to_all_event_tickets(schedule_item)
            # Add attendance records (eg. full event ticket customers should always be added).
            sih.create_attendance_records_for_event_schedule_items(schedule_item.schedule_event)

            # update event dates & times
            schedule_item.schedule_event.update_dates_and_times()

        return CreateScheduleItem(schedule_item=schedule_item)


class UpdateScheduleItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        account = graphene.ID(required=False)
        account_2 = graphene.ID(required=False)
        display_public = graphene.Boolean(required=False)
        name = graphene.String(required=False)
        spaces = graphene.Int(required=False)
        organization_location_room = graphene.ID(required=False)
        date_start = graphene.types.datetime.Date(required=False)
        date_end = graphene.types.datetime.Date(required=False)
        time_start = graphene.types.datetime.Time(required=False)
        time_end = graphene.types.datetime.Time(required=False)
        
    schedule_item = graphene.Field(ScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleitem')

        rid = get_rid(input['id'])
        schedule_item = ScheduleItem.objects.filter(id=rid.id).first()
        if not schedule_item:
            raise Exception('Invalid Schedule Item ID!')

        result = validate_create_update_input(input, update=True)

        if "name" in input:
            schedule_item.name = input['name']

        if "account" in result:
            schedule_item.account = result['account']

        if "account_2" in result:
            schedule_item.account_2 = result['account_2']

        if "display_public" in result:
            schedule_item.display_public = result['display_public']

        if "organization_location_room" in result:
            schedule_item.organization_location_room = result['organization_location_room']

        if "spaces" in input:
            schedule_item.spaces = input['spaces']

        if "date_start" in input:
            schedule_item.date_start = input['date_start']

        if "date_end" in input:
            schedule_item.date_end = input['date_end']

        if "time_start" in input:
            schedule_item.time_start = input['time_start']

        if "time_end" in input:
            schedule_item.time_end = input['time_end']

        schedule_item.save()

        if schedule_item.schedule_event:
            # update event dates & times
            schedule_item.schedule_event.update_dates_and_times()

        return UpdateScheduleItem(schedule_item=schedule_item)


class DeleteScheduleItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleitem')

        rid = get_rid(input['id'])
        schedule_item = ScheduleItem.objects.filter(id=rid.id).first()
        if not schedule_item:
            raise Exception('Invalid Schedule Item ID!')

        ok = bool(schedule_item.delete())

        return DeleteScheduleItem(ok=ok)


class ScheduleItemMutation(graphene.ObjectType):
    create_schedule_item = CreateScheduleItem.Field()
    update_schedule_item = UpdateScheduleItem.Field()
    delete_schedule_item = DeleteScheduleItem.Field()
