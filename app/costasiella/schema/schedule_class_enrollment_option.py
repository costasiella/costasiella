import graphene

from django.utils.translation import gettext as _
from django.db.models import Q
from django.utils import timezone

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import Account, AccountSubscription, ScheduleItem, ScheduleItemWeeklyOTC
from ..modules.gql_tools import require_login, require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages
from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper
from .account import AccountNode
from .account_subscription import AccountSubscriptionNode
from .schedule_class import ScheduleClassType
from .schedule_item import ScheduleItemNode
from .schedule_item_price import ScheduleItemPriceNode

from ..dudes import ClassCheckinDude, ClassScheduleDude


m = Messages()

import datetime


# ScheduleClassEnrollmentSubscriptionType
class ScheduleClassEnrollmentSubscriptionType(graphene.ObjectType):
    allowed = graphene.Boolean()
    blocked = graphene.Boolean()
    paused = graphene.Boolean()
    account_subscription = graphene.Field(AccountSubscriptionNode)

    
# ScheduleClassEnrollmentOptionsType
class ScheduleClassEnrollmentOptionsType(graphene.ObjectType):
    account = graphene.Field(AccountNode)
    account_id = graphene.ID()
    schedule_item = graphene.Field(ScheduleItemNode)
    schedule_item_id = graphene.ID()
    subscriptions = graphene.List(ScheduleClassEnrollmentSubscriptionType)

    def resolve_account(self, info):
        # account
        rid = get_rid(self.account_id)
        account = Account.objects.get(pk=rid.id)
        if not account:
            raise Exception('Invalid Account ID!')

        return account

    def resolve_schedule_item(self, info):
        # account
        rid = get_rid(self.schedule_item_id)
        schedule_item = ScheduleItem.objects.get(pk=rid.id)
        if not schedule_item:
            raise Exception('Invalid Schedule Item ID!')

        # sih = ScheduleItemHelper()
        # schedule_item = sih.schedule_item_with_otc_and_holiday_data(schedule_item, self.date)

        return schedule_item

    def resolve_subscriptions(self, info):
        checkin_dude = ClassCheckinDude()
        account = self.resolve_account(info)
        schedule_item = self.resolve_schedule_item(info)
        today = timezone.now().date()

        # All subscriptions that haven't ended yet. Also list subscriptions that start in the future.
        subscriptions_filter = (
            Q(account=account) &
            (Q(date_end__gte=today) | Q(date_end__isnull=True))
        )

        subscriptions = AccountSubscription.objects.filter(subscriptions_filter).order_by(
            'organization_subscription__name'
        )

        subscriptions_list = []
        for subscription in subscriptions:
            blocked = subscription.get_blocked_on_date(today)
            paused = subscription.get_paused_on_date(today)

            allowed = False
            if checkin_dude.subscription_enroll_allowed_for_class(subscription, schedule_item):
                allowed = True

            subscriptions_list.append(
                ScheduleClassEnrollmentSubscriptionType(
                    allowed=allowed,
                    blocked=blocked,
                    paused=paused,
                    account_subscription=subscription,
                )
            )

        return subscriptions_list


class ScheduleClassEnrollmentOptionsQuery(graphene.ObjectType):
    schedule_class_enrollment_options = graphene.Field(
        ScheduleClassEnrollmentOptionsType,
        account=graphene.ID(),
        schedule_item=graphene.ID(),
    )

    def resolve_schedule_class_enrollment_options(self, info, schedule_item, **kwargs):
        user = info.context.user
        require_login(user)

        permission = user.has_perm('costasiella.view_scheduleitem')

        account = to_global_id('AccountNode', user.id)
        if 'account' in kwargs and permission:
            # An account has been specified and the current user has permission to view booking options
            # for other accounts
            account = kwargs['account']

        validate_schedule_class_enrollment_options_input(
            account,
            schedule_item,
        )

        return ScheduleClassEnrollmentOptionsType(
            account_id=account,
            schedule_item_id=schedule_item,
        )


def validate_schedule_class_enrollment_options_input(account, schedule_item,):
    """
    Verify ids
    """
    result = {}
   
    # account
    rid = get_rid(account)
    account = Account.objects.get(pk=rid.id)
    if not account:
        raise Exception('Invalid account ID!')

    result['account'] = account

    # schedule_item
    rid = get_rid(schedule_item)
    schedule_item = ScheduleItem.objects.get(pk=rid.id)
    if not schedule_item:
        raise Exception('Invalid Schedule Item ID!')

    result['schedule_item'] = result

    return result
