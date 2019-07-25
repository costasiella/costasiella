from django.utils.translation import gettext as _

from django.db import models

class FinanceInvoiceGroup(models.Model):
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255, unique=True)
    next_id = models.PositiveIntegerField(default=1)
    due_after_days = models.PositiveSmallIntegerField(default=30)
    prefix = models.CharField(max_length=255, default="INV")
    prefix_year = models.BooleanField(default=True)
    auto_reset_prefix_year = models.BooleanField(default=True)
    terms = models.TextField(default="")
    footer = models.TextField(default="")
    code = models.CharField(max_length=255, default="", help_text=_("Journal code in your accounting software."))

    def __str__(self):
        return self.name
    