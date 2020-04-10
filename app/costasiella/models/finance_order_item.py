from django.utils.translation import gettext as _
from django.utils import timezone
import datetime

now = timezone.now()

from django.db import models

from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount
from .finance_order import FinanceOrder
from .finance_tax_rate import FinanceTaxRate
from .organization_classpass import OrganizationClasspass
from .schedule_item import ScheduleItem

from .choices.schedule_item_attendance_types import get_schedule_item_attendance_types

class FinanceOrderItem(models.Model):
    ATTENDANCE_TYPES = get_schedule_item_attendance_types()

    finance_order = models.ForeignKey(FinanceOrder, on_delete=models.CASCADE)
    # Class pass fields
    organization_classpass = models.ForeignKey(OrganizationClasspass, on_delete=models.CASCADE, null=True)
    # Class fields
    attendance_type = models.CharField(max_length=255, choices=ATTENDANCE_TYPES)
    schedule_item = models.ForeignKey(ScheduleItem, on_delete=models.CASCADE)
    date = models.DateField()
    # General fields
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

        
    def __str__(self):
        return _("Order: ") + str(self.id) + self.product_name


    def save(self, *args, **kwargs):
        self.subtotal = self._calculate_subtotal()
        self.tax = self._calculate_tax()
        self.total = self._calculate_total()

        super(FinanceOrderItem, self).save(*args, **kwargs)

    
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


# def define_customers_orders_items():
#     """
#         Table to hold customers_orders items
#     """
#     ac_query = (db.accounting_costcenters.Archived == False)
#     ag_query = (db.accounting_glaccounts.Archived == False)

#     types = [
#         (None,T("Subscription")),
#         (1,T("Trial class")),
#         (2,T("Drop In")),
#         (3,T("Class card")),
#     ]

#     db.define_table('customers_orders_items',
#         Field('customers_orders_id', db.customers_orders,
#             readable=False,
#             writable=False),
#         Field('DummySubscription', 'boolean', # Used to hold display for 2nd month (not processed, added to invoice based on system settings
#               default=False,
#               readable=False,
#               writable=False),
#         Field('Custom', 'boolean',
#             default=False,
#             readable=False,
#             writable=False),
#         Field('Donation', 'boolean',
#             readable=False,
#             writable=False),
#         Field('ProductVariant', 'boolean',
#             readable=False,
#             writable=False,
#             default=False),
#         Field('SubscriptionRegistrationFee', 'boolean',
#             readable=False,
#             writable=False,
#             default=False),
#         Field('school_classcards_id', db.school_classcards,
#             readable=False,
#             writable=False),
#         Field('school_subscriptions_id', db.school_subscriptions,
#             readable=False,
#             writable=False),
#         Field('school_memberships_id', db.school_memberships,
#             readable=False,
#             writable=False),
#         Field('workshops_products_id', db.workshops_products,
#             readable=False,
#             writable=False),
#         Field('classes_id', db.classes,
#             readable=False,
#             writable=False),
#         Field('ClassDate', 'date',
#             readable=False,
#             writable=False,
#             requires=IS_DATE_IN_RANGE(format=DATE_FORMAT,
#                                       minimum=datetime.date(1900, 1, 1),
#                                       maximum=datetime.date(2999, 1, 1)),
#             represent=represent_date,
#             label=T("Class date"),
#             widget=os_datepicker_widget),
#         Field('AttendanceType', 'integer',
#             requires=IS_IN_SET(types),
#             represent=lambda value, row: session.att_types_dict.get(value, ""),
#             label=T("Type")),
#         Field('ProductName',
#               requires=IS_NOT_EMPTY(error_message=T("Enter product name")),
#               label=T("Product Name")),
#         Field('Description', 'text',
#               label=T("Description")),
#         Field('Quantity', 'decimal(20,2)',
#             requires=IS_DECIMAL_IN_RANGE(-100000, 1000000,
#                      error_message=T("Enter a number, decimals use '.'")),
#             default=1,
#             label=T("Quantity")),
#         Field('Price', 'decimal(20,2)',
#               represent=represent_decimal_as_amount,
#               default=0,
#               label=T("Price")),
#         Field('tax_rates_id', db.tax_rates,
#               requires=IS_EMPTY_OR(IS_IN_DB(db(),
#                                             'tax_rates.id',
#                                             '%(Name)s')),
#               represent=represent_tax_rate,
#               label=T("Tax rate")),
#         Field('TotalPriceVAT', 'decimal(20,2)',
#               compute=lambda row: row.Price or 0 * row.Quantity,
#               represent=represent_decimal_as_amount),
#         Field('VAT', 'decimal(20,2)',
#               compute=compute_invoice_item_vat,
#               represent=represent_decimal_as_amount),
#         Field('TotalPrice', 'decimal(20,2)',
#               compute=compute_invoice_item_total_price,
#               represent=represent_decimal_as_amount),
#         Field('accounting_glaccounts_id', db.accounting_glaccounts,
#               requires=IS_EMPTY_OR(IS_IN_DB(db(ag_query),
#                                             'accounting_glaccounts.id',
#                                             '%(Name)s')),
#               represent=represent_accounting_glaccount,
#               label=T('G/L Account'),
#               comment=T('General ledger account ID in your accounting software')),
#         Field('accounting_costcenters_id', db.accounting_costcenters,
#               requires=IS_EMPTY_OR(IS_IN_DB(db(ac_query),
#                                             'accounting_costcenters.id',
#                                             '%(Name)s')),
#               represent=represent_accounting_costcenter,
#               label=T("Cost center"),
#               comment=T("Cost center code in your accounting software")),
#         )
