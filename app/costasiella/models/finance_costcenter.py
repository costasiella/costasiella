from django.utils.translation import gettext as _

from django.db import models

class FinanceCostCenter(models.Model):
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, default="", help_text=_("Cost center code in your accounting software."))

    def __str__(self):
        return self.name
    
