from django.utils.translation import gettext as _
from django.db.models import Q

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationSubscriptionGroup, ScheduleEvent, ScheduleEventSubscriptionGroupDiscount
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class ScheduleEventSubscriptionGroupDiscountNode(DjangoObjectType):
    class Meta:
        model = ScheduleEventSubscriptionGroupDiscount
        fields = (
            'schedule_event',
            'organization_subscription_group',
            'discount_percentage',
            'created_at',
            'updated_at'
        )
        filter_fields = ['schedule_event']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user

        permission = 'costasiella.view_scheduleeventsubscriptiongroupdiscount'

        schedule_event_subscription_group_discount = self._meta.model.objects.get(id=id)
        if user.has_perm(permission):
            return schedule_event_subscription_group_discount
        elif (schedule_event_subscription_group_discount.schedule_event.display_public or
              schedule_event_subscription_group_discount.schedule_event.display_shop):
            return schedule_event_subscription_group_discount


class ScheduleEventSubscriptionGroupDiscountQuery(graphene.ObjectType):
    schedule_event_subscription_group_discounts = DjangoFilterConnectionField(
        ScheduleEventSubscriptionGroupDiscountNode
    )
    schedule_event_subscription_group_discount = graphene.relay.Node.Field(
        ScheduleEventSubscriptionGroupDiscountNode
    )

    def resolve_schedule_event_subscription_group_discounts(self, info, schedule_event, **kwargs):
        user = info.context.user
        permission = 'costasiella.view_scheduleeventsubscriptiongroupdiscount'

        rid = get_rid(schedule_event)
        qs = ScheduleEventSubscriptionGroupDiscount.objects.filter(Q(schedule_event=rid.id))

        # Subscription group discounts public status is linked to schedule event public status
        if not user.has_perm(permission):
            qs = qs.filter((Q(schedule_event__display_public=True) or Q(schedule_event__display_shop=True)))

        return qs


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

    # Fetch & check organization subscription group
    rid = get_rid(input['organization_subscription_group'])
    organization_subscription_group = \
        OrganizationSubscriptionGroup.objects.filter(id=rid.id).first()
    result['organization_subscription_group'] = organization_subscription_group
    if not organization_subscription_group:
        raise Exception(_('Invalid Organization Subscription Group ID!'))

    return result


class CreateScheduleEventSubscriptionGroupDiscount(graphene.relay.ClientIDMutation):
    class Input:
        schedule_event = graphene.ID(required=True)
        organization_subscription_group = graphene.ID(required=True)
        discount_percentage = graphene.Decimal(required=True)

    schedule_event_subscription_group_discount = graphene.Field(ScheduleEventSubscriptionGroupDiscountNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleeventsubscriptiongroupdiscount')

        # Validate input
        result = validate_create_update_input(input, update=False)

        schedule_event_subscription_group_discount = ScheduleEventSubscriptionGroupDiscount(
            schedule_event=result['schedule_event'],
            organization_subscription_group=result['organization_subscription_group'],
            discount_percentage=input['discount_percentage'],
        )

        schedule_event_subscription_group_discount.save()

        return CreateScheduleEventSubscriptionGroupDiscount(
            schedule_event_subscription_group_discount=schedule_event_subscription_group_discount
        )


class UpdateScheduleEventSubscriptionGroupDiscount(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        organization_subscription_group = graphene.ID(required=False)
        discount_percentage = graphene.Decimal(required=False)
        
    schedule_event_subscription_group_discount = graphene.Field(ScheduleEventSubscriptionGroupDiscountNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleeventsubscriptiongroupdiscount')

        rid = get_rid(input['id'])
        schedule_event_subscription_group_discount = \
            ScheduleEventSubscriptionGroupDiscount.objects.filter(id=rid.id).first()
        if not schedule_event_subscription_group_discount:
            raise Exception('Invalid Schedule Event Subscription Group Discount ID!')

        # Validate input
        result = validate_create_update_input(input, update=True)

        if 'organization_subscription_group' in result:
            schedule_event_subscription_group_discount.organization_subscription_group = \
                result['organization_subscription_group']

        if 'discount_percentage' in input:
            schedule_event_subscription_group_discount.discount_percentage = input['discount_percentage']

        schedule_event_subscription_group_discount.save()

        return UpdateScheduleEventSubscriptionGroupDiscount(
            schedule_event_subscription_group_discount=schedule_event_subscription_group_discount
        )


class DeleteScheduleEventSubscriptionGroupDiscount(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleeventsubscriptiongroupdiscount')

        rid = get_rid(input['id'])
        schedule_event_subscription_group_discount = \
            ScheduleEventSubscriptionGroupDiscount.objects.filter(id=rid.id).first()
        if not schedule_event_subscription_group_discount:
            raise Exception('Invalid Schedule Event Subscription Group Discount ID!')

        ok = bool(schedule_event_subscription_group_discount.delete())

        return DeleteScheduleEventSubscriptionGroupDiscount(ok=ok)


class ScheduleEventSubscriptionGroupDiscountMutation(graphene.ObjectType):
    delete_schedule_event_subscription_group_discount = DeleteScheduleEventSubscriptionGroupDiscount.Field()
    create_schedule_event_subscription_group_discount = CreateScheduleEventSubscriptionGroupDiscount.Field()
    update_schedule_event_subscription_group_discount = UpdateScheduleEventSubscriptionGroupDiscount.Field()
