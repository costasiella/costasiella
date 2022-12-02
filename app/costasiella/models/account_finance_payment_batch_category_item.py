from django.db import models

from .account import Account
from .finance_payment_batch_category import FinancePaymentBatchCategory

from .helpers import model_string
from ..modules.encrypted_fields import EncryptedTextField


class AccountFinancePaymentBatchCategoryItem(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="payment_batch_category_items")
    finance_payment_batch_category = models.ForeignKey(
        FinancePaymentBatchCategory, on_delete=models.CASCADE, null=True)
    year = models.IntegerField()
    month = models.IntegerField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return model_string(self)
