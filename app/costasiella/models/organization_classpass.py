from django.utils.translation import gettext as _

from django.db import models

from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount
from .finance_taxrate import FinanceTaxRate
from .organization_membership import OrganizationMembership


class OrganizationClasspass(models.Model):
    VALIDITY_UNITS = (
        ("DAYS", _("Days")),
        ("WEEKS", _("Weeks")),
        ("MONTHS", _("Months"))
    )

    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    display_shop = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.CASCADE)
    validity = models.PositiveIntegerField()
    validity_unit = models.CharField(max_length=10, choices=VALIDITY_UNITS, default="DAYS")
    classes = models.PositiveSmallIntegerField()
    unlimited = models.BooleanField(default=False)
    organization_membership = models.ForeignKey(OrganizationMembership, on_delete=models.CASCADE, null=True)
    quick_stats_amount = models.DecimalField(max_digits=10, decimal_places=2)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.CASCADE, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name
    
