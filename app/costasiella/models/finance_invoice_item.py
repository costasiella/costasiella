from django.utils.translation import gettext as _
from django.utils import timezone

from django.db import models

from .account_classpass import AccountClasspass
from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount
from .finance_invoice import FinanceInvoice
from .finance_tax_rate import FinanceTaxRate


class FinanceInvoiceItem(models.Model):
    finance_invoice = models.ForeignKey(FinanceInvoice, on_delete=models.CASCADE, related_name="items")
    account_classpass = models.ForeignKey(AccountClasspass,
                                          on_delete=models.SET_NULL,
                                          null=True,
                                          default=None,
                                          related_name="invoice_items")
    line_number = models.PositiveSmallIntegerField(default=0)
    product_name = models.CharField(max_length=255)
    description = models.TextField(default="")
    quantity = models.DecimalField(max_digits=20, decimal_places=2)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.CASCADE, null=True)
    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.CASCADE, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ("finance_invoice", "line_number",)

    def __str__(self):
        return self.finance_invoice.invoice_number + " line: " + self.line_number + " " + self.product_name


    def save(self, *args, **kwargs):
        self.subtotal = self._calculate_subtotal()
        self.tax = self._calculate_tax()
        self.total = self._calculate_total()

        super(FinanceInvoiceItem, self).save(*args, **kwargs)

    
    def _calculate_subtotal(self):
        # If tax is included in price, first remove it.
        tax_rate = self.finance_tax_rate
        price = float(self.price)
        if tax_rate:
            if tax_rate.rate_type == "IN":
                # divide price by 1.tax_percentage and then multiply by quantity
                percentage = (float(tax_rate.percentage) / 100) + 1
                price = price / percentage

        return float(price) * float(self.quantity)


    def _calculate_tax(self):
        tax_rate = self.finance_tax_rate
        if tax_rate:
            percentage = (tax_rate.percentage / 100)

            return float(self.subtotal) * float(percentage)
        else:
            return 0
        
    
    def _calculate_total(self):
        return self.subtotal + self.tax
