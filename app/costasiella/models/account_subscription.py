import datetime
import calendar
import logging
import math
from collections import namedtuple

from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models
from django.db.models import Q

from .account import Account
from .organization_subscription import OrganizationSubscription
from .finance_payment_method import FinancePaymentMethod

from ..modules.cs_errors import \
    CSClassDoesNotTakePlaceOnDateError, \
    CSClassFullyBookedError, \
    CSClassBookingSubscriptionAlreadyBookedError, \
    CSClassBookingSubscriptionBlockedError, \
    CSClassBookingSubscriptionPausedError, \
    CSClassBookingSubscriptionNoCreditsError, \
    CSSubscriptionNotValidOnDateError

logger = logging.getLogger(__name__)


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
        billable_days = billable_period['billable_days']

        percent = float(billable_days) / float(total_days.days)
        classes = self.organization_subscription.classes
        if self.organization_subscription.subscription_unit == 'MONTH':
            credits_to_add = math.ceil(classes * percent)
        else:
            credits = 0
            if classes == 1:
                # 1 * 53 = 53
                # one day / week = 55 credits / year
                # 7 long months = 7 * 5 = 35
                # 5 shorter months = 5 * 4 = 20
                last_day_of_month = calendar.monthrange(year, month)[1]
                if last_day_of_month == 31:
                    credits = 5
                else:
                    credits = 4
            elif classes == 2:
                # 53 * 2 = 106 || 12 * 9 = 108
                credits = 9
            elif classes == 3:
                # 53 * 3 = 159 || 12 * 14 = 168
                credits = 14
            elif classes == 4:
                # 53 * 4 = 212 || 12 * 18 = 216
                credits = 18
            elif classes == 5:
                # One credit short here, but it's the closest
                # 53 * 5 = 265 || 12 * 22 = 264
                credits = 22
            elif classes == 6:
                # 53 * 6 = 318 || 12 * 27 = 324
                credits = 27

            credits_to_add = math.ceil(credits * percent)

        return credits_to_add

    def create_credits_for_month(self, year, month):
        """
        Add subscription credits for a given month
        :param year: int
        :param month: int
        :return: Number of credits added
        """
        from .account_subscription_credit import AccountSubscriptionCredit

        now = timezone.now()
        credit_validity_in_days = self.organization_subscription.credit_validity or 31
        expiration = now.date() + datetime.timedelta(days=credit_validity_in_days)

        number_of_credits_to_add = self._calculate_credits_for_month(year, month)

        # Link credits to advance credits first
        unreconcilded_advance_credits = AccountSubscriptionCredit.objects.filter(
            advance=True,
            reconciled__isnull=True,
            account_subscription=self,
        )

        count_unreconciled_advance_credits = unreconcilded_advance_credits.count()
        unreconcilded_advance_credits.update(reconciled=now)

        # Then give the remaining ones.
        remaining_credits_to_add = number_of_credits_to_add - count_unreconciled_advance_credits
        for i in range(0, remaining_credits_to_add):
            account_subscription_credit = AccountSubscriptionCredit(
                account_subscription=self,
                expiration=expiration,
                description=_("Credit %s-%s") % (year, month),
                subscription_year=year,
                subscription_month=month,
            )
            account_subscription_credit.save()

        return number_of_credits_to_add

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

    #TODO: Refactor this to accept a start & end date for more flexibility?
    # eg. class bookings up to x days into the future?
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

                        if (schedule_class_type.schedule_item_id == schedule_item_node_id
                            and date >= enrollment.date_start
                        ):
                            classes_in_month.append(schedule_class_type)

            date += datetime.timedelta(days=1)

        return classes_in_month

    def book_enrolled_classes_for_month(self, year, month):
        """

        :param year:
        :param month:
        :return:
        """
        from ..dudes import ClassCheckinDude, DateToolsDude
        from ..modules.model_helpers.schedule_item_helper import ScheduleItemHelper
        from ..modules.gql_tools import get_rid
        from .schedule_item import ScheduleItem

        sih = ScheduleItemHelper()
        class_checkin_dude = ClassCheckinDude()
        date_dude = DateToolsDude()
        first_day_month = datetime.date(year, month, 1)
        last_day_month = date_dude.get_last_day_month(first_day_month)

        classes_in_month = self.find_enrolled_classes_in_month(year, month)
        for schedule_class_type in classes_in_month:
            rid = get_rid(schedule_class_type.schedule_item_id)
            schedule_item_id = rid.id
            schedule_item = ScheduleItem.objects.get(pk=schedule_item_id)

            subscription_name = self.organization_subscription.name
            str_date = str(schedule_class_type.date)
            schedule_item_with_otc_data = sih.schedule_item_with_otc_and_holiday_data(
                schedule_item, schedule_class_type.date
            )

            schedule_item_string = f"{str_date} \
{schedule_item_with_otc_data.organization_location_room.organization_location.name} \
{schedule_item_with_otc_data.organization_classtype.name} \
{str(schedule_item_with_otc_data.time_start)}"

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
            except CSClassDoesNotTakePlaceOnDateError:
                logger.warning(
                    _(f"Enrollment class {schedule_item_string} not booked for {self.account.email} \
- This class doesn't take place on {schedule_class_type.date}"))
            except CSClassFullyBookedError:
                logger.warning(
                    _(f"Enrollment class {schedule_item_string} not booked for {self.account.email} \
- This class is full on {schedule_class_type.date}"))
            except CSClassBookingSubscriptionAlreadyBookedError:
                logger.warning(_(f"Enrollment class {schedule_item_string} not booked for {self.account.email} \
- Already booked class on {schedule_class_type.date}"))
            except CSClassBookingSubscriptionBlockedError:
                logger.warning(_(f"Enrollment class {schedule_item_string} not booked for {self.account.email} \
- Subscription is blocked on {schedule_class_type.date}"))
            except CSClassBookingSubscriptionPausedError:
                logger.warning(_(f"Enrollment class {schedule_item_string} not booked for {self.account.email} \
- Subscription is paused on {schedule_class_type.date}"))
            except CSClassBookingSubscriptionNoCreditsError:
                logger.warning(_(f"Enrollment class {schedule_item_string} not booked for {self.account.email} \
- No credits available on {schedule_class_type.date}"))
            except CSSubscriptionNotValidOnDateError:
                logger.warning(_(f"Enrollment class {schedule_item_string} not booked for {self.account.email} \
- Subscription is not valid on {schedule_class_type.date}"))

    def cancel_booked_classes_after_enrollment_end(self,
           schedule_item,
           cancel_bookings_from_date
       ):
        """

        :param schedule_item_enrollment:
        :return:
        """
        from .schedule_item_attendance import ScheduleItemAttendance

        # Find attendance on this subscription after the end date
        schedule_item_attendances = ScheduleItemAttendance.objects.filter(
            schedule_item=schedule_item,
            account_subscription=self,
            date__gte=cancel_bookings_from_date
        )

        # Cancel attendance & refund credits
        for schedule_item_attendance in schedule_item_attendances:
            schedule_item_attendance.cancel()

        logger.info("Enrollment ended: cancelled classes booked after %s on subscription %s" %
                    (cancel_bookings_from_date, self.id))

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

    def get_next_credit(self, date):
        """
        This function has to take a date, otherwise it doesn't work for past classes.
        For past classes an expired credit that hasn't been used, might be valid.
        :return:
        """
        from .account_subscription_credit import AccountSubscriptionCredit

        available_credits = AccountSubscriptionCredit.objects.filter(
            mutation_type="SINGLE",
            account_subscription=self,
            expiration__gte=date,
            schedule_item_attendance__isnull=True
        ).order_by('created_at', 'id')

        return available_credits.first()

    def get_credits_total(self, date):
        """
        Get credit records with expiration >= date, that haven't been used yet (no schedule item attendance)
        :return: Float
        """
        from .account_subscription_credit import AccountSubscriptionCredit

        qs = AccountSubscriptionCredit.objects.filter(
            mutation_type="SINGLE",
            account_subscription=self,
            expiration__gte=date,
            schedule_item_attendance__isnull=True
        )

        return qs.count()

    def get_unreconciled_credits_total(self, date):
        """
        Get unreconciled credit records with expiration >= date, that haven't been used yet
        (no schedule item attendance)
        :return:
        """
        from .account_subscription_credit import AccountSubscriptionCredit

        qs = AccountSubscriptionCredit.objects.filter(
            mutation_type="SINGLE",
            account_subscription=self,
            advance=True,
            reconciled=None
        )

        return qs.count()

    def get_usable_reconcile_later_credits(self, date):
        # Get credit records with expiration >= today, that haven't been used yet (no schedule item attendance)
        count_unreconciled_credits = self.get_unreconciled_credits_total(date)

        usable_reconciliation_credits = \
            self.organization_subscription.reconciliation_classes - count_unreconciled_credits

        # This function shouldn't return 0, knowing if there any usable classes is enough
        # Returning negative integers can confuse other credit calculations.
        return usable_reconciliation_credits if usable_reconciliation_credits >= 0 else 0

    def get_usable_credits_total(self, date):
        """
        Get total credits and add reconciliation credits from subscription (if any)
        :return: Float
        """
        credits_total = self.get_credits_total(date)
        usable_reconciliation_credits = self.get_usable_reconcile_later_credits(date)

        if self.organization_subscription.reconciliation_classes:
            return_value = credits_total + usable_reconciliation_credits
        else:
            return_value = credits_total

        return return_value

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
            Q(mutation_type='SINGLE')
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

        # Check what to set as invoice date
        if invoice_date == 'first_of_month':
            date_created = datetime.date(int(year), int(month), 1)
        else:
            date_created = today_local

        finance_invoice = FinanceInvoice(
            finance_payment_method=self.finance_payment_method,
            account=self.account,
            finance_invoice_group=finance_invoice_group,
            status='SENT',
            summary=_("Subscription invoice %s-%s") % (year, month),
            date_sent=date_created,
            terms=finance_invoice_group.terms,
            footer=finance_invoice_group.footer
        )
        finance_invoice.save()
        finance_invoice_item = finance_invoice.item_add_subscription(self, year, month, description=description)

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
