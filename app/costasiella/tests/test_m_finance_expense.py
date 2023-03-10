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


class TestModelFinanceExpense(TestCase):
    fixtures = [
        'app_settings.json',
    ]

    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

    def tearDown(self):
        # This is run after every test
        pass

    def test_percentage_applied_to_total_fields(self):
        """ Test whether the percentage is correctly applied to the total fields"""
        today = timezone.now().date()

        finance_expense = f.FinanceExpenseFactory.create()
        percentage = finance_expense.percentage

        self.assertEqual(finance_expense.subtotal * (percentage / 100), finance_expense.total)
        self.assertEqual(finance_expense.amount * (percentage / 100), finance_expense.total_amount)
        self.assertEqual(finance_expense.tax * (percentage / 100), finance_expense.total_tax)
