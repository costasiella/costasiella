# from graphql.error.located_error import GraphQLLocatedError
import graphql
import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser, Permission

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema

from ..tasks.account.subscription.credits.tasks import \
    account_subscription_credits_add_for_month, \
    account_subscription_credits_expire


class TaskAccountSubscriptionCredits(TestCase):
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

    def test_account_subscription_credits_add_for_month(self):
        """ Test adding subscription credits """
        account_subscription = f.AccountSubscriptionFactory.create()

        today = timezone.now().date()
        year = today.year
        month = today.month
        expected_credits = account_subscription._calculate_credits_for_month(year, month)
        result = account_subscription_credits_add_for_month(year, month)
        self.assertEqual(result, "Added credits for 1 subscriptions")

        # Check expiration amount
        add_mutation = models.AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription,
            mutation_type="ADD"
        ).first()
        self.assertEqual(float(add_mutation.mutation_amount), expected_credits)
        self.assertEqual(add_mutation.subscription_year, year)
        self.assertEqual(add_mutation.subscription_month, month)

    def test_expire_subscription_credits(self):
        """ Test credit expiration """
        account_subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        account_subscription = account_subscription_credit.account_subscription
        account_subscription_credit.created_at = account_subscription_credit.created_at - datetime.timedelta(days=100)
        account_subscription_credit.save()

        # Start credits expiration
        result = account_subscription_credits_expire()
        # Check result message
        self.assertEqual(result, "Expired credits for 1 subscriptions")

        # Check expiration amount
        sub_mutation = models.AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription,
            mutation_type="SUB"
        ).first()
        self.assertEqual(sub_mutation.mutation_amount, account_subscription_credit.mutation_amount)

