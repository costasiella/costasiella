from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField

from .account import Account
from .finance_payment_batch import FinancePaymentBatch

from .helpers import model_string


class FinancePaymentBatchExport(models.Model):
    finance_payment_batch = models.ForeignKey(FinancePaymentBatch,
                                              on_delete=models.CASCADE,
                                              related_name="exports")
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, related_name="payment_batch_exports", null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return model_string(self)
