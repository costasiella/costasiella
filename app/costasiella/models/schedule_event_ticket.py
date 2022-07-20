from django.utils.translation import gettext as _

from django.db import models
from django.db.models import Q

from .schedule_event import ScheduleEvent
from .schedule_event_ticket_schedule_item import ScheduleEventTicketScheduleItem
from .finance_tax_rate import FinanceTaxRate
from .finance_costcenter import FinanceCostCenter
from .finance_glaccount import FinanceGLAccount

from .helpers import model_string


class ScheduleEventTicket(models.Model):
    schedule_event = models.ForeignKey(ScheduleEvent, on_delete=models.CASCADE, related_name="tickets")
    full_event = models.BooleanField(default=False)
    deletable = models.BooleanField(default=True)
    display_public = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    price = models.DecimalField(max_digits=20, decimal_places=2)
    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    schedule_items = models.ManyToManyField(
        'ScheduleItem',
        through='ScheduleEventTicketScheduleItem',
        related_name='schedule_items'
    )
    finance_tax_rate = models.ForeignKey(FinanceTaxRate, on_delete=models.SET_NULL, null=True)
    finance_glaccount = models.ForeignKey(FinanceGLAccount, on_delete=models.SET_NULL, null=True)
    finance_costcenter = models.ForeignKey(FinanceCostCenter, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return model_string(self)

    def save(self, *args, **kwargs):
        self.subtotal = self._calculate_subtotal()
        self.tax = self._calculate_tax()
        self.total = self._calculate_total()

        super(ScheduleEventTicket, self).save(*args, **kwargs)

    def _calculate_subtotal(self):
        # If tax is included in price, first remove it.
        tax_rate = self.finance_tax_rate
        price = float(self.price)
        if tax_rate:
            if tax_rate.rate_type == "IN":
                # divide price by 1.tax_percentage
                percentage = (float(tax_rate.percentage) / 100) + 1
                price = price / percentage

        return float(price)

    def _calculate_tax(self):
        tax_rate = self.finance_tax_rate
        if tax_rate:
            percentage = (tax_rate.percentage / 100)

            return float(self.subtotal) * float(percentage)
        else:
            return 0

    def _calculate_total(self):
        return self.subtotal + self.tax

    def is_sold_out(self):
        """
        Check if this ticket is sold out.
        Sold out when at least 1 activity doesn't have sufficient spaces remaining.
        :return:
        """
        from .schedule_event_ticket_schedule_item import ScheduleEventTicketScheduleItem
        from .schedule_item_attendance import ScheduleItemAttendance

        sold_out = False

        ticket_schedule_items = ScheduleEventTicketScheduleItem.objects.filter(
            schedule_event_ticket=self
        )
        for ticket_schedule_item in ticket_schedule_items:
            schedule_item = ticket_schedule_item.schedule_item
            count_attendance = ScheduleItemAttendance.objects.filter(
                Q(schedule_item=schedule_item) &
                ~Q(booking_status="cancelled")
            ).count()

            if count_attendance >= schedule_item.spaces:
                sold_out = True
                break

        return sold_out

    def _get_earlybird_qs(self, date):
        from .schedule_event_earlybird import ScheduleEventEarlybird

        earlybird_qs = ScheduleEventEarlybird.objects.filter(
            Q(schedule_event=self.schedule_event),
            Q(date_start__lte=date),
            Q(date_end__gte=date)
        ).order_by('-discount_percentage')

        return earlybird_qs

    def is_earlybird_price_on_date(self, date):
        earlybirds = self._get_earlybird_qs(date)

        # Check if discounts exit
        if earlybirds.exists():
            return True
        else:
            return False

    def get_earlybird_discount_on_date(self, date):
        from decimal import Decimal, ROUND_HALF_UP
        discount = Decimal(0)
        earlybird = None
        earlybirds = self._get_earlybird_qs(date)

        # Check if discounts exit
        if earlybirds.exists():
            # If so, get the first one (with the highest discount)
            earlybird = earlybirds.first()

            discount_percentage = earlybird.discount_percentage
            discount = Decimal(self.price * Decimal(discount_percentage / 100))

        return {
            "discount": Decimal(discount.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)),
            "earlybird": earlybird
        }

    def get_highest_subscription_group_discount_on_date_for_account(self, finance_order_item, date):
        from decimal import Decimal, ROUND_HALF_UP
        import time
        from .account_subscription import AccountSubscription
        from .schedule_event_subscription_group_discount import ScheduleEventSubscriptionGroupDiscount

        print("Hello world")
        account = finance_order_item.finance_order.account

        discount = Decimal(0)
        organization_subscription_group = None
        organization_subscription_groups = self._get_earlybird_qs(date)

        # Get subscriptions for account that are active on given date
        account_subscriptions = AccountSubscription.objects.filter(
            Q(account=account),
            Q(date_start__lte=date),
            (Q(date_end__gte=date) | Q(date_end__isnull=True))
        )
        print(account_subscriptions)

        # For each account subscription, check which group(s) it belongs to
        highest_subscription_group_discount = None
        for account_subscription in account_subscriptions:
            print(account_subscription)
            organization_subscription = account_subscription.organization_subscription
            subscription_group_subscriptions = organization_subscription.organizationsubscriptiongroupsubscription_set.all()
            print(subscription_group_subscriptions)
            for subscription_group_subscription in subscription_group_subscriptions:
                print(subscription_group_subscription)
                # For each subscription group, check if there's a discount
                subscription_group_discounts = ScheduleEventSubscriptionGroupDiscount.objects.filter(
                    schedule_event=self.schedule_event,
                    organization_subscription_group=subscription_group_subscription.organization_subscription_group
                )
                print(subscription_group_discounts)
                for subscription_group_discount in subscription_group_discounts:
                    if not highest_subscription_group_discount:
                        highest_subscription_group_discount = subscription_group_discount

                    if (subscription_group_discount.discount_percentage >
                            highest_subscription_group_discount.discount_percentage):
                        highest_subscription_group_discount = subscription_group_discount

        # time.sleep(10)

        print("Highest discount:")
        print(highest_subscription_group_discount)

        if highest_subscription_group_discount:
            discount_percentage = highest_subscription_group_discount.discount_percentage
            discount = Decimal(Decimal(finance_order_item.total) * Decimal(discount_percentage / 100))

        return {
            "discount": Decimal(discount.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)),
            "subscription_group_discount": highest_subscription_group_discount
        }



        # Return the highest found discount


        # # Check if discounts exit
        # if earlybirds.exists():
        #     # If so, get the first one (with the highest discount)
        #     earlybird = earlybirds.first()
        #
        #     discount_percentage = earlybird.discount_percentage
        #     discount = Decimal(self.price * Decimal(discount_percentage / 100))
        #
        # return {
        #     "discount": Decimal(discount.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)),
        #     "earlybird": earlybird
        # }

    def total_price_on_date(self, date):
        # Process earlybird discount
        earlybird_result = self.get_earlybird_discount_on_date(date)

        price = self.price - earlybird_result.get('discount', 0)

        return price
