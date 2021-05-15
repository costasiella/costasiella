from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField
from .organization_location import OrganizationLocation
from .finance_payment_batch_category import FinancePaymentBatchCategory

from .helpers import model_string


class FinancePaymentBatch(models.Model):
    BATCH_TYPES = (
        ('COLLECTION', _("Collection")),
        ('PAYMENT', _("Payment")),
    )

    STATUSES = (
        ('SENT_TO_BANK', _("Sent to Bank")),
        ('APPROVED', _("Approved")),
        ('AWAITING_APPROVAL', _("Awaiting approval")),
        ('REJECTED', _("Rejected")),
    )

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
