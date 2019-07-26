from django.utils.translation import gettext as _

from django.db import models

from .finance_invoice import FinanceInvoice


class FinanceInvoiceAmount(models.Model):
    finance_invoice = models.ForeignKey(FinanceInvoice, on_delete=models.CASCADE)
    sub_total = models.DecimalField(max_digits=20, decimal_places=2)
    vat = models.DecimalField(max_digits=20, decimal_places=2)
    total = models.DecimalField(max_digits=20, decimal_places=2)
    paid = models.DecimalField(max_digits=20, decimal_places=2)
    balance = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.finance_invoice.invoice_number + " " + _("amounts")
    