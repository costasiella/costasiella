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
from .. import dudes
from .. import models
from .. import schema

from ..tasks.account.subscription.invoices.tasks import account_subscription_invoices_add_for_month


class TestDudeClassCheckinDude(TestCase):
    fixtures = [
        'app_settings.json',
        'finance_invoice_group.json',
        'finance_invoice_group_defaults.json',
        'finance_payment_methods.json',
        'organization.json',
        'system_mail_template'
    ]

    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()
        self.sales_dude = dudes.SalesDude()

    def tearDown(self):
        # This is run after every test
        pass

    def test_subscription_checkin_use_earliest_valid_credit(self):
        """

        :return:
        """
        from ..dudes import ClassCheckinDude

        class_checkin_dude = ClassCheckinDude()

        account_subscription_credit_1 = f.AccountSubscriptionCreditFactory.create()
        account_subscription_credit_1.expiration = datetime.date(2020, 1, 1)
        account_subscription_credit_1.created_at = datetime.date(2020, 1, 1)
        account_subscription_credit_1.save()
        account_subscription_credit_2 = f.AccountSubscriptionCreditFactory.create(
            account_subscription=account_subscription_credit_1.account_subscription
        )
        account_subscription_credit_2.created_at = datetime.date(2020, 1, 1)
        account_subscription_credit_2.save()
        account_subscription_credit_3 = f.AccountSubscriptionCreditFactory.create(
            account_subscription=account_subscription_credit_1.account_subscription
        )

        # Now do a check-in, and the 2nd credit should be used. It's the oldest one that's still valid.
        weekly_class = f.SchedulePublicWeeklyClassFactory.create()

        # Class takes place on a monday
        a_monday = datetime.date(2023, 1, 2)

        # Do the check-in
        account_subscription = account_subscription_credit_1.account_subscription
        account = account_subscription.account

        class_checkin_dude.class_checkin_subscription(
            account=account,
            account_subscription=account_subscription,
            schedule_item=weekly_class,
            date=a_monday
        )

        # Fetch credits from db and check booking
        # 1 is expired, so shouldn't be used
        credit_1 = models.AccountSubscriptionCredit.objects.get(id=account_subscription_credit_1.id)
        self.assertEqual(credit_1.schedule_item_attendance, None)
        # 2 is the oldest one valid, so should be used
        credit_2 = models.AccountSubscriptionCredit.objects.get(id=account_subscription_credit_2.id)
        self.assertNotEqual(credit_2.schedule_item_attendance, None)
        # 3 is the latest, so shouldn't be used yet
        credit_3 = models.AccountSubscriptionCredit.objects.get(id=account_subscription_credit_3.id)
        self.assertEqual(credit_3.schedule_item_attendance, None)

        
