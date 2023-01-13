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
    account_subscription_credits_add_for_month


class TaskAccountSubscriptionCredits(TestCase):
    fixtures = [
        'app_settings.json',
        'finance_invoice_group.json',
        'finance_invoice_group_defaults.json',
        'finance_payment_methods.json',
        'organization.json',
        'system_mail_template.json'
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

        # Check number of credits added
        qs = models.AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription
        )
        self.assertEqual(qs.count(), expected_credits)
        # Check contents of first credit given
        first_credit = qs.first()
        # Check credit expiration
        organization_subscription = account_subscription.organization_subscription
        credit_validity = organization_subscription.credit_validity
        expected_expiration = today + datetime.timedelta(days=credit_validity)
        self.assertEqual(first_credit.expiration, expected_expiration)
        # Check subscription year & month are set
        self.assertEqual(first_credit.subscription_year, year)
        self.assertEqual(first_credit.subscription_month, month)

    def test_account_subscription_credits_add_for_month_process_enrollments(self):
        """ Are enrolled classes booked """
        schedule_item_enrollment = f.ScheduleItemEnrollmentFactory.create()
        account_subscription = schedule_item_enrollment.account_subscription

        today = timezone.now().date()
        year = today.year
        month = today.month
        expected_credits = account_subscription._calculate_credits_for_month(year, month)
        result = account_subscription_credits_add_for_month(year, month)
        self.assertEqual(result, "Added credits for 1 subscriptions")

        # Check classes booked
        classes_booked = models.ScheduleItemAttendance.objects.filter(account_subscription=account_subscription)
        self.assertEqual(len(classes_booked) > 1, True)
