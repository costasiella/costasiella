import datetime
from collections import namedtuple

from django.db import models
from django.db.models import Q

from .account import Account
from .organization_subscription import OrganizationSubscription
from .finance_payment_method import FinancePaymentMethod


class AccountSubscription(models.Model):
    # add additional fields in here
    # teacher and employee will use OneToOne fields. An account can optionally be a teacher or employee.
    # Editable parameter docs
    # https://docs.djangoproject.com/en/2.2/ref/models/fields/#editable

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="subscriptions")
    organization_subscription = models.ForeignKey(OrganizationSubscription, on_delete=models.CASCADE)
    finance_payment_method = models.ForeignKey(FinancePaymentMethod, on_delete=models.CASCADE, null=True)
    date_start = models.DateField()
    date_end = models.DateField(null=True)
    note = models.TextField(default="")
    registration_fee_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.organization_subscription.name + ' [' + str(self.date_start) + ']'

    def get_billable_days_in_month(self, year, month):
        """
        Get billable number of days for a given month.
        The number of billable days is calculated by checking if the subscription starts or ends before or after the
        end of the month and if there's a pause in this month.

        :param year: int (YYYY)
        :param month: int (1 - 12)
        :return:
        """
        from .account_subscription_pause import AccountSubscriptionPause
        from ..dudes import DateToolsDude

        date_dude = DateToolsDude()
        first_day_month = datetime.date(year, month, 1)
        last_day_month = date_dude.get_last_day_month(first_day_month)

        broken_period = False
        pause = False

        # Check pause
        qs_pause = AccountSubscriptionPause.objects.filter(
            Q(id=self.id) &
            Q(date_start__lte=last_day_month) &
            (Q(date_end__gte=first_day_month) | Q(date_end__isnull=True)),
        )

        account_subscription_pause = None
        if qs_pause.exists():
            account_subscription_pause = qs_pause.first()

        # Calculate days to be paid
        period_start = first_day_month
        if self.date_start > first_day_month and self.date_start <= last_day_month:
            # Start later in month
            broken_period = True
            period_start = self.date_start

        period_end = last_day_month
        if self.date_end:
            if self.date_end >= first_day_month and self.date_end < last_day_month:
                # End somewhere in month
                broken_period = True
                period_end = self.date_end

        Range = namedtuple('Range', ['start', 'end'])
        period_range = Range(start=period_start, end=period_end)
        period_days = (period_range.end - period_range.start).days + 1

        if account_subscription_pause:
            # Set pause end date to period end if > period end
            pause_end = account_subscription_pause.date_end
            if pause_end >= period_range.end:
                pause_end = period_range.end

            pause_range = Range(start=account_subscription_pause.date_start, end=pause_end)
            latest_start = max(period_range.start, pause_range.start)
            earliest_end = min(pause_range.end, pause_range.end)
            delta = (earliest_end - latest_start).days + 1
            overlap = max(0, delta)

            # Subtract pause overlap from period to be paid
            period_days = period_days - overlap

        return period_days

    def get_credits_given_for_month(self, year, month):
        """
        Get credits given for a selected month
        :param year: int
        :param month: int
        :return: query set with added credits for a month
        """
        from .account_subscription_credit import AccountSubscriptionCredit

        qs = AccountSubscriptionCredit.objects.filter(
            Q(subscription_year=year) &
            Q(subscription_month=month) &
            Q(mutation_type='ADD')
        )

        return qs
