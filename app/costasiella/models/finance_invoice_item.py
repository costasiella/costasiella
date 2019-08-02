from django.utils.translation import gettext as _
from django.utils import timezone

from django.db import models

from .account_classpass import AccountClasspass
from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount
from .finance_invoice import FinanceInvoice
from .finance_tax_rate import FinanceTaxRate

class FinanceInvoiceItem(models.Model):
    finance_invoice = models.ForeignKey(FinanceInvoice, on_delete=models.CASCADE)
    account_classpass = models.ForeignKey(AccountClasspass, on_delete=models.SET_NULL, null=True, default=None)
    line_number = models.PositiveSmallIntegerField(default=1)
    product_name = models.CharField(max_length=255)
    description = models.TextField(default="")
    quantity = models.DecimalField(max_digits=20, decimal_places=2)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.CASCADE)
    sub_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    vat = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.CASCADE, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.finance_invoice.invoice_number + " line: " + self.line_number + " " + self.product_name


    def save(self, *args, **kwargs):
        self.sub_total = self._calculate_sub_total()
        self.vat = self._calculate_vat()
        self.total = self._calculate_total()

        super(FinanceInvoiceItem, self).save(*args, **kwargs)

    
    def _calculate_sub_total(self):
        # If tax is included in price, first remove it.
        tax_rate = self.finance_tax_rate
        price = self.price
        if tax_rate.rate_type == "IN":
            # divide price by 1.tax_percentage and then multiply by quantity
            percentage = (tax_rate.percentage / 100) + 1
            price = self.price / percentage

        return price * self.quantity


    def _calculate_vat(self):
        tax_rate = self.finance_tax_rate
        percentage = (tax_rate.percentage / 100)
        
        return self.sub_total * percentage
        
    
    def _calculate_total(self):
        return self.sub_total + self.vat


# def define_invoices_items():
#     ac_query = (db.accounting_costcenters.Archived == False)
#     ag_query = (db.accounting_glaccounts.Archived == False)

#     db.define_table('invoices_items',
#         Field('invoices_id', db.invoices,
#             readable=False,
#             writable=False),
#         Field('Sorting', 'integer',
#             readable=False,
#             writable=False),
#         Field('ProductName',
#             requires=IS_NOT_EMPTY(error_message = T("Enter product name")),
#             label   =T("Product Name")),
#         Field('Description', 'text',
#             label=T("Description")),
#         Field('Quantity', 'double',
#             requires=IS_FLOAT_IN_RANGE(-100000, 1000000, dot=".",
#                      error_message=T("Enter a number, decimals use '.'")),
#             default=1,
#             label=T("Quantity")),
#         Field('Price', 'double',
#             represent=represent_float_as_amount,
#             default=0,
#             label=T("Price")),
#         Field('tax_rates_id', db.tax_rates,
#             requires=IS_EMPTY_OR(IS_IN_DB(db(),
#                                   'tax_rates.id',
#                                   '%(Name)s')),
#             represent=represent_tax_rate,
#             label=T("Tax rate")),
#         Field('TotalPriceVAT', 'double',
#             compute=lambda row: row.Price * row.Quantity,
#             represent=represent_float_as_amount),
#         Field('VAT', 'double',
#             compute=compute_invoice_item_vat,
#             represent=represent_float_as_amount),
#         Field('TotalPrice', 'double',
#             compute=compute_invoice_item_total_price,
#             represent=represent_float_as_amount),
#         Field('accounting_glaccounts_id', db.accounting_glaccounts,
#               requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
#                                             'accounting_glaccounts.id',
#                                             '%(Name)s')),
#               represent=represent_accounting_glaccount,
#               label=T('G/L Account'),
#               comment=T('General ledger account ID in your accounting software')),
#         Field('accounting_costcenters_id', db.accounting_costcenters,
#             requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
#                                           'accounting_costcenters.id',
#                                           '%(Name)s')),
#             represent=represent_accounting_costcenter,
#             label=T("Cost center")),