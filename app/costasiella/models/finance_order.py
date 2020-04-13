from django.utils.translation import gettext as _
from django.utils import timezone
import datetime

now = timezone.now()

from django.db import models

from .account import Account
from .finance_invoice import FinanceInvoice
from .finance_invoice_group import FinanceInvoiceGroup
from .finance_invoice_group_default import FinanceInvoiceGroupDefault
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

    finance_invoice = models.ForeignKey(FinanceInvoice, on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=255, choices=STATUSES, default="RECEIVED")
    message = models.TextField(default="")
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
            description = organization_classpass.name,
            quantity = 1,
            price = organization_classpass.price,
            finance_tax_rate = organization_classpass.finance_tax_rate,
            finance_glaccount = organization_classpass.finance_glaccount,
            finance_costcenter = organization_classpass.finance_costcenter,
        )

        finance_order_item.save()

        self.update_amounts()

        return finance_order_item


    def deliver(self):
        """
        Deliver this order
        """
        # Don't deliver cancelled orders or orders that have already been deliverd
        if self.status == "DELIVERED" or self.status == "CANCELLED":
            return

        # Don't create an invoice when there's nothing that needs to be paid
        create_invoice = False
        if self.total > 0:
            create_invoice = True
            invoice = self._deliver_create_invoice()


    def _deliver_create_invoice(self):
        """
        Create invoice for order delivery & link invoice to order
        """
        finance_invoice_group_default = FinanceInvoiceGroupDefault.objects.filter(item_type="CLASSPASSES").first()
        finance_invoice_group = finance_invoice_group_default.finance_invoice_group

        finance_invoice = FinanceInvoice(
            account = self.account,
            finance_invoice_group = finance_invoice_group,
            summary = _("Order %s" % self.id),
            status = "SENT",
            terms = finance_invoice_group.terms,
            footer = finance_invoice_group.footer
        )
        finance_invoice.save()
        self.finance_invoice = finance_invoice

        return finance_invoice


    def _deliver_classpass(self,organization_classpass):
        """
        Deliver classpass
        """




            


