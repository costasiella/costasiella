from django.db import models

from .finance_invoice import FinanceInvoice
from .account import Account

class FinanceInvoiceAccount(models.Model):
    finance_invoice = models.ForeignKey(FinanceInvoice, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return self.finance_invoice.invoice_number + ' ' + self.account.full_name
    
