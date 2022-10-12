from django.utils.translation import gettext as _
from django.utils import timezone
import datetime

from django.db import models

from .account import Account
from .business import Business
from .finance_quote_group import FinanceQuoteGroup

from .helpers import model_string

now = timezone.now()


class FinanceQuote(models.Model):
    STATUSES = (
        ('DRAFT', _("Draft")),
        ('SENT', _("Sent")),
        ('ACCEPTED', _("Accepted")),
        ('REJECTED', _("Rejected")),
        ('CANCELLED', _("Cancelled")),
    )

    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="quotes")
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, related_name="quotes")
    finance_quote_group = models.ForeignKey(FinanceQuoteGroup, on_delete=models.CASCADE)
    # custom_to is used to control whether to copy relation info from an account or business, or not.
    custom_to = models.BooleanField(default=False)
    relation_company = models.CharField(max_length=255, default="")
    relation_company_registration = models.CharField(max_length=255, default="")
    relation_company_tax_registration = models.CharField(max_length=255, default="")
    relation_contact_name = models.CharField(max_length=255, default="")
    relation_address = models.CharField(max_length=255, default="")
    relation_postcode = models.CharField(max_length=255, default="")
    relation_city = models.CharField(max_length=255, default="")
    relation_country = models.CharField(max_length=255, default="")
    status = models.CharField(max_length=255, choices=STATUSES, default="DRAFT")
    summary = models.CharField(max_length=255, default="")
    quote_number = models.CharField(max_length=255, default="")  # Invoice #
    date_sent = models.DateField()
    date_expire = models.DateField()
    terms = models.TextField(default="")
    footer = models.TextField(default="")
    note = models.TextField(default="")
    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)

    def set_relation_info(self):
        """ Set relation info from linked account or business, when not custom_to """
        if not self.custom_to:
            self.relation_company = ""
            self.relation_company_registration = ""
            self.relation_company_tax_registration = ""

            if self.account:
                # Set account info by default
                self.relation_contact_name = self.account.full_name
                self.relation_address = self.account.address
                self.relation_postcode = self.account.postcode
                self.relation_city = self.account.city
                self.relation_country = self.account.country

            # Set default business from account on creation only (not self.id), if no other business has been set
            if self.account.invoice_to_business and not self.id and not self.business:
                # Set default business for account
                self.business = self.account.invoice_to_business

            if self.business:
                self.relation_company = self.business.name
                self.relation_company_registration = self.business.registration
                self.relation_company_tax_registration = self.business.tax_registration
                # Use business address fields
                self.relation_contact_name = ""
                self.relation_address = self.business.address
                self.relation_postcode = self.business.postcode
                self.relation_city = self.business.city
                self.relation_country = self.business.country

    def update_amounts(self):
        """ Update total amounts fields (subtotal, tax, total, paid, balance) """
        # Get totals from quote items
        from .finance_quote_item import FinanceQuoteItem
        from django.db.models import Sum
        sums = FinanceQuoteItem.objects.filter(finance_quote=self).aggregate(
            Sum('subtotal'), Sum('tax'), Sum('total')
        )

        self.subtotal = sums['subtotal__sum'] or 0
        self.tax = sums['tax__sum'] or 0
        self.total = sums['total__sum'] or 0

        self.save(update_fields=[
            "subtotal",
            "tax",
            "total",
        ])

    def _first_quote_in_group_this_year(self, year):
        """
        This quote has to be the first in the group this year if no other
        quotes are found in this group in this year
        """
        year_start = datetime.date(year, 1, 1)
        year_end = datetime.date(year, 12, 31)

        return not FinanceQuote.objects.filter(
            date_sent__gte=year_start,
            date_sent__lte=year_end,
            finance_quote_group=self.finance_quote_group
        ).exists()

    def _increment_group_next_id(self):
        # This code is here so the id is only +=1'd when an quote is actually created
        self.finance_quote_group.next_id += 1
        self.finance_quote_group.save()

    def save(self, *args, **kwargs):
        if self.pk is None:  # We know this is object creation when there is no pk / id yet.
            # Get relation info
            self.set_relation_info()

            # set dates
            if not self.date_sent:
                # Date is now if not supplied on creation
                self.date_sent = timezone.now().date()
            self.date_expire = self.date_sent + datetime.timedelta(days=self.finance_quote_group.expires_after_days)

            # set quote number
            # Check if this is the first invoice in this group
            # (Needed to check if we should reset the numbering for this year)
            year = self.date_sent.year
            first_quote_in_group_this_year = self._first_quote_in_group_this_year(year)
            self.quote_number = self.finance_quote_group.next_quote_number(
                year,
                first_quote_this_year=first_quote_in_group_this_year
            )

            # Increase next_id for invoice group
            self._increment_group_next_id()

        super(FinanceQuote, self).save(*args, **kwargs)

    def _get_item_next_line_nr(self):
        """
        Returns the next item number for a quote
        use to set sorting when adding an item
        """
        from .finance_quote_item import FinanceQuoteItem

        qs = FinanceQuoteItem.objects.filter(finance_quote=self)

        return qs.count()

    def tax_rates_amounts(self, formatted=False):
        """
        Returns tax for each tax rate as list sorted by tax rate percentage
        format: [ [ tax_rate_obj, sum ] ]
        """
        from django.db.models import Sum
        from .finance_tax_rate import FinanceTaxRate

        amounts_tax = []

        tax_rates = FinanceTaxRate.objects.filter(
            quote_items__finance_quote=self,
        ).annotate(quote_amount=Sum("quote_items__tax"))

        # print(tax_rates)

        # for t in tax_rates:
        #     print(t.name)
        #     print(t.rate_type)
        #     print(t.invoice_amount)

        return tax_rates

    def cancel(self):
        """
        Set status to cancelled
        :return:
        """
        self.status = "CANCELLED"
        self.save()
