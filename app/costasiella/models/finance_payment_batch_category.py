from django.utils.translation import gettext as _
from django.db import models

from .helpers import model_string


class FinancePaymentBatchCategory(models.Model):
    BATCH_CATEGORY_TYPES = (
        ('COLLECTION', _("Collection")),
        ('PAYMENT', _("Payment")),
    )

    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    batch_category_type = models.CharField(max_length=255, choices=BATCH_CATEGORY_TYPES)
    description = models.CharField(max_length=255, null=False, default="")  # default bankstatement description

    def __str__(self):
        return model_string(self)
