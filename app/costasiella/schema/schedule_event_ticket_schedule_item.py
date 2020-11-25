from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, ScheduleEvent, ScheduleEventTicketScheduleItem
from ..modules.model_helpers.schedule_event_ticket_schedule_item_helper import ScheduleEventTicketScheduleItemHelper
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class ScheduleEventTicketScheduleItemNode(DjangoObjectType):
    class Meta:
        model = ScheduleEventTicketScheduleItem
        filter_fields = ['schedule_event_ticket', 'schedule_item']
        interfaces = (graphene.relay.Node,)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleeventscheduleitem')

        return self._meta.model.objects.get(id=id)


class ScheduleEventTicketScheduleItemQuery(graphene.ObjectType):
    schedule_event_ticket_schedule_items = DjangoFilterConnectionField(ScheduleEventTicketScheduleItemNode)
    schedule_event_ticket_schedule_item = graphene.relay.Node.Field(ScheduleEventTicketScheduleItemNode)

    def resolve_schedule_event_ticket_schedule_items(self, info, schedule_event, **kwargs):
        user = info.context.user
        require_login(user)
        # Has permission: return everything requested
        if user.has_perm('costasiella.view_scheduleeventticket'):
            rid = get_rid(schedule_event)
            return ScheduleEventTicketScheduleItem.objects.filter(schedule_event=rid.id)

        # Return only public non-archived locations
        return ScheduleEventTicketScheduleItem.objects.filter(schedule_event_ticket__display_public=True)


def validate_create_update_input(input, update=False):
    """
    Validate input
    """
    result = {}

    # Fetch & check schedule event ticket
    if 'schedule_event_ticket' in input:
        if input['schedule_event_ticket']:
            rid = get_rid(input['schedule_event_ticket'])
            schedule_event_ticket = ScheduleEventTicket.objects.filter(id=rid.id).first()
            result['schedule_event_ticket'] = schedule_event_ticket
            if not schedule_event_ticket:
                raise Exception(_('Invalid Schedule Event Ticket ID!'))

    # Fetch & check schedule item
    if 'schedule_item' in input:
        if input['schedule_item']:
            rid = get_rid(input['schedule_item'])
            schedule_item = ScheduleItem.objects.filter(id=rid.id).first()
            result['schedule_item'] = schedule_item
            if not schedule_item:
                raise Exception(_('Invalid Schedule Item ID!'))

    return result


class CreateScheduleEventTicketScheduleItem(graphene.relay.ClientIDMutation):
    class Input:
        schedule_event_ticket = graphene.ID(required=True)
        schedule_item = graphene.ID(required=True)
        included = graphene.ID(required=False)

    schedule_event_ticket_schedule_item = graphene.Field(ScheduleEventTicketScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleeventticketscheduleitem')

        # Validate input
        result = validate_create_update_input(input, update=False)

        schedule_event_ticket_schedule_item = ScheduleEventTicketScheduleItem(
            schedule_event_ticket=result['schedule_event_ticket'],
            schedule_item=result['schedule_item'],
        )

        if 'included' in result:
            schedule_event_ticket_schedule_item.included = result['included']

        schedule_event_ticket_schedule_item.save()

        return CreateScheduleEventTicketScheduleItem(
            schedule_event_ticket_schedule_item=schedule_event_ticket_schedule_item
        )


class UpdateScheduleEventTicketScheduleItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        included = graphene.Boolean(required=True)
        
    schedule_event_ticket_schedule_item = graphene.Field(ScheduleEventTicketScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleeventticketscheduleitem')

        rid = get_rid(input['id'])
        schedule_event_ticket_schedule_item = ScheduleEventTicketScheduleItem.objects.filter(id=rid.id).first()
        if not schedule_event_ticket_schedule_item:
            raise Exception('Invalid Schedule Event Ticket Schedule Item ID!')

        # Validate input
        result = validate_create_update_input(input, update=True)

        if 'included' in input:
            schedule_event_ticket_schedule_item.display_public = input['included']

        schedule_event_ticket_schedule_item.save()

        return UpdateScheduleEventTicketScheduleItem(
            schedule_event_ticket_schedule_item=schedule_event_ticket_schedule_item
        )


class DeleteScheduleEventTicketScheduleItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleeventticketscheduleitem')

        rid = get_rid(input['id'])
        schedule_event_ticket_schedule_item = ScheduleEventTicketScheduleItem.objects.filter(id=rid.id).first()
        if not schedule_event_ticket_schedule_item:
            raise Exception('Invalid Schedule Event Ticket Schedule Item ID!')

        ok = schedule_event_ticket_schedule_item.delete()

        return DeleteScheduleEventTicketScheduleItem(ok=ok)


class ScheduleEventTicketMutation(graphene.ObjectType):
    delete_schedule_event_ticket_schedule_item = DeleteScheduleEventTicketScheduleItem.Field()
    create_schedule_event_ticket_schedule_item = CreateScheduleEventTicketScheduleItem.Field()
    update_schedule_event_ticket_schedule_item = UpdateScheduleEventTicketScheduleItem.Field()
