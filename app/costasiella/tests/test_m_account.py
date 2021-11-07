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


class TestModelAccount(TestCase):
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

    def test_has_reached_trial_limit(self):
        """
        Test if the trial limit reached method functions correctly
        """
        account_classpass = f.AccountClasspassFactory.create()
        account = account_classpass.account
        organization_classpass = account_classpass.organization_classpass
        organization_classpass.trial_pass = True
        organization_classpass.save()

        setting = models.SystemSetting(
            setting="workflow_trial_pass_limit",
            value="1"
        )
        setting.save()

        limit_reached = account.has_reached_trial_limit()
        self.assertEqual(limit_reached, True)


    def test_has_not_reached_trial_limit(self):
        """
        Test if the trial limit reached method functions correctly
        """
        account_classpass = f.AccountClasspassFactory.create()
        account = account_classpass.account
        organization_classpass = account_classpass.organization_classpass
        organization_classpass.trial_pass = True
        organization_classpass.save()

        setting = models.SystemSetting(
            setting="workflow_trial_pass_limit",
            value="20"
        )
        setting.save()

        limit_reached = account.has_reached_trial_limit()
        self.assertEqual(limit_reached, False)
