from django.db import models
from sorl.thumbnail import ImageField

from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount
from .finance_tax_rate import FinanceTaxRate

from .helpers import model_string


class OrganizationProduct(models.Model):
    archived = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    image = ImageField(upload_to='organization_product', default=None)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.SET_NULL, null=True)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.SET_NULL, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return model_string(self)
