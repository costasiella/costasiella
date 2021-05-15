from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField
from .organization_location import OrganizationLocation
from .finance_payment_batch_category import FinancePaymentBatchCategory

from .helpers import model_string
from .choices.finance_payment_batch_statuses import get_finance_payment_batch_statuses
from .choices.finance_payment_batch_types import get_finance_payment_batch_types


class FinancePaymentBatch(models.Model):
    BATCH_TYPES = get_finance_payment_batch_types()
    STATUSES = get_finance_payment_batch_statuses()

    name = models.CharField(max_length=255)
    batch_type = models.CharField(max_length=255, choices=BATCH_TYPES)
    finance_payment_batch_category = models.ForeignKey(FinancePaymentBatchCategory, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=STATUSES, default="AWAITING_APPROVAL")
    description = models.CharField(max_length=255, null=False, default="")  # default bankstatement description
    year = models.IntegerField()
    month = models.IntegerField()
    execution_date = models.DateField()
    include_zero_amounts = models.BooleanField(default=False)
    organization_location = models.ForeignKey(OrganizationLocation, on_delete=models.CASCADE)
    note = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)
