import datetime
from decimal import Decimal

from django.utils.translation import gettext as _
from django.utils import timezone
from django.db.models import Q

from django.db import models

from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount
from .finance_tax_rate import FinanceTaxRate
from .organization_membership import OrganizationMembership

from ..modules.finance_tools import display_float_as_amount


class OrganizationSubscription(models.Model):
    SUBSCRIPTION_UNITS = (
        ("WEEK", _("Week")),
        ("MONTH", _("Month"))
    )

    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    display_shop = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)
    min_duration = models.PositiveIntegerField()
    classes = models.PositiveIntegerField()
    subscription_unit = models.CharField(max_length=10, choices=SUBSCRIPTION_UNITS, default="WEEK")
    reconciliation_classes = models.PositiveSmallIntegerField(default=0)
    credit_validity = models.PositiveIntegerField(default=31)
    unlimited = models.BooleanField(default=False)
    terms_and_conditions = models.TextField()
    registration_fee = models.DecimalField(max_digits=20, decimal_places=2)
    organization_membership = models.ForeignKey(OrganizationMembership, on_delete=models.SET_NULL, null=True)
    quick_stats_amount = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.SET_NULL, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.SET_NULL, null=True)

    def get_price_on_date(self, date, raw_price=False, display=False):
        """
        :param date: datetime.date
        :param raw_price: Boolean - use to send price without VAT calculation to other functions
        :param display: Format returned value as string with currency symbol
        :return: Price (str or int)
        """
        query_set = self.organizationsubscriptionprice_set.filter(
            Q(date_start__lte=date) &
            (Q(date_end__gte=date) | Q(date_end__isnull=True))
        )

        if query_set.exists():
            subscription_price = query_set.first()
            price = subscription_price.price

            if raw_price:
                return price

            if subscription_price.finance_tax_rate:
                finance_tax_rate = subscription_price.finance_tax_rate
                if finance_tax_rate.rate_type == "EX":
                    percentage = (finance_tax_rate.percentage / 100)
                    price = round(float(price) * float(1 + percentage), 2)
                    # No need to do anything for included tax rates here, a user will see the correct price

            if display:
                return display_float_as_amount(price)
            else:
                return price
        else:
            return None

    def get_price_first_month(self, date, display=False):
        """
        Return the price for the first month, looking from date.
        :param date: datetime.date
        :param display: Format returned value as string with currency symbol
        :return: Price (str or int)
        """
        from ..dudes import DateToolsDude

        date_tools_dude = DateToolsDude()

        # today = timezone.now().date()
        first_day_month = datetime.date(date.year, date.month, 1)
        last_day_month = date_tools_dude.get_last_day_month(first_day_month)
        month_days = (last_day_month - first_day_month).days + 1
        billable_days = month_days - date.day + 1

        subscription_price = self.get_price_on_date(date)
        if subscription_price:
            price_first_month = round(((float(billable_days) / float(month_days)) * float(subscription_price)), 2)

            if display:
                return display_float_as_amount(price_first_month)
            else:
                return price_first_month
        else:
            return None

    def get_finance_tax_rate_on_date(self, date, display=False):
        query_set = self.organizationsubscriptionprice_set.filter(
            Q(date_start__lte=date) &
            (Q(date_end__gte=date) | Q(date_end__isnull=True))
        )

        if query_set.exists():
            finance_tax_rate = query_set.first().finance_tax_rate
            if display:
                return finance_tax_rate.name
            else:
                return finance_tax_rate
        else:
            return None

    def __str__(self):
        field_values = ["OrganizationSubscription:", "--------"]
        for field in self._meta.get_fields():
            field_values.append(": ".join([field.name, str(getattr(self, field.name, ''))]))
            # field_values.append(str(getattr(self, field.name, '')))
        field_values.append("--------")
        return '\n'.join(field_values)

    def get_account_registration_fee(self, account):
        """
        Return registration fee for account if not yet paid, else 0
        :param account: Account object
        :return: amount of registration fee to be paid
        """
        account_registration_fee = Decimal(0)
        if self.registration_fee and not account.has_paid_subscription_registration_fee():
            account_registration_fee = self.registration_fee

        return account_registration_fee
