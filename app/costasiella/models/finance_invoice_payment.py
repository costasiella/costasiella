from django.utils.translation import gettext as _
from django.utils import timezone

from django.db import models

from .finance_invoice import FinanceInvoice
from .finance_tax_rate import FinanceTaxRate
from .finance_payment_method import FinancePaymentMethod

class FinanceInvoicePayment(models.Model):
    finance_invoice = models.ForeignKey(FinanceInvoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()
    finance_payment_method = models.ForeignKey(FinancePaymentMethod, on_delete=models.CASCADE, null=True)
    note = models.TextField(default="")


    def __str__(self):
        return self.finance_invoice.invoice_number + " payment: " + self.date + " " + self.amount
