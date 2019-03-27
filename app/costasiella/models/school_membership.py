import uuid

from django.db import models

from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount
from .finance_taxrate import FinanceTaxRate
# Create your models here.

class SchoolMembership(models.Model):
    archived = models.BooleanField(default=False)
    display_public = models.BooleanField(default=True)
    trial_card = models.BooleanField(default=False)
    trial_times = models.IntegerField(default=1)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.CASCADE)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.CASCADE)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
