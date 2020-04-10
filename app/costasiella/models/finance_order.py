from django.utils.translation import gettext as _
from django.utils import timezone
import datetime

now = timezone.now()

from django.db import models

from .account import Account
# from .finance_invoice_group import FinanceInvoiceGroup
# from .finance_payment_method import FinancePaymentMethod


class FinanceOrder(models.Model):
    STATUSES = (
        ('RECEIVED', _("Received")),
        ('AWAITING_PAYMENT', _("Awaiting payment")),
        ('PAID', _("Paid")),
        ('DELIVERED', _("Delivered")),
        ('CANCELLED', _("Cancelled")),
    )

    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=255, choices=STATUSES, default="RECEIVED")
    note = models.TextField(default="")
    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return _("Order: ") + str(self.id)


    def update_amounts(self):
        """ Update total amounts fields (subtotal, tax, total, paid, balance) """
        # Get totals from invoice items
        from .finance_order_item import FinanceOrderItem
        from django.db.models import Sum

        sums = FinanceOrderItem.objects.filter(finance_order = self).aggregate(Sum('subtotal'), Sum('tax'), Sum('total'))

        self.subtotal = sums['subtotal__sum'] or 0
        self.tax = sums['tax__sum'] or 0
        self.total = sums['total__sum'] or 0

        self.save(update_fields=[
            "subtotal",
            "tax",
            "total"
        ])


    def item_add_classpass(self, organization_classpass):
        """
        Add organization classpass invoice item
        """
        from .finance_order_item import FinanceOrderItem
        
        # add item to order
        finance_order_item = FinanceOrderItem(
            finance_order = self,
            organization_classpass = organization_classpass,
            product_name = _('Class pass'),
            description = "",
            quantity = 1,
            price = organization_classpass.price,
            finance_tax_rate = organization_classpass.finance_tax_rate,
            finance_glaccount = organization_classpass.finance_glaccount,
            finance_costcenter = organization_classpass.finance_costcenter,
        )

        finance_order_item.save()

        self.update_amounts()

        return finance_order_item


    # def tax_rates_amounts(self, formatted=False):
    #     """
    #     Returns tax for each tax rate as list sorted by tax rate percentage
    #     format: [ [ tax_rate_obj, sum ] ]
    #     """
    #     from django.db.models import Sum

    #     from .finance_invoice_item import FinanceInvoiceItem
    #     from .finance_tax_rate import FinanceTaxRate

    #     amounts_tax = []

    #     tax_rates = FinanceTaxRate.objects.filter(
    #         financeinvoiceitem__finance_invoice = self,
    #     ).annotate(invoice_amount=Sum("financeinvoiceitem__tax"))

    #     # print(tax_rates)

    #     # for t in tax_rates:
    #     #     print(t.name)
    #     #     print(t.rate_type)
    #     #     print(t.invoice_amount)

    #     return tax_rates

            




    #TODO: Port this function to Django
    # def amounts_tax_rates(self, formatted=False):
    #     """
    #         Returns vat for each tax rate as list sorted by tax rate percentage
    #         format: [ [ Name, Amount ] ]
    #     """
    #     db = current.db
    #     # CURRSYM = current.globalenv['CURRSYM']

    #     amounts_vat = []
    #     rows = db().select(db.tax_rates.id, db.tax_rates.Name,
    #                        orderby=db.tax_rates.Percentage)
    #     for row in rows:
    #         sum = db.invoices_items.VAT.sum()
    #         query = (db.invoices_items.invoices_id == iID) & \
    #                 (db.invoices_items.tax_rates_id == row.id)

    #         result = db(query).select(sum).first()

    #         if not result[sum] is None:
    #             # if formatted:
    #                 # amount = SPAN(CURRSYM, ' ', format(result[sum], '.2f'))
    #             else:
    #                 amount = result[sum]
    #             amounts_vat.append({'Name'   : row.Name,
    #                                 'Amount' : amount})

    #     return amounts_vat