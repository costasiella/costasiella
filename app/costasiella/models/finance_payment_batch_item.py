from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField
# from .organization_location import OrganizationLocation

from .account import Account
from .account_subscription import AccountSubscription
from .finance_invoice import FinanceInvoice
from .finance_payment_batch import FinancePaymentBatch

from .helpers import model_string

from ..modules.encrypted_fields import EncryptedTextField


class FinancePaymentBatchItem(models.Model):
    finance_payment_batch = models.ForeignKey(FinancePaymentBatch,
                                              on_delete=models.CASCADE,
                                              related_name="items")
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, related_name="payment_batch_items", null=True)
    # account_subscription = models.ForeignKey(AccountSubscription, on_delete=models.SET_NULL, null=True)
    finance_invoice = models.ForeignKey(FinanceInvoice, on_delete=models.CASCADE, null=True)
    account_holder = EncryptedTextField(default="")
    account_number = EncryptedTextField(default="")
    account_bic = EncryptedTextField(default="")
    mandate_signature_date = models.DateField(null=True)
    mandate_reference = EncryptedTextField(default="")
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=255, default="")
    description = EncryptedTextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return model_string(self)
