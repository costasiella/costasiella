from django.utils.translation import gettext as _
from django.db.models import Q

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import \
    Account, \
    ScheduleEvent, \
    ScheduleItem, \
    OrganizationClasstype, \
    OrganizationLevel, \
    OrganizationLocationRoom
from ..modules.gql_tools import require_login_and_permission, require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages
from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper


m = Messages()

import datetime


class ScheduleItemNode(DjangoObjectType):
    # Disable output like "A_3" by graphene automatically converting model choices
    # to an Enum field
    frequency_interval = graphene.Field(graphene.Int, source='frequency_interval')

    class Meta:
        model = ScheduleItem
        filter_fields = ['schedule_item_type', 'schedule_event']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        permissions = [
            'costasiella.view_scheduleitem',
            'costasiella.view_scheduleclass',
            'costasiella.view_scheduleevent',
        ]
        require_login_and_one_of_permissions(user, permissions)

        return self._meta.model.objects.get(id=id)


class ScheduleItemQuery(graphene.ObjectType):
    schedule_items = DjangoFilterConnectionField(ScheduleItemNode)
    schedule_item = graphene.relay.Node.Field(ScheduleItemNode)

    def resolve_schedule_items(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitem')

        ## return everything:
        return ScheduleItem.objects.filter()


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

        print(input)

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
        if "schedule_event" in result:
            schedule_item.schedule_event = result['schedule_event']

        if "name" in input:
            schedule_item.name = input['name']

        if "spaces" in input:
            schedule_item.spaces = input['spaces']

        date_end = input.get('date_end', None)
        if "date_end" in input:
            schedule_item.date_end = input['date_end']

        # ALl done, save it :).
        schedule_item.save()

        return CreateScheduleItem(schedule_item=schedule_item)


class UpdateScheduleItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        
    schedule_item = graphene.Field(ScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleitem')

        rid = get_rid(input['id'])

        schedule_item = ScheduleItem.objects.filter(id=rid.id).first()
        if not schedule_item:
            raise Exception('Invalid Schedule Item ID!')

        schedule_item.name = input['name']
        schedule_item.save(force_update=True)

        return UpdateScheduleItem(schedule_item=schedule_item)


class DeleteScheduleItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleitem')

        rid = get_rid(input['id'])
        schedule_item = ScheduleItem.objects.filter(id=rid.id).first()
        if not schedule_item:
            raise Exception('Invalid Organization Level ID!')

        ok = schedule_item.delete()

        return DeleteScheduleItem(ok=ok)


class ScheduleItemMutation(graphene.ObjectType):
    create_schedule_item = CreateScheduleItem.Field()
    update_schedule_item = UpdateScheduleItem.Field()
    delete_schedule_item = DeleteScheduleItem.Field()
