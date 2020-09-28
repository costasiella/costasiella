import datetime
from collections import namedtuple

from django.utils.translation import gettext as _
from django.utils import timezone
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

    def get_billable_period_in_month(self, year, month):
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
            period_start = latest_start
            period_end = earliest_end
            period_days = period_days - overlap

        return dict(
            period_start=period_start,
            period_end=period_end,
            billable_days=period_days
        )

    def create_credits_for_month(self, year, month):
        # Calculate number of credits to give:
        # Total days (Add 1, when subtracted it's one day less)
        from ..dudes import DateToolsDude
        from .account_subscription_credit import AccountSubscriptionCredit

        date_dude = DateToolsDude()

        first_day_month = datetime.date(year, month, 1)
        last_day_month = date_dude.get_last_day_month(first_day_month)
        total_days = (last_day_month - first_day_month) + datetime.timedelta(days=1)
        billable_period = self.get_billable_period_in_month(year, month)
        billable_days=billable_period['billable_days']

        percent = float(billable_days) / float(total_days.days)
        classes = self.organization_subscription.classes
        if self.organization_subscription.subscription_unit == 'MONTH':
            credits_to_add = round(classes * percent, 1)
        else:
            weeks_in_month = round(total_days.days / float(7), 1)
            credits_to_add = round((weeks_in_month * (classes or 0)) * percent, 1)

        # print("Credits to add: %s" % credits_to_add)

        account_subscription_credit = AccountSubscriptionCredit(
            account_subscription=self,
            mutation_type="ADD",
            mutation_amount=credits_to_add,
            description=_("Credits %s-%s") % (year, month),
            subscription_year=year,
            subscription_month=month,
        )
        account_subscription_credit.save()

        return account_subscription_credit

    def get_credits_total(self):
        """

        :return: Float
        """
        from django.db.models import Sum
        from .account_subscription_credit import AccountSubscriptionCredit

        qs_add = AccountSubscriptionCredit.objects.filter(
            account_subscription=self.id,
            mutation_type="ADD"
        ).aggregate(Sum('mutation_amount'))
        qs_sub = AccountSubscriptionCredit.objects.filter(
            account_subscription=self.id,
            mutation_type="SUB"
        ).aggregate(Sum('mutation_amount'))

        total_add = qs_add['mutation_amount__sum'] or 0
        total_sub = qs_sub['mutation_amount__sum'] or 0

        # Round to 1 decimal and return
        return round(total_add - total_sub, 1)

    def get_usable_credits_total(self):
        """
        Get total credits and add reconciliation credits from subscription (if any)
        :return: Float
        """
        credits_total = self.get_credits_total()
        if self.organization_subscription.reconciliation_classes:
            return_value = credits_total + self.organization_subscription.reconciliation_classes
        else:
            return_value = credits_total

        return round(return_value, 1)

    def get_credits_given_for_month(self, year, month):
        """
        Get credits given for a selected month
        :param year: int
        :param month: int
        :return: query set with added credits for a month
        """
        from .account_subscription_credit import AccountSubscriptionCredit

        qs = AccountSubscriptionCredit.objects.filter(
            Q(account_subscription=self) &
            Q(subscription_year=year) &
            Q(subscription_month=month) &
            Q(mutation_type='ADD')
        )

        return qs

    def create_invoice_for_month(self, year, month, description=None, invoice_date='today'):
        """
            :param year: Year of subscription
            :param month: Month of subscription
            :param description: Invoice description
            :param invoice_date: date of invoice
        """
        from ..dudes import AppSettingsDude, DateToolsDude
        from .account_subscription_alt_price import AccountSubscriptionAltPrice
        from .finance_invoice import FinanceInvoice
        from .finance_invoice_item import FinanceInvoiceItem
        from .finance_invoice_group_default import FinanceInvoiceGroupDefault

        app_settings_dude = AppSettingsDude()
        date_dude = DateToolsDude()

        now = timezone.now()
        today_local = now.date()
        date_format = app_settings_dude.date_format

        first_day_month = datetime.date(year, month, 1)
        last_day_month = date_dude.get_last_day_month(first_day_month)

        # Check if an invoice item is already created for this month
        qs = FinanceInvoiceItem.objects.filter(
            account_subscription=self,
            subscription_year=year,
            subscription_month=month
        )

        if qs.exists():
            # An invoice item already exists for this month. Return the existing invoice item.
            return qs.first()

        # Check if there are billable days in this month
        billable_period = self.get_billable_period_in_month(year, month)
        if not billable_period['billable_days']:
            return

        # Check if the account is active
        if not self.account.is_active:
            return

        # Fetch alt. price for this month (if any)
        qs = AccountSubscriptionAltPrice.objects.filter(
            account_subscription=self,
            subscription_year=year,
            subscription_month=month
        )

        alt_price = None
        if qs.exists():
            alt_price = qs.first()
            if alt_price.amount == 0:
                # A 0 amount has been set in an alt. price. We don't need an invoice this month
                return

        # Check if a regular price is set
        subscription_price = self.organization_subscription.get_price_on_date(first_day_month,
                                                                              raw_price=True)
        if not subscription_price:
            # No price is set, or the price is set to 0.
            return

        # Ok we've survived all checks, continue with invoice creation
        finance_invoice_group = FinanceInvoiceGroupDefault.objects.filter(
            item_type="SUBSCRIPTIONS"
        ).first().finance_invoice_group

        if not description:
            description = _("Subscription")

        #TODO: Add a setting that allows invoices to be created with the 1st of the month as date

        # if invoice_date == 'first_of_month':
        #     date_created = datetime.date(
        #         int(SubscriptionYear),
        #         int(SubscriptionMonth),
        #         1
        #     )
        # else:
        #     date_created = TODAY_LOCAL

        date_created = timezone.now().date()

        finance_invoice = FinanceInvoice(
            account=self.account,
            finance_invoice_group=finance_invoice_group,
            status='SENT',
            summary=_("Subscription invoice %s-%s") % (year, month),
            date_sent=date_created,
            terms=finance_invoice_group.terms,
            footer=finance_invoice_group.footer
        )
        finance_invoice.save()
        finance_invoice_item = finance_invoice.item_add_subscription(self, year, month)

        return finance_invoice_item

        # iID = db.invoices.insert(
        #     invoices_groups_id=igID,
        #     payment_methods_id=self.payment_methods_id,
        #     customers_subscriptions_id=self.csID,
        #     SubscriptionYear=SubscriptionYear,
        #     SubscriptionMonth=SubscriptionMonth,
        #     Description=description,
        #     Status='sent',
        #     DateCreated=date_created
        # )

        # # create object to set Invoice# and due date
        # invoice = Invoice(iID)
        # invoice.link_to_customer(self.auth_customer_id)
        # iiID = invoice.item_add_subscription(self.csID, SubscriptionYear, SubscriptionMonth)
        #
        # return iID
