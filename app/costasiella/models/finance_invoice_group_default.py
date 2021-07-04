from django.utils.translation import gettext as _
from django.utils import timezone

from django.db import models
from .finance_invoice_group import FinanceInvoiceGroup


class FinanceInvoiceGroupDefault(models.Model):
    item_type = models.CharField(max_length=255, default="")
    finance_invoice_group = models.ForeignKey(FinanceInvoiceGroup, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.item_type + ' - ' + self.finance_invoice_group.name
