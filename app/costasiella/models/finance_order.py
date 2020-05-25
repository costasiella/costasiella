from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models

from ..models.choices.finance_order_statuses import get_finance_order_statuses
from .account import Account
from .finance_invoice import FinanceInvoice
from .finance_invoice_group_default import FinanceInvoiceGroupDefault

from ..dudes.class_checkin_dude import ClassCheckinDude

now = timezone.now()


class FinanceOrder(models.Model):
    STATUSES = get_finance_order_statuses()

    finance_invoice = models.ForeignKey(FinanceInvoice, on_delete=models.SET_NULL, null=True, related_name="orders")
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

    def _item_add_class_data(self, finance_order_item, schedule_item, attendance_date):
        """
        Enrich item with class checkin info
        :param schedule_item: schedule item id
        :param date: class date
        :return: finance order item with class data set
        """
        finance_order_item.attendance_date = attendance_date
        finance_order_item.schedule_item = schedule_item

        return finance_order_item

    def item_add_classpass(self, organization_classpass, schedule_item=None, attendance_date=None):
        """
        Add organization classpass invoice item
        """
        from .finance_order_item import FinanceOrderItem
        
        # add item to order
        finance_order_item = FinanceOrderItem(
            finance_order=self,
            organization_classpass=organization_classpass,
            product_name=_('Class pass'),
            description=organization_classpass.name,
            quantity=1,
            price=organization_classpass.price,
            finance_tax_rate=organization_classpass.finance_tax_rate,
            finance_glaccount=organization_classpass.finance_glaccount,
            finance_costcenter=organization_classpass.finance_costcenter,
        )

        if schedule_item and attendance_date:
            finance_order_item = self._item_add_class_data(finance_order_item,
                                                           schedule_item,
                                                           attendance_date)
        finance_order_item.save()

        self.update_amounts()

        return finance_order_item

    def deliver(self):
        """
        Deliver this order
        """
        from .finance_order_item import FinanceOrderItem
        # Don't deliver cancelled orders or orders that have already been delivered
        if self.status == "DELIVERED" or self.status == "CANCELLED":
            return

        # Don't create an invoice when there's nothing that needs to be paid
        create_invoice = False
        finance_invoice = None

        if self.total > 0:
            create_invoice = True
            finance_invoice = self._deliver_create_invoice()

        items = FinanceOrderItem.objects.filter(finance_order=self)

        for item in items:
            if item.organization_classpass:
                account_classpass = self._deliver_classpass(
                    item.organization_classpass,
                    finance_invoice,
                    create_invoice
                )

                if item.schedule_item and item.attendance_date:
                    print("DELIVER CLASS CHECKIN FOR CLASS PASS")
                    self._deliver_checkin_class(
                        schedule_item=item.schedule_item,
                        attendance_date=item.attendance_date,
                        account_classpass=account_classpass
                    )

        self.status = "DELIVERED"
        self.save()

        return dict(
            finance_invoice=finance_invoice
        )

    def _deliver_create_invoice(self):
        """
        Create invoice for order delivery & link invoice to order
        """
        finance_invoice_group_default = FinanceInvoiceGroupDefault.objects.filter(item_type="CLASSPASSES").first()
        finance_invoice_group = finance_invoice_group_default.finance_invoice_group

        finance_invoice = FinanceInvoice(
            account=self.account,
            finance_invoice_group=finance_invoice_group,
            summary=_("Order %s" % self.id),
            status="SENT",
            terms=finance_invoice_group.terms,
            footer=finance_invoice_group.footer
        )
        finance_invoice.save()
        self.finance_invoice = finance_invoice

        return finance_invoice

    def _deliver_classpass(self,
                           organization_classpass,
                           finance_invoice,
                           create_invoice):
        """
        :param organization_classpass: models.organization_classpass object
        :param finance_invoice: models.finance_invoice object
        :param create_invoice: Boolean
        :return:
        """
        from ..dudes.sales_dude import SalesDude

        sales_dude = SalesDude()
        today = timezone.now().date()
        result = sales_dude.sell_classpass(
            self.account, 
            organization_classpass, 
            today,
            create_invoice=False
        )
        account_classpass = result['account_classpass']

        if create_invoice:
            finance_invoice.item_add_classpass(
                account_classpass
            )

        return account_classpass

    def _deliver_checkin_class(self,
                               schedule_item,
                               attendance_date,
                               account_classpass=None):
        """

        :param schedule_item: models.ScheduleItem object
        :param attendance_date: datetime.date (class date)
        :param account_classpass: models.AccountClasspass object
        :return: None
        """
        class_checkin_dude = ClassCheckinDude()
        schedule_item_attendance = None

        if account_classpass:
            schedule_item_attendance = class_checkin_dude.class_checkin_classpass(
                account=self.account,
                account_classpass=account_classpass,
                schedule_item=schedule_item,
                date=attendance_date,
                online_booking=True,  # Orders can only be online bookings
                booking_status="BOOKED"
            )

        return schedule_item_attendance
