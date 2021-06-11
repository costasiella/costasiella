from django.utils.translation import gettext as _
from django.utils import timezone

from django.db import models

from .finance_invoice import FinanceInvoice
from .finance_payment_method import FinancePaymentMethod

from .helpers import model_string


class FinanceInvoicePayment(models.Model):
    finance_invoice = models.ForeignKey(FinanceInvoice, on_delete=models.CASCADE, related_name="payments")
    date = models.DateField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    finance_payment_method = models.ForeignKey(FinancePaymentMethod, on_delete=models.CASCADE, null=True)
    note = models.TextField(default="")
    online_payment_id = models.TextField(null=True)
    online_refund_id = models.TextField(null=True)
    online_chargeback_id = models.TextField(null=True)

    def __str__(self):
        return model_string(self)
