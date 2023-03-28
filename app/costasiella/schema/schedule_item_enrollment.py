from django.utils.translation import gettext as _

import os
import datetime
import pytz
import graphene
from django.utils import timezone
from django.conf import settings
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from django_filters import FilterSet, OrderingFilter

from ..models import AccountSubscription, ScheduleItem, ScheduleItemEnrollment
from ..modules.gql_tools import require_login, require_login_and_permission, \
                                require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages

from ..dudes import ClassCheckinDude, ClassScheduleDude
from ..tasks import cancel_booked_classes_after_enrollment_end

m = Messages()

class ScheduleItemEnrollmentFilter(FilterSet):
    class Meta:
        model = ScheduleItemEnrollment
        fields = {
            'schedule_item': ['exact'],
            'account_subscription': ['exact'],
            'account_subscription__account': ['exact'],
            'date_start': ['exact', 'gte', 'lte'],
            'date_end': ['exact', 'gt', 'gte', 'lt', 'lte', 'isnull']
        }

    order_by = OrderingFilter(
        fields=(
            ('date_start', 'date_start'), # order by field, display name (used in query)
            ('account_subscription__account__full_name', 'full_name'), # order by field, display name (used in query)
        )
    )


class ScheduleItemEnrollmentNode(DjangoObjectType):
    class Meta:
        model = ScheduleItemEnrollment
        filterset_class = ScheduleItemEnrollmentFilter
        fields = (
            'schedule_item',
            'account_subscription',
            'date_start',
            'date_end',
            'created_at',
            'updated_at'
        )
        # account_schedule_event_ticket_Isnull filter can be used to differentiate class & event enrollment
        # filter_fields = {
        #     'schedule_item': ['exact'],
        #     'account_subscription': ['exact'],
        #     'account_subscription__account': ['exact'],
        #     'date_start': ['exact', 'gte', 'lte'],
        #     'date_end': ['exact', 'gt', 'gte', 'lt', 'lte', 'isnull']
        # }
        interfaces = (graphene.relay.Node,)

    @classmethod
    def get_node(cls, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemenrollment')

        return cls._meta.model.objects.get(id=id)


class ScheduleItemEnrollmentQuery(graphene.ObjectType):
    # finance_quote_items = DjangoFilterConnectionField(
    #     FinanceQuoteItemNode,
    #     filterset_class=FinanceQuoteItemFilter,
    #     orderBy=graphene.List(of_type=graphene.String)
    # )

    schedule_item_enrollments = DjangoFilterConnectionField(
        ScheduleItemEnrollmentNode
    )
    schedule_item_enrollment = graphene.relay.Node.Field(ScheduleItemEnrollmentNode)

    def resolve_schedule_item_enrollments(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemenrollment')

        return ScheduleItemEnrollment.objects.order_by('account_subscription__account__full_name')

        ## Code below can someday be modified to allow a filtering enrollments by accounts & allow users to
        ## view their own enrollments
        # require_login(user)
        #
        # view_permission = user.has_perm('costasiella.view_scheduleitemenrollment')
        #
        # if view_permission and 'account' in kwargs:
        #     # Allow user to filter by any account
        #     rid = get_rid(kwargs.get('account', user.id))
        #     account_id = rid.id
        # elif view_permission:
        #     # return all
        #     account_id = None
        # else:
        #     # A user can only query their own orders
        #     account_id = user.id
        #
        # if account_id:
        #     order_by = '-date_start'
        #     return ScheduleItemEnrollment.objects.filter(account=account_id).order_by(order_by)
        # else:
        #     order_by = '-account__full_name'
        #     return ScheduleItemEnrollment.objects.all().order_by(order_by)
            

def validate_schedule_item_enrollment_create_update_input(input):
    """
    Validate input
    """ 
    result = {}

    # Check AccountSubscription
    if 'account_subscription' in input:
        if input['account_subscription']:
            rid = get_rid(input['account_subscription'])
            account_subscription = AccountSubscription.objects.filter(id=rid.id).first()
            result['account_subscription'] = account_subscription
            if not account_subscription:
                raise Exception(_('Invalid Account Subscription ID!'))

    # Check Schedule Item
    if 'schedule_item' in input:
        if input['schedule_item']:
            rid = get_rid(input['schedule_item'])
            schedule_item = ScheduleItem.objects.get(id=rid.id)
            result['schedule_item'] = schedule_item
            if not schedule_item:
                raise Exception(_('Invalid Schedule Item (class) ID!'))        

    return result


class CreateScheduleItemEnrollment(graphene.relay.ClientIDMutation):
    class Input:
        schedule_item = graphene.ID(required=True)
        account_subscription = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False)

    schedule_item_enrollment = graphene.Field(ScheduleItemEnrollmentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleitemenrollment')

        date_start = input['date_start']

        validation_result = validate_schedule_item_enrollment_create_update_input(input)
        account_subscription = validation_result['account_subscription']

        schedule_item_enrollment = ScheduleItemEnrollment(
            schedule_item=validation_result['schedule_item'],
            account_subscription=account_subscription,
            date_start=date_start
        )

        if 'date_end' in input:
            schedule_item_enrollment.date_end = input['date_end']

        schedule_item_enrollment.save()

        # Book enrollment classes for this and next month
        first_day_of_month = datetime.date(date_start.year, date_start.month, 1)
        first_day_of_next_month = first_day_of_month + datetime.timedelta(days=32)
        account_subscription.book_enrolled_classes_for_month(
            first_day_of_month.year, first_day_of_month.month
        )
        account_subscription.book_enrolled_classes_for_month(
            first_day_of_next_month.year, first_day_of_next_month.month
        )

        return CreateScheduleItemEnrollment(schedule_item_enrollment=schedule_item_enrollment)


class UpdateScheduleItemEnrollment(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=False)
        date_end = graphene.types.datetime.Date(required=False)
        
    schedule_item_enrollment = graphene.Field(ScheduleItemEnrollmentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleitemenrollment')

        rid = get_rid(input['id'])
        schedule_item_enrollment = ScheduleItemEnrollment.objects.filter(id=rid.id).first()
        if not schedule_item_enrollment:
            raise Exception('Invalid Schedule Item Enrollment ID!')

        if 'date_start' in input:
            schedule_item_enrollment.date_start = input['date_start']

        if 'date_end' in input:
            schedule_item_enrollment.date_end = input['date_end']

        schedule_item_enrollment.save()

        if schedule_item_enrollment.date_end:
            # Call background task to create batch items when we're not in CI test mode
            if 'GITHUB_WORKFLOW' not in os.environ and not getattr(settings, 'TESTING', False):
                task = cancel_booked_classes_after_enrollment_end.delay(
                    account_subscription_id=schedule_item_enrollment.account_subscription.id,
                    schedule_item_id=schedule_item_enrollment.schedule_item.id,
                    cancel_bookings_from_date=str(schedule_item_enrollment.date_end)
                )

        return UpdateScheduleItemEnrollment(schedule_item_enrollment=schedule_item_enrollment)


class DeleteScheduleItemEnrollment(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleitemenrollment')

        rid = get_rid(input['id'])
        schedule_item_enrollment = ScheduleItemEnrollment.objects.filter(id=rid.id).first()
        if not schedule_item_enrollment:
            raise Exception('Invalid Schedule Item Enrollment ID!')

        # Cancel all class bookings enrollment subscription after today
        # Set end date
        today = timezone.now().date()
        if 'GITHUB_WORKFLOW' not in os.environ and not getattr(settings, 'TESTING', False):
            task = cancel_booked_classes_after_enrollment_end.delay(
                account_subscription_id=schedule_item_enrollment.account_subscription.id,
                schedule_item_id=schedule_item_enrollment.schedule_item.id,
                cancel_bookings_from_date=str(today)
            )

        # Actually remove
        ok = bool(schedule_item_enrollment.delete())

        return DeleteScheduleItemEnrollment(ok=ok)


class ScheduleItemEnrollmentMutation(graphene.ObjectType):
    delete_schedule_item_enrollment = DeleteScheduleItemEnrollment.Field()
    create_schedule_item_enrollment = CreateScheduleItemEnrollment.Field()
    update_schedule_item_enrollment = UpdateScheduleItemEnrollment.Field()
