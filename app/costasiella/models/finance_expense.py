from django.utils.translation import gettext as _
from django.db import models
from django.conf import settings

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
    # total holds amount + tax
    subtotal = models.DecimalField(max_digits=20, decimal_places=2)
    percentage = models.DecimalField(max_digits=20, decimal_places=2, default=100)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    total_tax = models.DecimalField(max_digits=20, decimal_places=2)
    # Total holds amount + tax
    total = models.DecimalField(max_digits=20, decimal_places=2)
    supplier = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, related_name="supplier_expenses")
    # TODO: Add client field later.
    # Without client field: not billable
    # With client field: billable - option create invoice (bill expense)
    # When adding, also add it to the dude's duplicate method
    # client = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, related_name="client_expenses")
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.SET_NULL, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.SET_NULL, null=True)
    document = models.FileField(upload_to='finance_expense', default=None, storage=settings.MEDIA_PROTECTED_STORAGE)

    def __str__(self):
        return model_string(self)

    def save(self, *args, **kwargs):
        self.subtotal = self._calculate_subtotal()
        self.total_amount = self._calculate_percentage(self.amount)
        self.total_tax = self._calculate_percentage(self.tax)
        self.total = self._calculate_percentage(self.subtotal)

        super(FinanceExpense, self).save(*args, **kwargs)

    def _calculate_subtotal(self):
        from ..dudes import FinanceDude
        finance_dude = FinanceDude()
        return finance_dude.calculate_total(
            subtotal=self.amount,
            tax=self.tax
        )

    def _calculate_percentage(self, value):
        if self.percentage:
            return value * (self.percentage / 100)
        else:
            return value
