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
    accounts = models.ManyToManyField(Account, through='FinanceInvoiceAccount', related_name='accounts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.invoice_number


    def save(self, *args, **kwargs):
        if self.pk is None: # We know this is object creation when there is no pk yet.
            # set dates
            self.date_sent = timezone.now().date()
            self.date_due = self.date_sent + datetime.timedelta(days=self.finance_invoice_group.due_after_days)
            # set invoice number
            self.invoice_number = self.finance_invoice_group.next_invoice_number()

            ## Increase next_id for invoice group
            # This code is here so the id is only +=1'd when an invoice is actually created 
            self.finance_invoice_group.next_id += 1
            self.finance_invoice_group.save()


        super(FinanceInvoice, self).save(*args, **kwargs)