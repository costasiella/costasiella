from django.utils.translation import gettext as _
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField

from .finance_invoice import FinanceInvoice
from .finance_order import FinanceOrder

class IntegrationLogMollie(models.Model):
    # add additional fields in here

    mollie_payment_id = models.CharField(max_length=255)
    recurring_type = models.CharField(max_length=255, null=True)
    webhook_url = models.TextField()
    finance_invoice = models.ForeignKey(FinanceInvoice, on_delete=models.CASCADE, null=True)
    finance_order = models.ForeignKey(FinanceOrder, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return "mollie payment: " + self.mollie_payment_id

    # def save(self, *args, **kwargs):
    #     name = [self.first_name, self.last_name]
    #     self.full_name = " ".join(name)
    #     super(Account, self).save(*args, **kwargs)