from django.utils.translation import gettext as _
from django.db import models


class FinanceTaxRate(models.Model):
    IN_OR_EX = (
        ("IN", _("Inclusive")),
        ("EX", _("Exclusive"))
    )

    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    percentage = models.DecimalField(max_digits=20, decimal_places=2)
    rate_type = models.CharField(max_length=2, choices=IN_OR_EX, default="IN")
    code = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name
