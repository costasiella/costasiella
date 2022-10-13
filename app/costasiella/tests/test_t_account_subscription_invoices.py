# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser, Permission

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema

from ..tasks.account.subscription.invoices.tasks import account_subscription_invoices_add_for_month


class TaskAccountSubscriptionInvoices(TestCase):
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

    def test_create_monthly_subscription_invoices(self):
        """ Test creating monthly subscription invoices """
        account_subscription = f.AccountSubscriptionFactory.create()
        organization_subscription = account_subscription.organization_subscription
        price = f.OrganizationSubscriptionPriceFactory(organization_subscription=organization_subscription)

        date_start = account_subscription.date_start

        # Create an invoice with date today for first month of subscription
        account_subscription_invoices_add_for_month(
            year=date_start.year,
            month=date_start.month,
            invoice_date="first_of_month"
        )

        # Check that an invoice was created
        invoice = models.FinanceInvoice.objects.all().first()
        self.assertEqual(invoice.date_sent, date_start)

        # Assert main points of invoice item are correct
        first_item = invoice.items.all().first()
        self.assertEqual(first_item.price, price.price)
        self.assertEqual(first_item.account_subscription, account_subscription)
        self.assertEqual(first_item.subscription_year, date_start.year)
        self.assertEqual(first_item.subscription_month, date_start.month)
