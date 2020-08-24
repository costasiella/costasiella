import datetime

from celery import shared_task
from django.utils.translation import gettext as _
from django.db.models import Q

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
        billable_days = account_subscription.get_billable_days_in_month(year, month)
        if not billable_days:
            # No credits to give. No billable days
            continue

        credits_given = account_subscription.get_credits_given_for_month(year, month)
        if credits_given.exists():
            # credits for this month have already been given
            continue

        if (not account_subscription.organization_subscription.classes and
                not account_subscription.organization_subscription.unlimited):
            # No classes defined for a subscription with limited nr of classes
            continue

        if (not account_subscription.organization_subscription.classes and
                not account_subscription.organization_subscription.unlimited):
            # No classes defined for a subscription with limited nr of classes
            continue

        # passed all checks, time to add some credits!
        # Calculate number of credits to give:
        # Total days (Add 1, when subtracted it's one day less)
        total_days = (last_day_month - first_day_month) + datetime.timedelta(days=1)

        percent = float(billable_days) / float(total_days.days)
        classes = account_subscription.organization_subscription.classes
        if account_subscription.organization_subscription.subscription_unit == 'MONTH':
            credits_to_add = round(classes * percent, 1)
        else:
            weeks_in_month = round(total_days.days / float(7), 1)
            credits_to_add = round((weeks_in_month * (classes or 0)) * percent, 1)

        account_subscription_credit = AccountSubscriptionCredit(
            account_subscription=account_subscription,
            mutation_type="ADD",
            mutation_amount=credits_to_add,
            subscription_year=year,
            subscription_month=month,
        )
        account_subscription_credit.save()

        counter += 1

    return _("Added credits for %s subscriptions") % counter



    # For row in rows
    # Skip when credits have already been given for a month
    # Skip when no billable days (fully paused)
    # Skip when no classes or subscription unit defined in organization subscription

    # Pass number of billable days to add function for individual subscription
    #TODO book classes when class reservations are implemented

    # Calculate number of credits to give

# def add_credits(self, year, month):
#     """
#         Add subscription credits for month
#     """
#     from .os_customers import Customers
#
#     T = current.T
#     db = current.db
#
#     first_day = datetime.date(year, month, 1)
#     last_day = get_last_day_month(first_day)
#
#     # Get list of bookable classes for each customer, based on recurring reservations
#
#     self.add_credits_reservations = self._get_customers_list_classes_recurring_reservations(year, month)
#     # Get list of total credits balance for each customer
#     customers = Customers()
#     self.add_credits_balance = customers.get_credits_balance(first_day, include_reconciliation_classes=True)
#
#     customers_credits_added = 0
#
#     rows = self.add_credits_get_subscription_rows_month(year, month)
#
#     for row in rows:
#         if row.customers_subscriptions_credits.id:
#             continue
#         if row.customers_subscriptions_paused.id:
#             continue
#         if row.school_subscriptions.Classes == 0 or row.school_subscriptions.Classes is None:
#             continue
#         if row.school_subscriptions.SubscriptionUnit is None:
#             # Don't do anything if this subscription already got credits for this month or is paused
#             # or has no classes or subscription unit defined
#             continue
#
#         # calculate number of credits
#         # only add partial credits if startdate != first day, add full credits if startdate < first day
#         if row.customers_subscriptions.Startdate <= first_day:
#             p_start = first_day
#         else:
#             p_start = row.customers_subscriptions.Startdate
#
#         if row.customers_subscriptions.Enddate is None or row.customers_subscriptions.Enddate >= last_day:
#             p_end = last_day
#         else:
#             p_end = row.customers_subscriptions.Enddate
#
#         self.add_subscription_credits_month(
#             row.customers_subscriptions.id,
#             row.customers_subscriptions.auth_customer_id,
#             year,
#             month,
#             p_start,
#             p_end,
#             row.school_subscriptions.Classes,
#             row.school_subscriptions.SubscriptionUnit,
#         )
#
#         # Increase counter
#         customers_credits_added += 1
#
#     return customers_credits_added or 0