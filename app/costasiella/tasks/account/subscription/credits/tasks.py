import datetime
import logging

from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db import models
from django.db.models import Q, Sum

from .....models import AccountSubscription, AccountSubscriptionCredit
from .....dudes import DateToolsDude

logger = logging.getLogger(__name__)


@shared_task
def account_subscription_credits_add_for_month(year, month):
    """
    Add subscription credits for a given month
    :param year: YYYY
    :param month: 1 ... 2
    :return:
    """
    date_dude = DateToolsDude()

    first_day_month = datetime.date(year, month, 1)
    last_day_month = date_dude.get_last_day_month(first_day_month)

    # Fetch not unlimited rows
    qs = AccountSubscription.objects.filter(
        Q(date_start__lte=last_day_month) &
        (Q(date_end__gte=first_day_month) | Q(date_end__isnull=True)),
        Q(organization_subscription__unlimited=False)
    )

    if not qs.exists():
        # Nothing to do
        return _("No active subscription found in month %s-%s") % (year, month)

    counter = 0
    for account_subscription in qs:
        billable_period = account_subscription.get_billable_period_in_month(year, month)
        if not billable_period['billable_days']:
            # No credits to give. No billable days
            logger.warning('No billable days for subscription %s in month %s-%s' %
                           (account_subscription.id, year, month))
            continue

        credits_given = account_subscription.get_credits_given_for_month(year, month)
        if credits_given.exists():
            # credits for this month have already been given
            logger.warning('Credits already given for subscription %s in month %s-%s' %
                           (account_subscription.id, year, month))
            continue

        if (not account_subscription.organization_subscription.classes and
                not account_subscription.organization_subscription.unlimited):
            # No classes defined for a subscription with limited nr of classes
            logger.warning('No classes defined for subscription %s' %
                           (account_subscription.id))
            continue

        # passed all checks, time to add some credits!
        # Calculate number of credits to give:
        # Total days (Add 1, when subtracted it's one day less)
        account_subscription.create_credits_for_month(year, month)
        account_subscription.book_enrolled_classes_for_month(year, month)
        counter += 1

    return _("Added credits for %s subscriptions") % counter
