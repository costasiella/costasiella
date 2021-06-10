# This file holds tests for the finance invoice model as it has code to create invoice items
# These invoice items will change depending on values set in the database and should therefore be tested to be sure
# that the correct values are being set for the new invoice items.

# from graphql.error.located_error import GraphQLLocatedError
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


class TestModelAccountSubscription(TestCase):
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

    def test_create_invoice_for_month(self):
        """ Test Add regular subscription item - default values"""
        today = timezone.now().date()

        account_subscription = f.AccountSubscriptionFactory.create()
        account = account_subscription.account
        organization_subscription = account_subscription.organization_subscription
        price = f.OrganizationSubscriptionPriceFactory(organization_subscription=organization_subscription)
        finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)  # 100 = default

        date_start = account_subscription.date_start

        # Create an invoice with date today for first month of subscription
        account_subscription.create_invoice_for_month(
            year=date_start.year,
            month=date_start.month,
        )

        # Check if invoice was created
        invoice = models.FinanceInvoice.objects.all().first()
        sums = models.FinanceInvoiceItem.objects.filter(finance_invoice=invoice).aggregate(
            Sum('subtotal'), Sum('tax'), Sum('total')
        )

        subtotal = sums['subtotal__sum'] or 0
        tax = sums['tax__sum'] or 0
        total = sums['total__sum'] or 0

        # Check invoice fields
        self.assertEqual(invoice.summary, "Subscription invoice %s-%s" % (date_start.year, date_start.month))
        self.assertEqual(invoice.relation_contact_name, account.full_name)
        self.assertEqual(invoice.status, "SENT")
        self.assertEqual(invoice.invoice_number, "INV%s1" % today.year)
        self.assertEqual(invoice.date_sent, today)
        self.assertEqual(invoice.date_due, today + datetime.timedelta(days=finance_invoice_group.due_after_days))
        self.assertEqual(invoice.total, total)
        self.assertEqual(invoice.tax, tax)
        self.assertEqual(invoice.subtotal, subtotal)
        self.assertEqual(invoice.balance, total)

        # Check invoice item
        invoice_item = invoice.items.all().first()

        self.assertEqual(invoice_item.account_subscription, account_subscription)
        self.assertEqual(invoice_item.subscription_year, date_start.year)
        self.assertEqual(invoice_item.subscription_month, date_start.month)
        self.assertEqual(invoice_item.line_number, 0)
        self.assertEqual(invoice_item.product_name, "Subscription %s" % account_subscription.id)
        self.assertEqual(invoice_item.description, "%s [%s - %s]" % (
            organization_subscription.name,
            date_start,
            str(datetime.date(date_start.year, date_start.month, last_day_month(date_start)))
        ))
        self.assertEqual(invoice_item.quantity, 1)
        self.assertEqual(invoice_item.price, price.price)
        self.assertEqual(float(invoice_item.tax), round(invoice_item._calculate_tax(), 2))
        self.assertEqual(float(invoice_item.subtotal), round(invoice_item._calculate_subtotal(), 2))
        self.assertEqual(float(invoice_item.total), round(invoice_item._calculate_total(), 2))
        self.assertEqual(invoice_item.finance_tax_rate, price.finance_tax_rate)
        self.assertEqual(invoice_item.finance_costcenter, organization_subscription.finance_costcenter)
        self.assertEqual(invoice_item.finance_glaccount, organization_subscription.finance_glaccount)

    def test_create_invoice_for_month_add_registration_fee(self):
        """ Check registration fee was added, if set for subscription """
        today = timezone.now().date()

        account_subscription = f.AccountSubscriptionFactory.create()
        account = account_subscription.account
        organization_subscription = account_subscription.organization_subscription
        price = f.OrganizationSubscriptionPriceFactory(organization_subscription=organization_subscription)
        finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)  # 100 = default

        date_start = account_subscription.date_start

        # Create an invoice with date today for first month of subscription
        account_subscription.create_invoice_for_month(
            year=date_start.year,
            month=date_start.month,
        )

        # Check if invoice was created
        invoice = models.FinanceInvoice.objects.all().first()

        # Check invoice fields
        self.assertEqual(invoice.summary, "Subscription invoice %s-%s" % (date_start.year, date_start.month))

        # Check invoice item
        invoice_item = invoice.items.all()[1]

        self.assertEqual(invoice_item.line_number, 1)
        self.assertEqual(invoice_item.product_name, "Registration fee")
        self.assertEqual(invoice_item.description, "One time registration fee")
        self.assertEqual(invoice_item.quantity, 1)
        self.assertEqual(invoice_item.price, organization_subscription.registration_fee)

        # Re-fetch account subscription and check registration fee is set to paid
        account_subscription = models.AccountSubscription.objects.get(pk=account_subscription.id)
        self.assertEqual(account_subscription.registration_fee_paid, True)

    def test_create_invoice_for_month_add_registration_fee_not_added(self):
        """ Check registration fee was added, if set for subscription, but already paid """
        today = timezone.now().date()

        account_subscription = f.AccountSubscriptionFactory.create()
        account_subscription.registration_fee_paid = True
        account_subscription.save()
        account = account_subscription.account
        organization_subscription = account_subscription.organization_subscription
        price = f.OrganizationSubscriptionPriceFactory(organization_subscription=organization_subscription)
        finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)  # 100 = default

        date_start = account_subscription.date_start

        # Create an invoice with date today for first month of subscription
        account_subscription.create_invoice_for_month(
            year=date_start.year,
            month=date_start.month,
        )

        # Check if invoice was created
        invoice = models.FinanceInvoice.objects.all().first()

        # Check invoice fields
        self.assertEqual(invoice.summary, "Subscription invoice %s-%s" % (date_start.year, date_start.month))

        # Check only one invoice item (no item for registration fee)
        self.assertEqual(len(invoice.items.all()), 1)

    def test_create_invoice_for_month_blocked(self):
        """ Check invoice is created when subscription is blocked """
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        account_subscription = subscription_block.account_subscription
        account = account_subscription.account
        organization_subscription = account_subscription.organization_subscription
        price = f.OrganizationSubscriptionPriceFactory(organization_subscription=organization_subscription)
        finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)  # 100 = default

        date_start = account_subscription.date_start

        # Create an invoice with date today for first month of subscription
        account_subscription.create_invoice_for_month(
            year=date_start.year,
            month=date_start.month,
        )

        # Check if invoice was created
        invoice = models.FinanceInvoice.objects.all().first()
        sums = models.FinanceInvoiceItem.objects.filter(finance_invoice=invoice).aggregate(
            Sum('subtotal'), Sum('tax'), Sum('total')
        )

        subtotal = sums['subtotal__sum'] or 0
        tax = sums['tax__sum'] or 0
        total = sums['total__sum'] or 0

        # Check invoice fields
        self.assertEqual(invoice.summary, "Subscription invoice %s-%s" % (date_start.year, date_start.month))
        self.assertEqual(invoice.relation_contact_name, account.full_name)
        self.assertEqual(invoice.status, "SENT")
        self.assertEqual(invoice.total, total)
        self.assertEqual(invoice.tax, tax)
        self.assertEqual(invoice.subtotal, subtotal)
        self.assertEqual(invoice.balance, total)

    def test_dont_create_invoice_for_month_when_paused(self):
        """ An invoice shouldn't be created when a subscription is paused a full month """
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        account_subscription = subscription_pause.account_subscription
        account = account_subscription.account
        organization_subscription = account_subscription.organization_subscription
        price = f.OrganizationSubscriptionPriceFactory(organization_subscription=organization_subscription)
        finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)  # 100 = default

        date_start = account_subscription.date_start

        # Create an invoice with date today for first month of subscription
        result = account_subscription.create_invoice_for_month(
            year=date_start.year,
            month=date_start.month,
        )

        # Check that invoice (item) wasn't created
        self.assertEqual(result, None)

    def test_create_invoice_for_month_paused_partial_period(self):
        """ An invoice for a partial payment should be created when a """
        subscription_pause = f.AccountSubscriptionPauseFactory.create(
            date_end="2019-01-30"
        )
        account_subscription = subscription_pause.account_subscription
        account_subscription.registration_fee_paid = True
        account_subscription.save()

        account = account_subscription.account
        organization_subscription = account_subscription.organization_subscription
        price = f.OrganizationSubscriptionPriceFactory(organization_subscription=organization_subscription)
        finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)  # 100 = default

        date_start = account_subscription.date_start

        # Create an invoice with date today for first month of subscription
        result = account_subscription.create_invoice_for_month(
            year=date_start.year,
            month=date_start.month,
        )

        # Check if invoice was created
        invoice = models.FinanceInvoice.objects.all().first()
        sums = models.FinanceInvoiceItem.objects.filter(finance_invoice=invoice).aggregate(
            Sum('subtotal'), Sum('tax'), Sum('total')
        )

        subtotal = sums['subtotal__sum'] or 0
        tax = sums['tax__sum'] or 0
        total = sums['total__sum'] or 0

        # Check invoice fields
        self.assertEqual(invoice.summary, "Subscription invoice %s-%s" % (date_start.year, date_start.month))
        self.assertEqual(invoice.relation_contact_name, account.full_name)
        self.assertEqual(invoice.status, "SENT")
        self.assertEqual(invoice.total, total)
        self.assertEqual(invoice.tax, tax)
        self.assertEqual(invoice.subtotal, subtotal)
        self.assertEqual(invoice.balance, total)

        # Check amount calculation
        price_per_day = round(price.price / 31, 2)
        self.assertEqual(float(invoice.total), price_per_day)

    def test_create_invoice_for_month_alt_price(self):
        """ An invoice should apply an alt price if defined """
        alt_price = f.AccountSubscriptionAltPriceFactory.create()
        account_subscription = alt_price.account_subscription
        account_subscription.registration_fee_paid = True
        account_subscription.save()

        account = account_subscription.account
        organization_subscription = account_subscription.organization_subscription
        price = f.OrganizationSubscriptionPriceFactory(organization_subscription=organization_subscription)
        finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)  # 100 = default

        date_start = account_subscription.date_start

        # Create an invoice with date today for first month of subscription
        result = account_subscription.create_invoice_for_month(
            year=date_start.year,
            month=date_start.month,
        )

        # Check if invoice was created
        invoice = models.FinanceInvoice.objects.all().first()
        sums = models.FinanceInvoiceItem.objects.filter(finance_invoice=invoice).aggregate(
            Sum('subtotal'), Sum('tax'), Sum('total')
        )

        subtotal = sums['subtotal__sum'] or 0
        tax = sums['tax__sum'] or 0
        total = sums['total__sum'] or 0

        # Check invoice fields
        self.assertEqual(invoice.summary, "Subscription invoice %s-%s" % (date_start.year, date_start.month))
        self.assertEqual(invoice.relation_contact_name, account.full_name)
        self.assertEqual(invoice.status, "SENT")
        self.assertEqual(invoice.total, total)
        self.assertEqual(invoice.tax, tax)
        self.assertEqual(invoice.subtotal, subtotal)
        self.assertEqual(invoice.balance, total)

        # Check amount calculation
        self.assertEqual(invoice.total, alt_price.amount)

        # Check item description
        first_item = invoice.items.all().first()
        self.assertEqual(first_item.description, alt_price.description)
        self.assertEqual(first_item.total, alt_price.amount)

    def test_create_invoice_description(self):
        """ An invoice should apply an alt price if defined """
        account_subscription = f.AccountSubscriptionFactory.create()
        account = account_subscription.account
        organization_subscription = account_subscription.organization_subscription
        price = f.OrganizationSubscriptionPriceFactory(organization_subscription=organization_subscription)
        finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)  # 100 = default

        date_start = account_subscription.date_start

        # Create an invoice with date today for first month of subscription
        description = "description"
        account_subscription.create_invoice_for_month(
            year=date_start.year,
            month=date_start.month,
            description=description
        )

        # Check if invoice was created
        invoice = models.FinanceInvoice.objects.all().first()
        sums = models.FinanceInvoiceItem.objects.filter(finance_invoice=invoice).aggregate(
            Sum('subtotal'), Sum('tax'), Sum('total')
        )

        # Check invoice fields
        self.assertEqual(invoice.summary, "Subscription invoice %s-%s" % (date_start.year, date_start.month))

        # Check item description
        first_item = invoice.items.all().first()
        self.assertEqual(first_item.description, description)

    def test_create_invoice_description(self):
        """ An invoice should apply an alt price if defined """
        account_subscription = f.AccountSubscriptionFactory.create()
        account = account_subscription.account
        organization_subscription = account_subscription.organization_subscription
        price = f.OrganizationSubscriptionPriceFactory(organization_subscription=organization_subscription)
        finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)  # 100 = default

        date_start = account_subscription.date_start

        # Create an invoice with date today for first month of subscription
        description = "description"
        account_subscription.create_invoice_for_month(
            year=date_start.year,
            month=date_start.month,
            invoice_date="first_of_month"
        )

        # Check if invoice was created
        invoice = models.FinanceInvoice.objects.all().first()
        self.assertEqual(invoice.date_sent, date_start)
