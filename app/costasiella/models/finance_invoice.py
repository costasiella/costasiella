from django.utils.translation import gettext as _
from django.utils import timezone
import datetime

now = timezone.now()

from django.db import models

from .account import Account
from .finance_invoice_group import FinanceInvoiceGroup
from .finance_payment_method import FinancePaymentMethod


class FinanceInvoice(models.Model):
    STATUSES = (
        ('DRAFT', _("Draft")),
        ('SENT', _("Sent")),
        ('PAID', _("Paid")),
        ('CANCELLED', _("Cancelled"))
    )

    accounts = models.ManyToManyField(Account, through='FinanceInvoiceAccount', related_name='accounts')
    finance_invoice_group = models.ForeignKey(FinanceInvoiceGroup, on_delete=models.CASCADE)
    finance_payment_method = models.ForeignKey(FinancePaymentMethod, on_delete=models.CASCADE, null=True)
    teacher_payment = models.BooleanField(default=False)
    employee_claim = models.BooleanField(default=False)
    relation_company = models.CharField(max_length=255, default="")
    relation_company_registration = models.CharField(max_length=255, default="")
    relation_company_tax_registration = models.CharField(max_length=255, default="")
    relation_contact_name = models.CharField(max_length=255, default="")
    relation_address = models.CharField(max_length=255, default="")
    status = models.CharField(max_length=255, choices=STATUSES, default="DRAFT")
    summary = models.CharField(max_length=255, default="")
    invoice_number = models.CharField(max_length=255, default="") # Invoice #
    date_sent = models.DateField()
    date_due = models.DateField()
    terms = models.TextField(default="")
    footer = models.TextField(default="")
    note = models.TextField(default="")
    sub_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    vat = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.invoice_number

    def set_relation_info(self):
        """ Set relation info from linked account """
        pass

    def _first_invoice_in_group_this_year(self, year): 
        """
        This invoice has to be the first in the group this year if no other 
        invoices are found in this group in this year
        """
        year_start = datetime.date(year, 1, 1)
        year_end = datetime.date(year, 12, 31)

        return not FinanceInvoice.objects.filter(
            date_sent__gte = year_start,
            date_sent__lte = year_end,
            finance_invoice_group = self.finance_invoice_group
        ).exists()  

    def _increment_group_next_id(self):
        # This code is here so the id is only +=1'd when an invoice is actually created 
        self.finance_invoice_group.next_id += 1
        self.finance_invoice_group.save()

    def save(self, *args, **kwargs):
        if self.pk is None: # We know this is object creation when there is no pk yet.
            # set dates
            self.date_sent = timezone.now().date()
            self.date_due = self.date_sent + datetime.timedelta(days=self.finance_invoice_group.due_after_days)
            
            ## set invoice number
            # Check if this is the first invoice in this group
            # (Needed to check if we should reset the numbering for this year)
            year = self.date_sent.year
            first_invoice_in_group_this_year = self._first_invoice_in_group_this_year(year)
            self.invoice_number = self.finance_invoice_group.next_invoice_number(
                year, 
                first_invoice_this_year = first_invoice_in_group_this_year
            )

            ## Increase next_id for invoice group
            self._increment_group_next_id()

        super(FinanceInvoice, self).save(*args, **kwargs)