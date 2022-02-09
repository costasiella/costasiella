from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from django_filters import FilterSet, OrderingFilter

from ..models import Account, ScheduleEvent, ScheduleEventTicketScheduleItem
from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper
from ..modules.model_helpers.schedule_event_ticket_schedule_item_helper import ScheduleEventTicketScheduleItemHelper
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class CustomOrderingFilter(OrderingFilter):
    """
    A Custom ordering filter to allow ordering by multiple fields
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra['choices'] += [
            ('date_start', 'Date start'),
            ('-date_start', 'Date start (descending)'),
        ]

    def filter(self, qs, value):
        # OrderingFilter is CSV-based, so `value` is a list
        value = ['date_start'] if not value else value  # Set a default:

        if any(v in ['date_start', '-date_start'] for v in value):
            # sort queryset by relevance
            return qs.order_by('schedule_item__date_start', 'schedule_item__time_start')

        return super().filter(qs, value)


class ScheduleEventTicketScheduleItemFilter(FilterSet):
    class Meta:
        model = ScheduleEventTicketScheduleItem
        fields = ['schedule_event_ticket', 'schedule_item', 'included']

    order_by = CustomOrderingFilter()


class ScheduleEventTicketScheduleItemNode(DjangoObjectType):
    class Meta:
        model = ScheduleEventTicketScheduleItem
        fields = (
            'schedule_event_ticket',
            'schedule_item',
            'included'
        )
        filterset_class = ScheduleEventTicketScheduleItemFilter
        interfaces = (graphene.relay.Node,)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleeventscheduleitem')

        return self._meta.model.objects.get(id=id)


class ScheduleEventTicketScheduleItemQuery(graphene.ObjectType):
    schedule_event_ticket_schedule_items = DjangoFilterConnectionField(ScheduleEventTicketScheduleItemNode)
    schedule_event_ticket_schedule_item = graphene.relay.Node.Field(ScheduleEventTicketScheduleItemNode)

    def resolve_schedule_event_ticket_schedule_items(self, info, schedule_event_ticket, **kwargs):
        user = info.context.user
        require_login(user)

        rid = get_rid(schedule_event_ticket)
        qs = ScheduleEventTicketScheduleItem.objects.filter(schedule_event_ticket=rid.id)

        if not user.has_perm('costasiella.view_scheduleeventticket'):
            # Only items for public tickets
            qs = qs.filter(schedule_event_ticket__display_public=True)

        return qs.order_by('schedule_item__date_start', 'schedule_item__time_start')


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


# class CreateScheduleEventTicketScheduleItem(graphene.relay.ClientIDMutation):
#     class Input:
#         schedule_event_ticket = graphene.ID(required=True)
#         schedule_item = graphene.ID(required=True)
#         included = graphene.ID(required=False)
#
#     schedule_event_ticket_schedule_item = graphene.Field(ScheduleEventTicketScheduleItemNode)
#
#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.add_scheduleeventticketscheduleitem')
#
#         # Validate input
#         result = validate_create_update_input(input, update=False)
#
#         schedule_event_ticket_schedule_item = ScheduleEventTicketScheduleItem(
#             schedule_event_ticket=result['schedule_event_ticket'],
#             schedule_item=result['schedule_item'],
#         )
#
#         if 'included' in result:
#             schedule_event_ticket_schedule_item.included = result['included']
#
#         schedule_event_ticket_schedule_item.save()
#
#         return CreateScheduleEventTicketScheduleItem(
#             schedule_event_ticket_schedule_item=schedule_event_ticket_schedule_item
#         )


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

        if schedule_event_ticket_schedule_item.schedule_event_ticket.full_event:
            raise Exception('For a full event ticket, all schedule items for this event are included!')

        if 'included' in input:
            schedule_event_ticket_schedule_item.included = input['included']

        schedule_event_ticket_schedule_item.save()

        # Add or remove attendance rows
        schedule_item_helper = ScheduleItemHelper()

        if schedule_event_ticket_schedule_item.included:
            schedule_event = schedule_event_ticket_schedule_item.schedule_event_ticket.schedule_event
            schedule_item_helper.create_attendance_records_for_event_schedule_items(schedule_event)
        else:
            schedule_item_helper.remove_attendance_from_event_ticket(
                schedule_item=schedule_event_ticket_schedule_item.schedule_item,
                schedule_event_ticket=schedule_event_ticket_schedule_item.schedule_event_ticket
            )

        return UpdateScheduleEventTicketScheduleItem(
            schedule_event_ticket_schedule_item=schedule_event_ticket_schedule_item
        )


# class DeleteScheduleEventTicketScheduleItem(graphene.relay.ClientIDMutation):
#     class Input:
#         id = graphene.ID(required=True)
#
#     ok = graphene.Boolean()
#
#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.delete_scheduleeventticketscheduleitem')
#
#         rid = get_rid(input['id'])
#         schedule_event_ticket_schedule_item = ScheduleEventTicketScheduleItem.objects.filter(id=rid.id).first()
#         if not schedule_event_ticket_schedule_item:
#             raise Exception('Invalid Schedule Event Ticket Schedule Item ID!')
#
#         ok = schedule_event_ticket_schedule_item.delete()
#
#         return DeleteScheduleEventTicketScheduleItem(ok=ok)


class ScheduleEventTicketScheduleItemMutation(graphene.ObjectType):
    # delete_schedule_event_ticket_schedule_item = DeleteScheduleEventTicketScheduleItem.Field()
    # create_schedule_event_ticket_schedule_item = CreateScheduleEventTicketScheduleItem.Field()
    update_schedule_event_ticket_schedule_item = UpdateScheduleEventTicketScheduleItem.Field()
