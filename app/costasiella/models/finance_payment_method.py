from django.utils.translation import gettext as _

from django.db import models


class FinancePaymentMethod(models.Model):
    archived = models.BooleanField(default=False)
    system_method = models.BooleanField(editable=False, default=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, default="", help_text=_("Payment method/condition code in your accounting software."))

    def __str__(self):
        return self.name
    
