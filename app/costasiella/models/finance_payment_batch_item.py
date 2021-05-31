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
from .choices.finance_payment_batch_statuses import get_finance_payment_batch_statuses
from .choices.finance_payment_batch_types import get_finance_payment_batch_types

from ..modules.encrypted_fields import EncryptedTextField


class FinancePaymentBatchItem(models.Model):
    # BATCH_TYPES = get_finance_payment_batch_types()
    # STATUSES = get_finance_payment_batch_statuses()
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
    mandate_reference = models.DateField(null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=255, default="")
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return model_string(self)
