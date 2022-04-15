from django.utils.translation import gettext as _
from django.db.models import Q

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import ScheduleEvent, ScheduleEventEarlybird
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class ScheduleEventEarlybirdNode(DjangoObjectType):
    class Meta:
        model = ScheduleEventEarlybird
        fields = (
            'schedule_event',
            'date_start',
            'date_end',
            'discount_percentage',
            'created_at',
            'updated_at'
        )
        filter_fields = ['schedule_event']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user

        permission = 'costasiella.view_scheduleeventearlybird'

        schedule_event_earlybird = self._meta.model.objects.get(id=id)
        if user.has_perm(permission):
            return schedule_event_earlybird
        elif (schedule_event_earlybird.schedule_event.display_public or
              schedule_event_earlybird.schedule_event.display_shop):
            return schedule_event_earlybird


class ScheduleEventEarlybirdQuery(graphene.ObjectType):
    schedule_event_earlybirds = DjangoFilterConnectionField(ScheduleEventEarlybirdNode)
    schedule_event_earlybird = graphene.relay.Node.Field(ScheduleEventEarlybirdNode)

    def resolve_schedule_event_earlybirds(self, info, schedule_event, **kwargs):
        user = info.context.user
        permission = 'costasiella.view_scheduleeventearlybird'

        rid = get_rid(schedule_event)
        qs = ScheduleEventEarlybird.objects.filter(Q(schedule_event=rid.id))

        # Earlybird discounts public status is linked to schedule event public status
        if not user.has_perm(permission):
            qs = qs.filter((Q(schedule_event__display_public=True) or Q(schedule_event__display_shop=True)))

        return qs.order_by('-date_start')


def validate_create_update_input(input, update=False):
    """
    Validate input
    """
    result = {}

    if not update:
        # Fetch & check schedule event (insert only)
        rid = get_rid(input['schedule_event'])
        schedule_event = ScheduleEvent.objects.filter(id=rid.id).first()
        result['schedule_event'] = schedule_event
        if not schedule_event:
            raise Exception(_('Invalid Schedule Event ID!'))

    return result


class CreateScheduleEventEarlybird(graphene.relay.ClientIDMutation):
    class Input:
        schedule_event = graphene.ID(required=True)
        discount_percentage = graphene.Decimal(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=True)

    schedule_event_earlybird = graphene.Field(ScheduleEventEarlybirdNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleeventearlybird')

        # Validate input
        result = validate_create_update_input(input, update=False)

        schedule_event_earlybird = ScheduleEventEarlybird(
            schedule_event=result['schedule_event'],
            discount_percentage=input['discount_percentage'],
            date_start=input['date_start'],
            date_end=input['date_end']
        )

        schedule_event_earlybird.save()

        return CreateScheduleEventEarlybird(schedule_event_earlybird=schedule_event_earlybird)


class UpdateScheduleEventEarlybird(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        discount_percentage = graphene.Decimal(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=True)
        
    schedule_event_earlybird = graphene.Field(ScheduleEventEarlybirdNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleeventearlybird')

        rid = get_rid(input['id'])
        schedule_event_earlybird = ScheduleEventEarlybird.objects.filter(id=rid.id).first()
        if not schedule_event_earlybird:
            raise Exception('Invalid Schedule Event Earlybird ID!')

        # Validate input
        result = validate_create_update_input(input, update=True)

        if 'discount_percentage' in input:
            schedule_event_earlybird.discount_percentage = input['discount_percentage']
        if 'date_start' in input:
            schedule_event_earlybird.date_start = input['date_start']
        if 'date_end' in input:
            schedule_event_earlybird.date_end = input['date_end']

        schedule_event_earlybird.save()

        return UpdateScheduleEventEarlybird(schedule_event_earlybird=schedule_event_earlybird)


class DeleteScheduleEventEarlybird(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleeventearlybird')

        rid = get_rid(input['id'])
        schedule_event_earlybird = ScheduleEventEarlybird.objects.filter(id=rid.id).first()
        if not schedule_event_earlybird:
            raise Exception('Invalid Schedule Event Earlybird ID!')

        ok = bool(schedule_event_earlybird.delete())

        return DeleteScheduleEventEarlybird(ok=ok)


class ScheduleEventEarlybirdMutation(graphene.ObjectType):
    delete_schedule_event_earlybird = DeleteScheduleEventEarlybird.Field()
    create_schedule_event_earlybird = CreateScheduleEventEarlybird.Field()
    update_schedule_event_earlybird = UpdateScheduleEventEarlybird.Field()
