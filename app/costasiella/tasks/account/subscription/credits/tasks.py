import datetime

from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db import models
from django.db.models import Q, Sum

from .....models import AccountSubscription, AccountSubscriptionCredit
from .....dudes import DateToolsDude

@shared_task
def account_subscription_credits_add_for_month(year, month):
    """
    Add subscription credits for a given month
    :param year: YYYY
    :param month: 1 ... 2
    :return:
    """
    date_dude = DateToolsDude()

    # print("###############")
    # print("Start adding credits")

    first_day_month = datetime.date(year, month, 1)
    last_day_month = date_dude.get_last_day_month(first_day_month)

    # Fetch rows
    qs = AccountSubscription.objects.filter(
        Q(date_start__lte=last_day_month) &
        (Q(date_end__gte=first_day_month) | Q(date_end__isnull=True))
    )

    if not qs.exists():
        # Nothing to do
        return _("No active subscription found in month %s-%s") % (year, month)

    counter = 0
    for account_subscription in qs:
        print(account_subscription)
        billable_period = account_subscription.get_billable_period_in_month(year, month)
        if not billable_period['billable_days']:
            # No credits to give. No billable days
            # print("no billable days")
            continue

        credits_given = account_subscription.get_credits_given_for_month(year, month)
        if credits_given.exists():
            # credits for this month have already been given
            # print("Credits already added")
            continue

        if (not account_subscription.organization_subscription.classes and
                not account_subscription.organization_subscription.unlimited):
            # No classes defined for a subscription with limited nr of classes
            # print("No classes defined")
            continue

        # passed all checks, time to add some credits!
        # Calculate number of credits to give:
        # Total days (Add 1, when subtracted it's one day less)
        account_subscription.create_credits_for_month(year, month)
        account_subscription.book_enrolled_classes_for_month(year, month)
        counter += 1

    return _("Added credits for %s subscriptions") % counter

    # For row in rows
    # Skip when credits have already been given for a month
    # Skip when no billable days (fully paused)
    # Skip when no classes or subscription unit defined in organization subscription

    # Pass number of billable days to add function for individual subscription
    #TODO book classes when class reservations are implemented


@shared_task
def account_subscription_credits_expire():
    """
    Expire all credits that are over the accumulation limit today.
    Credits are expired by creating a "SUB" mutation for the excessive amount.
    :return: String - result of task executed
    """
    now = timezone.now()
    today = now.date()
    # Go over all subscriptions that are still valid today
    # Ref: https://docs.djangoproject.com/en/3.2/topics/db/aggregation/#filtering-on-annotation
    add_mutations = Sum("credits__mutation_amount", filter=Q(credits__mutation_type="ADD"))
    sub_mutations = Sum("credits__mutation_amount", filter=Q(credits__mutation_type="SUB"))
    account_subscriptions = AccountSubscription.objects.exclude(
        date_end__lt=today
    ).annotate(
        total_added=add_mutations,
        total_used=sub_mutations
    )

    subscriptions_with_expired_credits = 0
    for account_subscription in account_subscriptions:
        if account_subscription.organization_subscription.unlimited:
            # Don't do anything for unlimited subscriptions
            continue

        # Calculate total of credits
        total_added = account_subscription.total_added or 0
        total_used = account_subscription.total_used or 0
        total_credits = total_added - total_used

        # Calculate maximum accumulation
        accumulation_period = account_subscription.organization_subscription.credit_accumulation_days
        total_in_accumulation_period = 0
        qs = AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription,
            mutation_type="ADD",
            created_at__gte=(today-datetime.timedelta(days=accumulation_period))
        )

        for subscription_credit in qs:
            total_in_accumulation_period += subscription_credit.mutation_amount

        # Check if the total is over the maximum accumulation (expired)
        expired_credits = total_credits - total_in_accumulation_period
        if expired_credits:
            # If so, expire the surplus credits
            account_subscription_credit = AccountSubscriptionCredit(
                account_subscription=account_subscription,
                mutation_type="SUB",
                mutation_amount=expired_credits,
                description=_("Credit expiration")
            )
            account_subscription_credit.save()

            subscriptions_with_expired_credits += 1

    return _("Expired credits for %s subscriptions") % subscriptions_with_expired_credits

