import datetime

from celery import shared_task
from django.utils import timezone
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
        counter += 1

    return _("Added credits for %s subscriptions") % counter

    # For row in rows
    # Skip when credits have already been given for a month
    # Skip when no billable days (fully paused)
    # Skip when no classes or subscription unit defined in organization subscription

    # Pass number of billable days to add function for individual subscription
    #TODO book classes when class reservations are implemented

    # Calculate number of credits to give


@shared_task
def account_subscription_credits_expire():
    """
    Expire all credits that are over the accumulation limit today.
    Credits are expired by creating a "SUB" mutation for the excessive amount.
    :return: String - result of task executed
    """
    #TODO: Implement this

    now = timezone.now()
    today = now.date()
    # Go over all subscriptions that are still valid today
    account_subscriptions = AccountSubscription.objects.exclude(
        date_end__lt=today
    ).annotate(
        total_added=Sum(credits__mutation_type="ADD"),
        total_used=Sum(credits__mutation_type="SUB"),
    )

    for account_subscription in account_subscriptions:
        credits_total = account_subscription.total_added - account_subscription.total_used
        print("----")
        print(account_subscription)
        print(credits_total)


    # - get the total sum of credits
    # - get the amount of credits added within the accumulation period

    # if total sum > accumulation period sum:
    # Add a mutation of type sub to expire excess credits





    # def expire_credits(self, date):
    #     """
    #     Check if there are any expired credits, if so, add a subtract mutation with the expired amount
    #     where the 'Expired' field is set to True
    #
    #     :param date: datetime.date
    #     :return: number of subscriptions for which credits were expired
    #     """
    #     T = current.T
    #     db = current.db
    #     NOW_LOCAL = current.NOW_LOCAL
    #     web2pytest = current.globalenv['web2pytest']
    #     request = current.request
    #
    #     # Create dictionary of expiration for school_subscriptions
    #     subscriptions_count_expired = 0
    #     query = (db.school_subscriptions.Archived == False)
    #     rows = db(query).select(db.school_subscriptions.id,
    #                             db.school_subscriptions.CreditValidity)
    #
    #     for row in rows:
    #         if not row.CreditValidity:
    #             continue
    #
    #         # Get list of all active subscriptions
    #         fields = [
    #             db.customers_subscriptions.id,
    #             db.customers_subscriptions.auth_customer_id,
    #             db.customers_subscriptions.Startdate,
    #             db.customers_subscriptions.Enddate,
    #             db.customers_subscriptions.payment_methods_id,
    #             db.school_subscriptions.id,
    #             db.school_subscriptions.Name,
    #             db.customers_subscriptions.CreditsRemaining,
    #             db.customers_subscriptions.PeriodCreditsAdded,
    #         ]
    #
    #         if web2pytest.is_running_under_test(request, request.application):
    #             # the test environment uses sqlite
    #             mutation_date_sql = "date('{date}', '-{validity} day')".format(
    #                 date=date,
    #                 validity=row.CreditValidity
    #             )
    #         else:
    #             # MySQL format
    #             mutation_date_sql = "DATE_SUB('{date}', INTERVAL {validity} DAY)".format(
    #                 date=date,
    #                 validity=row.CreditValidity
    #             )
    #
    #         sql = """SELECT cs.id,
    #                         cs.auth_customer_id,
    #                         cs.Startdate,
    #                         cs.Enddate,
    #                         cs.payment_methods_id,
    #                         ssu.id,
    #                         ssu.Name,
    #                         ( IFNULL((SELECT SUM(csc.MutationAmount)
    #                            FROM customers_subscriptions_credits csc
    #                            WHERE csc.customers_subscriptions_id = cs.id AND
    #                                  csc.MutationType = 'add'), 0) -
    #                            IFNULL(( SELECT SUM(csc.MutationAmount)
    #                            FROM customers_subscriptions_credits csc
    #                            WHERE csc.customers_subscriptions_id = cs.id AND
    #                                  csc.MutationType = 'sub'), 0)) AS credits,
    #                         IFNULL(( SELECT SUM(csc.MutationAmount)
    #                          FROM customers_subscriptions_credits csc
    #                          WHERE csc.customers_subscriptions_id = cs.id AND
    #                                csc.MutationType = 'add' AND
    #                                csc.MutationDateTime >= {mutation_date}), 0) as c_add_in_period
    #                         FROM customers_subscriptions cs
    #                         LEFT JOIN
    #                         school_subscriptions ssu ON cs.school_subscriptions_id = ssu.id
    #                         WHERE ssu.id = {ssuID} AND
    #                               (cs.Startdate <= '{date}' AND
    #                               (cs.Enddate >= '{date}' OR cs.Enddate IS NULL))
    #                         ORDER BY cs.Startdate
    #                         """.format(date=date, ssuID=row.id, mutation_date=mutation_date_sql)
    #
    #         cs_rows = db.executesql(sql, fields=fields)
    #
    #         for row in cs_rows:
    #
    #             expired_credits = (float(row.customers_subscriptions.CreditsRemaining) -
    #                                float(row.customers_subscriptions.PeriodCreditsAdded))
    #
    #             if expired_credits > 0 and row.customers_subscriptions.CreditsRemaining > 0:
    #                 db.customers_subscriptions_credits.insert(
    #                     customers_subscriptions_id=row.customers_subscriptions.id,
    #                     MutationDateTime=NOW_LOCAL,
    #                     MutationType='sub',
    #                     MutationAmount=round(expired_credits, 1),
    #                     Description=T('Credits expiration'),
    #                     Expiration=True
    #                 )
    #
    #                 subscriptions_count_expired += 1
    #
    #     return subscriptions_count_expired
