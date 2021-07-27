from django.utils.translation import gettext as _
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField

from .finance_invoice import FinanceInvoice
from .finance_order import FinanceOrder


class IntegrationLogMollie(models.Model):
    # add additional fields in here
    LOG_SOURCES = (
        ('ORDER_PAY', _("Order pay")),
        ('INVOICE_PAY', _("Invoice pay")),
        ('WEBHOOK', _("Webhook")),
    )

    RECURRING_TYPES = (
        ("FIRST", _("First")),
        ('RECURRING', _("Recurring"))
    )

    log_source = models.CharField(max_length=255, choices=LOG_SOURCES)
    mollie_payment_id = models.CharField(max_length=255)
    recurring_type = models.CharField(max_length=255, choices=RECURRING_TYPES, null=True)
    webhook_url = models.TextField(null=True)
    finance_invoice = models.ForeignKey(FinanceInvoice, on_delete=models.CASCADE, null=True)
    finance_order = models.ForeignKey(FinanceOrder, on_delete=models.CASCADE, null=True)
    payment_data = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "mollie payment: " + self.mollie_payment_id
