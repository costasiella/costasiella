from django.utils.translation import gettext as _
from django.db import models

from .business import Business
from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount

from .helpers import model_string


class FinanceExpense(models.Model):
    date = models.DateField()
    summary = models.CharField(max_length=255)
    description = models.TextField(default="")
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    tax = models.DecimalField(max_digits=20, decimal_places=2)
    percentage = models.DecimalField(max_digits=20, decimal_places=2, default=100)
    total = models.DecimalField(max_digits=20, decimal_places=2)
    supplier = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, related_name="supplier_expenses")
    # TODO: Add client field later.
    # Without client field: not billable
    # With client field: billable - option create invoice (bill expense)
    # client = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, related_name="client_expenses")
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.SET_NULL, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.SET_NULL, null=True)
    document = models.FileField(upload_to='finance_expense', default=None)

    def __str__(self):
        return model_string(self)

    def save(self, *args, **kwargs):
        self.total = self._calculate_total()

        super(FinanceExpense, self).save(*args, **kwargs)

    def _calculate_total(self):
        from ..dudes import FinanceDude
        finance_dude = FinanceDude()
        return finance_dude.calculate_total(
            subtotal=self.amount,
            tax=self.tax
        )
