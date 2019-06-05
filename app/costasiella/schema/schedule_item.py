from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import ScheduleItem, OrganizationLocationRoom
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()

import datetime


class ScheduleItemNode(DjangoObjectType):
    class Meta:
        model = ScheduleItem
        filter_fields = ['schedule_item_type']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitem')

        return self._meta.model.objects.get(id=id)



# # ScheduleClassesType
# class ScheduleClassesType(graphene.ObjectType):
    

# ScheduleClassDayType
class ScheduleClassesDayType(graphene.ObjectType):
    date = graphene.types.datetime.Date()
    # classes = graphene.List(ScheduleClassType


# # ScheduleClassType
# class ScheduleClassType(graphene.ObjectType):
#     id = graphene.ID
#     date = graphene.types.datetime.Date()
#     time_start = graphene.types.datetime.Time()
#     time_end = graphene.types.datetime.Time()


class ScheduleItemQuery(graphene.ObjectType):
    schedule_items = DjangoFilterConnectionField(ScheduleItemNode)
    # schedule_items = graphene.Field(ScheduleItemNode)
    schedule_item = graphene.relay.Node.Field(ScheduleItemNode)
    schedule_classes = graphene.List(ScheduleClassesDayType,
        date_from=graphene.types.datetime.Date(), 
        date_until=graphene.types.datetime.Date()
    )

    def resolve_schedule_items(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitem')

        ## return everything:
        return ScheduleItem.objects.filter()


    def resolve_schedule_classes(self, 
                                 info, 
                                 date_from=graphene.types.datetime.Date(), 
                                 date_until=graphene.types.datetime.Date()):
        delta = datetime.timedelta(days=1)
        date = date_from
        return_list = []
        while date < date_until:
            day = ScheduleClassesDayType()
            day.date = date

            return_list.append(day)
            date += delta

        return return_list


def validate_create_update_input(input, update=False):
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


class CreateScheduleItem(graphene.relay.ClientIDMutation):
    class Input:
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
            schedule_item_type=input['schedule_item_type'], 
            frequency_type=input['frequency_type'], 
            frequency_interval=input['frequency_interval'],
            date_start=input['date_start'],
            time_start=input['time_start'],
            time_end=input['time_end'],   
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
            raise Exception('Invalid Organization Level ID!')

        schedule_item.name = input['name']
        schedule_item.save(force_update=True)

        return UpdateScheduleItem(schedule_item=schedule_item)


class ArchiveScheduleItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    schedule_item = graphene.Field(ScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleitem')

        rid = get_rid(input['id'])

        schedule_item = ScheduleItem.objects.filter(id=rid.id).first()
        if not schedule_item:
            raise Exception('Invalid Organization Level ID!')

        schedule_item.archived = input['archived']
        schedule_item.save(force_update=True)

        return ArchiveScheduleItem(schedule_item=schedule_item)


class ScheduleItemMutation(graphene.ObjectType):
    archive_schedule_item = ArchiveScheduleItem.Field()
    create_schedule_item = CreateScheduleItem.Field()
    update_schedule_item = UpdateScheduleItem.Field()