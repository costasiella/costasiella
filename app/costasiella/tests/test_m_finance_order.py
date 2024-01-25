# This file holds tests for the finance invoice model as it has code to create invoice items
# These invoice items will change depending on values set in the database and should therefore be tested to be sure
# that the correct values are being set for the new invoice items.

# from graphql.error.located_error import GraphQLLocatedError
from django.utils.translation import gettext as _

import graphql
import base64
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id
from ..modules.date_tools import last_day_month

# Create your tests here.
from django.db.models import Sum
from django.contrib.auth.models import AnonymousUser, Permission
from django.utils import timezone

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema

from ..tasks.account.subscription.invoices.tasks import account_subscription_invoices_add_for_month


class TestModelFinanceOrder(TestCase):
    fixtures = [
        'app_settings.json',
        'finance_invoice_group.json',
        'finance_invoice_group_defaults.json',
        'finance_payment_methods.json'
    ]

    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

    def tearDown(self):
        # This is run after every test
        pass

    def test_item_add_schedule_event_ticket_with_earlybird_discount(self):
        """ Test adding schedule event ticket item with an earlybird discount"""
        today = timezone.now().date()

        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        schedule_event_earlybird = f.ScheduleEventEarlybirdFactory.create(
            schedule_event=schedule_event_ticket.schedule_event
        )
        account = f.RegularUserFactory.create()

        finance_order = f.FinanceOrderFactory.create(account=account)
        finance_order.item_add_schedule_event_ticket(schedule_event_ticket=schedule_event_ticket)

        # Now test;
        # Check if the order was created
        order = models.FinanceOrder.objects.all().first()
        sums = models.FinanceOrderItem.objects.filter(finance_order=order).aggregate(
            Sum('subtotal'), Sum('tax'), Sum('total')
        )

        subtotal = sums['subtotal__sum'] or 0
        tax = sums['tax__sum'] or 0
        total = sums['total__sum'] or 0

        # Check invoice item fields
        items = order.items.all()
        first_item = items[0]
        second_item = items[1]

        # Verify that event ticket item was added to the order
        self.assertEqual(first_item.product_name, "Event ticket")
        self.assertEqual(first_item.price, schedule_event_ticket.price)
        self.assertEqual(first_item.total, schedule_event_ticket.price)
        self.assertEqual(first_item.description,
                         '%s\n[%s]' % (schedule_event_ticket.schedule_event.name, schedule_event_ticket.name))
        self.assertEqual(first_item.quantity, 1)
        self.assertEqual(first_item.finance_tax_rate, schedule_event_ticket.finance_tax_rate)
        self.assertEqual(first_item.finance_glaccount, schedule_event_ticket.finance_glaccount)
        self.assertEqual(first_item.finance_costcenter, schedule_event_ticket.finance_costcenter)

        # Verify that the earlybird discount was added
        earlybird_result = schedule_event_ticket.get_earlybird_discount_on_date(today)
        discount_price = format(earlybird_result['discount'] * -1, ".2f")
        self.assertEqual(second_item.product_name, "Event ticket earlybird discount")
        self.assertEqual(format(second_item.price, ".2f"), discount_price)
        self.assertEqual(format(second_item.total, ".2f"), discount_price)
        self.assertEqual(second_item.description,
                         format(schedule_event_earlybird.discount_percentage, ".2f") + _('% discount'))
        self.assertEqual(second_item.quantity, 1)
        self.assertEqual(second_item.finance_tax_rate, schedule_event_ticket.finance_tax_rate)
        self.assertEqual(second_item.finance_glaccount, schedule_event_ticket.finance_glaccount)
        self.assertEqual(second_item.finance_costcenter, schedule_event_ticket.finance_costcenter)

    def test_item_add_schedule_event_ticket_with_subscription_group_discount(self):
        """ Test adding schedule event ticket item with a subscription group discount"""
        today = timezone.now().date()

        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        schedule_event = schedule_event_ticket.schedule_event
        subscription_group_discount = f.ScheduleEventSubscriptionGroupDiscountFactory.create(
            schedule_event=schedule_event
        )

        # Add a subscription and ensure it's added to the subscription group getting the discount
        account_subscription = f.AccountSubscriptionFactory.create()
        account = account_subscription.account
        organization_subscription_group = subscription_group_discount.organization_subscription_group
        organization_subscription_group.organization_subscriptions.add(account_subscription.organization_subscription)
        organization_subscription_group.save()

        finance_order = f.FinanceOrderFactory.create(account=account)
        finance_order.item_add_schedule_event_ticket(schedule_event_ticket=schedule_event_ticket)

        # Now test;
        # Check if invoice was created
        order = models.FinanceOrder.objects.all().first()
        sums = models.FinanceOrderItem.objects.filter(finance_order=order).aggregate(
            Sum('subtotal'), Sum('tax'), Sum('total')
        )

        subtotal = sums['subtotal__sum'] or 0
        tax = sums['tax__sum'] or 0
        total = sums['total__sum'] or 0

        # Check invoice item fields
        items = order.items.all()
        first_item = items[0]
        second_item = items[1]

        # Verify that event ticket item was added to the order
        self.assertEqual(first_item.product_name, "Event ticket")
        self.assertEqual(first_item.price, schedule_event_ticket.price)
        self.assertEqual(first_item.total, schedule_event_ticket.price)
        self.assertEqual(first_item.description,
                         '%s\n[%s]' % (schedule_event_ticket.schedule_event.name, schedule_event_ticket.name))
        self.assertEqual(first_item.quantity, 1)
        self.assertEqual(first_item.finance_tax_rate, schedule_event_ticket.finance_tax_rate)
        self.assertEqual(first_item.finance_glaccount, schedule_event_ticket.finance_glaccount)
        self.assertEqual(first_item.finance_costcenter, schedule_event_ticket.finance_costcenter)

        # Verify that the subscription group discount was added
        # Get the highest subscription group discount (if any)
        subscription_group_discount_result = \
            schedule_event_ticket.get_highest_subscription_group_discount_on_date_for_account(
                account, account_subscription.date_start
            )
        discount_price = format(subscription_group_discount_result['discount'] * -1, ".2f")
        discount_percentage = subscription_group_discount_result['subscription_group_discount'].discount_percentage
        self.assertEqual(second_item.product_name, "Event ticket subscription discount")
        self.assertEqual(format(second_item.price, ".2f"), discount_price)
        self.assertEqual(format(second_item.total, ".2f"), discount_price)
        self.assertEqual(second_item.description,
                         format(discount_percentage, ".2f") + _('% discount'))
        self.assertEqual(second_item.quantity, 1)
        self.assertEqual(second_item.finance_tax_rate, schedule_event_ticket.finance_tax_rate)
        self.assertEqual(second_item.finance_glaccount, schedule_event_ticket.finance_glaccount)
        self.assertEqual(second_item.finance_costcenter, schedule_event_ticket.finance_costcenter)

    def test_deliver_error_on_order_with_class_booking_when_customer_is_already_attending_class(self):
        """ Set status DELIVERY ERROR when trying to deliver an order with a class booking the customer
        is already attending """

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        account = schedule_item_attendance.account
        finance_order = f.FinanceOrderFactory.create(account=account)

        organization_classpass = schedule_item_attendance.account_classpass.organization_classpass

        finance_order_item = f.FinanceOrderItemClasspassFactory.create(
            finance_order=finance_order,
            organization_classpass=organization_classpass
        )
        finance_order = finance_order_item.finance_order

        finance_order_item.attendance_type = "CLASSPASS"
        finance_order_item.attendance_date = schedule_item_attendance.date
        finance_order_item.schedule_item = schedule_item_attendance.schedule_item

        finance_order_item.save()

        # Deliver though set the status to "DELIVERY ERROR" and set the delivery_error_message on the field
        finance_order.deliver()

        self.assertEqual(finance_order.status, 'DELIVERY_ERROR')
        self.assertEqual(finance_order.delivery_error_message,
                         _("Unable to deliver class pass in this order. Already attending the specified class."))

