from django.utils.translation import gettext as _
from django.utils import timezone

from django.db import models

from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount
from .finance_quote import FinanceQuote
from .finance_tax_rate import FinanceTaxRate

from .helpers import model_string


class FinanceQuoteItem(models.Model):
    finance_quote = models.ForeignKey(FinanceQuote, on_delete=models.CASCADE, related_name="items")
    line_number = models.PositiveSmallIntegerField(default=0)
    product_name = models.CharField(max_length=255)
    description = models.TextField(default="")
    quantity = models.DecimalField(max_digits=20, decimal_places=2)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    finance_tax_rate = models.ForeignKey(FinanceTaxRate,
                                         on_delete=models.SET_NULL,
                                         null=True,
                                         related_name="quote_items")
    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.SET_NULL, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ("finance_quote", "line_number",)

    def __str__(self):
        return model_string(self)

    def save(self, *args, **kwargs):
        self.subtotal = self._calculate_subtotal()
        self.tax = self._calculate_tax()
        self.total = self._calculate_total()

        super(FinanceQuoteItem, self).save(*args, **kwargs)
    
    def _calculate_subtotal(self):
        from ..dudes import FinanceDude
        finance_dude = FinanceDude()
        return finance_dude.calculate_subtotal(
            price=self.price,
            quantity=self.quantity,
            finance_tax_rate=self.finance_tax_rate
        )

    def _calculate_tax(self):
        from ..dudes import FinanceDude
        finance_dude = FinanceDude()
        return finance_dude.calculate_tax(
            subtotal=self.subtotal,
            finance_tax_rate=self.finance_tax_rate
        )

    def _calculate_total(self):
        from ..dudes import FinanceDude
        finance_dude = FinanceDude()
        return finance_dude.calculate_total(
            subtotal=self.subtotal,
            tax=self.tax
        )

