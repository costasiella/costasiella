import graphene

from django.utils.translation import gettext as _
from django.db.models import Q

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import Account, AccountClasspass, AccountSubscription, \
                     ScheduleItem, ScheduleItemPrice, ScheduleItemWeeklyOTC
from ..modules.gql_tools import require_login, require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages
from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper
from .account import AccountNode
from .account_classpass import AccountClasspassNode
from .account_subscription import AccountSubscriptionNode
from .schedule_class import ScheduleClassType
from .schedule_item import ScheduleItemNode
from .schedule_item_price import ScheduleItemPriceNode

from ..dudes import ClassCheckinDude, ClassScheduleDude
from ..modules.gql_tools import get_error_code

m = Messages()

import datetime


# ScheduleClassBookingClasspassType
class ScheduleClassBookingClasspassType(graphene.ObjectType):
    booking_type = graphene.String()
    allowed = graphene.Boolean()  
    account_classpass = graphene.Field(AccountClasspassNode)


# ScheduleClassBookingSubscriptionType
class ScheduleClassBookingSubscriptionType(graphene.ObjectType):
    booking_type = graphene.String()
    allowed = graphene.Boolean()  
    blocked = graphene.Boolean()
    paused = graphene.Boolean()
    credits_on_date = graphene.Int()
    account_subscription = graphene.Field(AccountSubscriptionNode)

    
# ScheduleClassBookingOptionsType
class ScheduleClassBookingOptionsType(graphene.ObjectType):  
    date = graphene.types.datetime.Date()
    list_type = graphene.String()
    account = graphene.Field(AccountNode)
    account_id = graphene.ID()
    schedule_item = graphene.Field(ScheduleItemNode)
    schedule_item_id = graphene.ID()
    classpasses = graphene.List(ScheduleClassBookingClasspassType)
    subscriptions = graphene.List(ScheduleClassBookingSubscriptionType)
    schedule_item_prices = graphene.Field(ScheduleItemPriceNode)
    already_booked = graphene.Boolean()

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

        sih = ScheduleItemHelper()
        schedule_item = sih.schedule_item_with_otc_and_holiday_data(schedule_item, self.date)

        return schedule_item

    def resolve_schedule_item_prices(self, info):
        # Drop-in classpass
        schedule_item = self.resolve_schedule_item(info)

        qs = ScheduleItemPrice.objects.filter(
            Q(schedule_item=schedule_item) &
            Q(date_start__lte=self.date) &
            (Q(date_end__gte=self.date ) | Q(date_end__isnull=True))
        )

        if qs.exists():
            return qs.first()
        else:
            return None

    def resolve_classpasses(self, 
                            info,
                            date=graphene.types.datetime.Date(),
                            ):
        checkin_dude = ClassCheckinDude()
        account = self.resolve_account(info)
        schedule_item = self.resolve_schedule_item(info)

        classpasses_filter = (
            Q(account=account) &
            Q(date_start__lte=self.date) &
            (Q(date_end__gte=self.date) | Q(date_end__isnull=True)) &
            (Q(classes_remaining__gt=0) | Q(organization_classpass__unlimited=True))
        )

        classpasses = AccountClasspass.objects.filter(classpasses_filter).order_by('organization_classpass__name')

        classpasses_list = []
        for classpass in classpasses:
            allowed = False
            if self.list_type == "ATTEND":
                if checkin_dude.classpass_attend_allowed_for_class(classpass, schedule_item):
                    allowed = True
            elif self.list_type == "SHOP_BOOK":
                if checkin_dude.classpass_shop_book_allowed_for_class(classpass, schedule_item):
                    allowed = True

            classpasses_list.append(
                ScheduleClassBookingClasspassType(
                    booking_type="CLASSPASS",
                    allowed=allowed,
                    account_classpass=classpass,
                )
            )

        return classpasses_list

    def resolve_subscriptions(self, 
                              info,
                              date=graphene.types.datetime.Date(),
                              ):
        checkin_dude = ClassCheckinDude()
        account = self.resolve_account(info)
        schedule_item = self.resolve_schedule_item(info)

        subscriptions_filter = Q(account=account) & \
            Q(date_start__lte=self.date) & \
            (Q(date_end__gte=self.date) | Q(date_end__isnull=True))

        subscriptions = AccountSubscription.objects.filter(subscriptions_filter).order_by('organization_subscription__name')

        subscriptions_list = []
        for subscription in subscriptions:
            blocked = subscription.get_blocked_on_date(self.date)
            paused = subscription.get_paused_on_date(self.date)

            allowed = False
            if self.list_type == "ATTEND":
                if checkin_dude.subscription_attend_allowed_for_class(subscription, schedule_item):
                    allowed = True
            elif self.list_type == "SHOP_BOOK":
                if checkin_dude.subscription_shop_book_allowed_for_class(subscription, schedule_item):
                    allowed = True

            subscriptions_list.append(
                ScheduleClassBookingSubscriptionType(
                    booking_type="SUBSCRIPTION",
                    allowed=allowed,
                    blocked=blocked,
                    paused=paused,
                    credits_on_date=subscription.get_credits_total(self.date),
                    account_subscription=subscription,
                )
            )

        return subscriptions_list

    def resolve_already_booked(self, info):
        """
        Check if the account is already attending this class
        """
        checkin_dude = ClassCheckinDude()
        return checkin_dude.class_check_checkedin(
            account=self.resolve_account(info),
            schedule_item=self.resolve_schedule_item(info),
            date=self.date
        )


class ScheduleClassBookingOptionsQuery(graphene.ObjectType):
    schedule_class_booking_options = graphene.Field(
        ScheduleClassBookingOptionsType,
        account=graphene.ID(),
        schedule_item=graphene.ID(),
        date=graphene.types.datetime.Date(),
        list_type=graphene.String(default_value="SHOP_BOOK")
    )

    def resolve_schedule_class_booking_options(self, info, list_type, schedule_item, date, **kwargs):
        user = info.context.user
        require_login(user)

        permission = \
            user.has_perm('costasiella.view_scheduleitem') or \
            user.has_perm('costasiella.view_scheduleclass') or \
            user.has_perm('costasiella.add_scheduleitemattendance') or \
            user.has_perm('costasiella.view_selfcheckin')

        account = to_global_id('AccountNode', user.id)
        if 'account' in kwargs and kwargs['account'] and permission:
            # An account has been specified and the current user has permission to view booking options
            # for other accounts
            account = kwargs['account']

        validate_schedule_class_booking_options_input(
            account,
            schedule_item,
            date,
            list_type,
        )

        return ScheduleClassBookingOptionsType(
            date=date,
            list_type=list_type,
            account_id=account,
            schedule_item_id=schedule_item,
        )


def validate_schedule_class_booking_options_input(account, schedule_item, date, list_type):
    """
    Check if date_until >= date_start
    Check if delta between dates <= 7 days
    """
    result = {}

    list_types = [
        'ATTEND',
        'ENROLL',
        'SHOP_BOOK'
    ]

    if list_type not in list_types:
        raise Exception('Invalid list type, possible options [ATTEND, ENROLL, SHOP_BOOK]')
   
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

    # Check if schedule item takes place on date
    schedule_dude = ClassScheduleDude()
    if not schedule_dude.schedule_item_takes_place_on_day(schedule_item, date):
        raise GraphQLError(
            f"This class doesn't take place on date: {date}",
            extensions={'code': get_error_code('CLASS_DOESNT_TAKE_PLACE_ON_DATE')})

    return result

