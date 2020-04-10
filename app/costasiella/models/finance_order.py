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


    # def _first_invoice_in_group_this_year(self, year): 
    #     """
    #     This invoice has to be the first in the group this year if no other 
    #     invoices are found in this group in this year
    #     """
    #     year_start = datetime.date(year, 1, 1)
    #     year_end = datetime.date(year, 12, 31)

    #     return not FinanceInvoice.objects.filter(
    #         date_sent__gte = year_start,
    #         date_sent__lte = year_end,
    #         finance_invoice_group = self.finance_invoice_group
    #     ).exists()  


    # def _increment_group_next_id(self):
    #     # This code is here so the id is only +=1'd when an invoice is actually created 
    #     self.finance_invoice_group.next_id += 1
    #     self.finance_invoice_group.save()


    # def save(self, *args, **kwargs):
    #     if self.pk is None: # We know this is object creation when there is no pk yet.
    #         # Get relation info
    #         self._set_relation_info()

    #         # set dates
    #         if not self.date_sent:
    #             # Date is now if not supplied on creation
    #             self.date_sent = timezone.now().date()
    #         self.date_due = self.date_sent + datetime.timedelta(days=self.finance_invoice_group.due_after_days)
            
    #         ## set invoice number
    #         # Check if this is the first invoice in this group
    #         # (Needed to check if we should reset the numbering for this year)
    #         year = self.date_sent.year
    #         first_invoice_in_group_this_year = self._first_invoice_in_group_this_year(year)
    #         self.invoice_number = self.finance_invoice_group.next_invoice_number(
    #             year, 
    #             first_invoice_this_year = first_invoice_in_group_this_year
    #         )

    #         ## Increase next_id for invoice group
    #         self._increment_group_next_id()

    #     super(FinanceInvoice, self).save(*args, **kwargs)


    # def _get_item_next_line_nr(self):
    #     """
    #     Returns the next item number for an invoice
    #     use to set sorting when adding an item
    #     """
    #     from .finance_invoice_item import FinanceInvoiceItem

    #     qs = FinanceInvoiceItem.objects.filter(finance_invoice = self)

    #     return qs.count()


    # def item_add_classpass(self, account_classpass):
    #     """
    #     Add account classpass invoice item
    #     """
    #     from .finance_invoice_item import FinanceInvoiceItem
    #     # add item to invoice
        

    #     organization_classpass = account_classpass.organization_classpass
    #     # finance_invoice = FinanceInvoice.objects.get(pk=self.id)

    #     finance_invoice_item = FinanceInvoiceItem(
    #         finance_invoice = self,
    #         account_classpass = account_classpass,
    #         line_number = self._get_item_next_line_nr(),
    #         product_name = _('Class pass'),
    #         description = _('Class pass %s' % str(account_classpass.pk)),
    #         quantity = 1,
    #         price = organization_classpass.price,
    #         finance_tax_rate = organization_classpass.finance_tax_rate,
    #         finance_glaccount = organization_classpass.finance_glaccount,
    #         finance_costcenter = organization_classpass.finance_costcenter,
    #     )

    #     finance_invoice_item.save()

    #     self.update_amounts()

    #     return finance_invoice_item


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