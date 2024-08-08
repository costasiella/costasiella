import logging

from django.utils.translation import gettext as _
from django.utils import timezone
from django.db import models

from ..models.choices.finance_order_statuses import get_finance_order_statuses
from .account import Account
from .finance_invoice import FinanceInvoice
from .finance_invoice_group_default import FinanceInvoiceGroupDefault

from ..dudes.class_checkin_dude import ClassCheckinDude

now = timezone.now()
logger = logging.getLogger(__name__)


class FinanceOrder(models.Model):
    STATUSES = get_finance_order_statuses()

    finance_invoice = models.ForeignKey(FinanceInvoice, on_delete=models.SET_NULL, null=True, related_name="orders")
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=255, choices=STATUSES, default="RECEIVED")
    message = models.TextField(default="")
    delivery_error_message = models.TextField(default="")
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

        sums = FinanceOrderItem.objects.filter(finance_order=self).aggregate(Sum('subtotal'), Sum('tax'), Sum('total'))

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

    def item_add_schedule_event_ticket(self, schedule_event_ticket):
        """
        Add organization classpass order item
        """
        from .finance_order_item import FinanceOrderItem

        # add item to order
        finance_order_item = FinanceOrderItem(
            finance_order=self,
            schedule_event_ticket=schedule_event_ticket,
            product_name=_('Event ticket'),
            description='%s\n[%s]' % (schedule_event_ticket.schedule_event.name, schedule_event_ticket.name),
            quantity=1,
            price=schedule_event_ticket.price,
            finance_tax_rate=schedule_event_ticket.finance_tax_rate,
            finance_glaccount=schedule_event_ticket.finance_glaccount,
            finance_costcenter=schedule_event_ticket.finance_costcenter,
        )

        finance_order_item.save()

        # Discount processing
        now = timezone.now()
        date = now.date()

        # Check if an earlybird discount should be added
        earlybird_result = schedule_event_ticket.get_earlybird_discount_on_date(date)
        if earlybird_result.get('discount', 0):
            discount_percentage = earlybird_result['earlybird'].discount_percentage
            earlybird_finance_order_item = FinanceOrderItem(
                finance_order=self,
                product_name=_('Event ticket earlybird discount'),
                description=str(discount_percentage) + _('% discount'),
                quantity=1,
                price=earlybird_result['discount'] * -1,
                finance_tax_rate=schedule_event_ticket.finance_tax_rate,
                finance_glaccount=schedule_event_ticket.finance_glaccount,
                finance_costcenter=schedule_event_ticket.finance_costcenter,
            )
            earlybird_finance_order_item.save()

        # Get the highest subscription group discount (if any)
        subscription_group_discount_result = \
            schedule_event_ticket.get_highest_subscription_group_discount_on_date_for_account(
                self.account, date
            )
        if subscription_group_discount_result.get('discount', 0):
            discount_percentage = subscription_group_discount_result['subscription_group_discount'].discount_percentage
            subscription_group_discount_finance_order_item = FinanceOrderItem(
                finance_order=self,
                product_name=_('Event ticket subscription discount'),
                description=str(discount_percentage) + _('% discount'),
                quantity=1,
                price=subscription_group_discount_result['discount'] * -1,
                finance_tax_rate=schedule_event_ticket.finance_tax_rate,
                finance_glaccount=schedule_event_ticket.finance_glaccount,
                finance_costcenter=schedule_event_ticket.finance_costcenter,
            )
            subscription_group_discount_finance_order_item.save()

        self.update_amounts()

        return finance_order_item

    def item_add_classpass(self, organization_classpass, schedule_item=None, attendance_date=None):
        """
        Add organization classpass order item
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

    def item_add_subscription(self, organization_subscription):
        """
        Add organization subscription order item
        """
        from .finance_order_item import FinanceOrderItem

        now = timezone.now()
        # add item to order
        today = now.date()
        finance_order_item = FinanceOrderItem(
            finance_order=self,
            organization_subscription=organization_subscription,
            product_name=_('Subscription'),
            description=organization_subscription.name,
            quantity=1,
            price=organization_subscription.get_price_first_month(today),
            finance_tax_rate=organization_subscription.get_finance_tax_rate_on_date(today),
            finance_glaccount=organization_subscription.finance_glaccount,
            finance_costcenter=organization_subscription.finance_costcenter,
        )
        finance_order_item.save()

        self.update_amounts()

        return finance_order_item

    def items_contain_subscription(self):
        """
        Check if there is a subscription item in the items for this order
        :return:
        """
        from .finance_order_item import FinanceOrderItem

        qs = FinanceOrderItem.objects.filter(
            finance_order=self,
            organization_subscription__isnull=False,
        )
        return qs.exists()

    def is_deliverable(self):
        """
        Check whether is order is deliverable, if not, don't process any further and
        set the status to delivery error

        :return:
        """
        from .finance_order_item import FinanceOrderItem

        deliverable = True

        items = FinanceOrderItem.objects.filter(finance_order=self)
        for item in items:
            if item.organization_classpass:
                # Check if we should deliver. Don't deliver when;
                # schedule_item and attendance_date are set, but account is already attending the class.
                class_checkin_dude = ClassCheckinDude()
                account_is_attending_class = class_checkin_dude.account_is_attending_class(
                    account=self.account,
                    schedule_item=item.schedule_item,
                    date=item.attendance_date
                )
                if account_is_attending_class:
                    deliverable = False

                    logger.error("Unable to deliver order %s: Account already attending specified class.",
                                 self.id)

                    self.status = 'DELIVERY_ERROR'
                    self.delivery_error_message = \
                        _("Unable to deliver class pass in this order. Already attending the specified class.")
                    self.save()

        return deliverable

    def deliver(self):
        """
        Deliver this order
        """
        from .finance_order_item import FinanceOrderItem

        # Don't deliver cancelled orders or orders that have already been delivered
        dont_deliver_statuses = [
            'DELIVERED',
            'DELIVERY_ERROR',
            'CANCELLED'
        ]

        if self.status in dont_deliver_statuses:
            return

        # Don't delivery undeliverable orders
        if not self.is_deliverable():
            return

        # Don't create an invoice when there's nothing that needs to be paid
        create_invoice = False
        finance_invoice = None

        # The invoice object is created, but not stored in the DB yet.
        if self.total > 0:
            create_invoice = True
            self._deliver_create_invoice()

        items = FinanceOrderItem.objects.filter(finance_order=self)

        for item in items:
            if item.schedule_event_ticket:
                account_schedule_event_ticket = self._deliver_schedule_event_ticket(
                    item.schedule_event_ticket,
                    self.finance_invoice,
                    create_invoice
                )

            if item.organization_classpass:
                # Continue delivery as usual
                account_classpass = self._deliver_classpass(
                    item.organization_classpass,
                    self.finance_invoice,
                    create_invoice
                )

                if item.schedule_item and item.attendance_date:
                    self._deliver_checkin_class(
                        schedule_item=item.schedule_item,
                        attendance_date=item.attendance_date,
                        account_classpass=account_classpass
                    )

            if item.organization_subscription:
                account_subscription = self._deliver_subscription(
                    item.organization_subscription,
                    self.finance_invoice,
                    create_invoice
                )

                #TODO: Check for class when delivering a subscription

        self.status = "DELIVERED"
        self.save()

        return dict(
            finance_invoice=self.finance_invoice
        )

    def _deliver_create_invoice(self):
        """
        Create invoice for order delivery & link invoice to order
        """
        finance_invoice_group_default = FinanceInvoiceGroupDefault.objects.filter(item_type="SHOP_SALES").first()
        finance_invoice_group = finance_invoice_group_default.finance_invoice_group

        finance_invoice = FinanceInvoice(
            account=self.account,
            finance_invoice_group=finance_invoice_group,
            summary=_("Order %s" % self.id),
            status="SENT",
            terms=finance_invoice_group.terms,
            footer=finance_invoice_group.footer
        )
        self.finance_invoice = finance_invoice
        finance_invoice.save()

        return finance_invoice

    def _deliver_schedule_event_ticket(self,
                                       schedule_event_ticket,
                                       finance_invoice,
                                       create_invoice):
        """
        :param schedule_event_ticket: models.schedule_event_ticket object
        :param finance_invoice: models.finance_invoice object
        :param create_invoice: Boolean
        :return:
        """
        from ..dudes.sales_dude import SalesDude

        sales_dude = SalesDude()
        today = timezone.now().date()
        result = sales_dude.sell_schedule_event_ticket(
            self.account,
            schedule_event_ticket,
            create_invoice=False
        )
        account_schedule_event_ticket = result['account_schedule_event_ticket']

        if create_invoice:
            finance_invoice.item_add_schedule_event_ticket(account_schedule_event_ticket)

        return account_schedule_event_ticket

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

    def _deliver_subscription(self,
                              organization_subscription,
                              finance_invoice,
                              create_invoice):
        """
        :param organization_subscription: models.organization_subscription object
        :param finance_invoice: models.finance_invoice object
        :param create_invoice: Boolean
        :return:
        """
        from .finance_payment_method import FinancePaymentMethod
        from ..dudes.sales_dude import SalesDude

        # Mollie payment
        finance_payment_method = FinancePaymentMethod.objects.get(pk=100)

        sales_dude = SalesDude()
        today = timezone.now().date()
        result = sales_dude.sell_subscription(
            self.account,
            organization_subscription,
            today,
            finance_payment_method=finance_payment_method,
            create_invoice=False
        )
        account_subscription = result['account_subscription']

        if create_invoice:
            finance_invoice.item_add_subscription(account_subscription, today.year, today.month)

        return account_subscription

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
