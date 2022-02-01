import datetime
from collections import namedtuple

from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models
from django.db.models import Q

from .account import Account
from .organization_subscription import OrganizationSubscription
from .finance_payment_method import FinancePaymentMethod

from ..modules.cs_errors import CSClassBookingSubscriptionBlockedError, \
    CSClassBookingSubscriptionPausedError, \
    CSClassBookingSubscriptionNoCreditsError

class AccountSubscription(models.Model):
    # add additional fields in here
    # instructor and employee will use OneToOne fields. An account can optionally be a instructor or employee.
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
            Q(account_subscription=self) &
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

    def _calculate_credits_for_month(self, year, month):
        """ Calculate number of credits for a given month """
        from ..dudes import DateToolsDude

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

        return credits_to_add


    def create_credits_for_month(self, year, month):
        # Calculate number of credits to give:
        # Total days (Add 1, when subtracted it's one day less)
        from .account_subscription_credit import AccountSubscriptionCredit

        credits_to_add = self._calculate_credits_for_month(year, month)
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

    def get_enrollments_in_month(self, year, month):
        """

        :param year:
        :param month:
        :return:
        """
        from ..dudes import DateToolsDude
        from .schedule_item_enrollment import ScheduleItemEnrollment

        date_dude = DateToolsDude()
        first_day_month = datetime.date(year, month, 1)
        last_day_month = date_dude.get_last_day_month(first_day_month)

        enrollments = ScheduleItemEnrollment.objects.filter(
            Q(account_subscription=self) &
            Q(date_start__lte=last_day_month) &
            (Q(date_end__gte=first_day_month) | Q(date_end__isnull=True))
        )

        return enrollments

    def find_enrolled_classes_in_month(self, year, month):
        """

        :return:
        """
        from graphql_relay import to_global_id

        from ..dudes import DateToolsDude
        from ..schema.schedule_class import ScheduleClassesDayType

        date_dude = DateToolsDude()
        enrollments = self.get_enrollments_in_month(year, month)

        first_day_month = datetime.date(year, month, 1)
        last_day_month = date_dude.get_last_day_month(first_day_month)

        classes_in_month = []
        date = first_day_month
        while date <= last_day_month:
            day = ScheduleClassesDayType()
            day.date = date
            day.attendance_count_type = 'ATTENDING_AND_BOOKED'
            day.classes = day.resolve_classes(None)

            if day.classes:
                for schedule_class_type in day.classes:
                    for enrollment in enrollments:
                        # Possible optimization; do this only once for each enrollment... but well...
                        # it's in the background
                        schedule_item_node_id = to_global_id('ScheduleItemNode', enrollment.schedule_item.id)

                        print("---")
                        print(date)
                        print(enrollment.date_start)
                        print(schedule_item_node_id)
                        print(schedule_class_type.schedule_item_id)

                        if (schedule_class_type.schedule_item_id == schedule_item_node_id
                            and date >= enrollment.date_start
                        ):
                            classes_in_month.append(schedule_class_type)
                            print("added class")
                        else:
                            print("Skipped class")

            date += datetime.timedelta(days=1)

        return classes_in_month

    def book_enrolled_classes_for_month(self, year, month):
        """

        :param year:
        :param month:
        :return:
        """
        from ..dudes import ClassCheckinDude, DateToolsDude
        from ..modules.gql_tools import get_rid
        from .schedule_item import ScheduleItem

        class_checkin_dude = ClassCheckinDude()
        date_dude = DateToolsDude()
        first_day_month = datetime.date(year, month, 1)
        last_day_month = date_dude.get_last_day_month(first_day_month)

        classes_in_month = self.find_enrolled_classes_in_month(year, month)
        for schedule_class_type in classes_in_month:
            rid = get_rid(schedule_class_type.schedule_item_id)
            schedule_item_id = rid.id
            schedule_item = ScheduleItem.objects.get(pk=schedule_item_id)

            # Try to book class, but continue on possible common errors, try to book as many as possible.
            try:
                class_checkin_dude.class_checkin_subscription(
                    account=self.account,
                    account_subscription=self,
                    schedule_item=schedule_item,
                    date=schedule_class_type.date,
                    online_booking=False,
                    booking_status="BOOKED"
                )
            except CSClassBookingSubscriptionBlockedError:
                pass
            except CSClassBookingSubscriptionPausedError:
                pass
            except CSClassBookingSubscriptionNoCreditsError:
                pass


    def cancel_booked_classes_after_enrollment_end(self, schedule_item_enrollment):
        """

        :param schedule_item_enrollment:
        :return:
        """
        from .schedule_item_attendance import ScheduleItemAttendance

        schedule_item = schedule_item_enrollment.schedule_item

        if schedule_item_enrollment.date_end:
            ScheduleItemAttendance.objects.filter(
                schedule_item=schedule_item,
                account_subscription=self,
                date__gte=schedule_item_enrollment.date_end
            ).update(booking_status='CANCELLED')

    def get_blocked_on_date(self, date):
        """

        :param date:
        :return:
        """
        from .account_subscription_block import AccountSubscriptionBlock

        qs = AccountSubscriptionBlock.objects.filter(
            Q(account_subscription=self) &
            Q(date_start__lte=date) &
            (Q(date_end__gte=date) | Q(date_end__isnull=True))
        )

        return qs.exists()

    def get_paused_on_date(self, date):
        """

        :param date:
        :return:
        """
        from .account_subscription_pause import AccountSubscriptionPause

        qs = AccountSubscriptionPause.objects.filter(
            Q(account_subscription=self) &
            Q(date_start__lte=date) &
            (Q(date_end__gte=date) | Q(date_end__isnull=True))
        )

        return qs.exists()

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

    def create_invoice_for_month(self, year, month, description="", invoice_date='today'):
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

        print("$$$$$$$$$$")
        print("Creating invoices for month")

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

        print("#### invoice items already found:")
        print(qs)

        if qs.exists():
            # An invoice item already exists for this month. Return the existing invoice item.
            print("already found")
            return qs.first()

        # Check if there are billable days in this month
        billable_period = self.get_billable_period_in_month(year, month)
        print(billable_period)

        if not billable_period['billable_days']:
            print("no billable days")
            return

        # Check if the account is active
        print(self.account.is_active)
        if not self.account.is_active:
            print("account_not_active")
            return

        # Fetch alt. price for this month (if any)
        qs = AccountSubscriptionAltPrice.objects.filter(
            account_subscription=self,
            subscription_year=year,
            subscription_month=month
        )

        print("alt price")
        print(qs)

        alt_price = None
        if qs.exists():
            alt_price = qs.first()
            if alt_price.amount == 0:
                print("alt price 0")
                # A 0 amount has been set in an alt. price. We don't need an invoice this month
                return

        # Check if a regular price is set
        subscription_price = self.organization_subscription.get_price_on_date(first_day_month,
                                                                              raw_price=True)
        if not subscription_price:
            print("subscription price 0")
            # No price is set, or the price is set to 0.
            return

        # Ok we've survived all checks, continue with invoice creation
        finance_invoice_group = FinanceInvoiceGroupDefault.objects.filter(
            item_type="SUBSCRIPTIONS"
        ).first().finance_invoice_group

        print(finance_invoice_group)

        # Check what to set as invoice date
        if invoice_date == 'first_of_month':
            date_created = datetime.date(int(year), int(month), 1)
        else:
            date_created = today_local

        print(date_created)

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
        print("invoice")
        print(finance_invoice)
        finance_invoice_item = finance_invoice.item_add_subscription(self, year, month, description=description)

        print("&&&")
        print(finance_invoice_item)

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
