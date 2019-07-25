from django.utils.translation import gettext as _

from django.db import models

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
    account_company = models.CharField(max_length=255, default="")
    account_company_registration = models.CharField(max_length=255, default="")
    account_company_tax_registration = models.CharField(max_length=255, default="")
    account_contact_name = models.CharField(max_length=255, default="")
    account_address = models.CharField(max_length=255, default="")
    status = models.CharField(max_length=255, choices=STATUSES, default="DRAFT")
    summary = models.CharField(max_length=255, default="")
    invoice_number = models.CharField(max_length=255, default="") # Invoice #
    date_sent = models.DateField(auto_now_add=True)
    date_due = models.DateField()
    terms = models.TextField(default="")
    footer = models.TextField(default="")
    note = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.invoice_number
    