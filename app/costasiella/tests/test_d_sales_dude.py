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


class TestDudeSalesDude(TestCase):
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
        self.sales_dude = dudes.SalesDude()

    def tearDown(self):
        # This is run after every test
        pass

    def test_dont_sell_trialpass_when_over_limit(self):
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

        self.assertRaises(
            Exception,
            self.sales_dude.sell_classpass,
            account=account,
            organization_classpass=organization_classpass,
            date_start=datetime.date.today(), note="", create_invoice=True
        )

    def test_sell_schedule_event_ticket_add_schedule_item_attendances(self):
        """ Are all schedule item attendances added? """
        from ..dudes import SalesDude

        account = f.RegularUserFactory.create()
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create(
            schedule_event=schedule_event_ticket.schedule_event
        )
        schedule_event_ticket_schedule_item = f.ScheduleEventTicketScheduleItemIncludedFactory.create(
            schedule_item=schedule_event_activity,
            schedule_event_ticket=schedule_event_ticket
        )

        sales_dude = SalesDude()
        sales_result = sales_dude.sell_schedule_event_ticket(
            account,
            schedule_event_ticket,
            create_invoice=False
        )
        account_schedule_event_ticket = sales_result['account_schedule_event_ticket']

        # Check a schedule item has been added
        schedule_item_attendance = models.ScheduleItemAttendance.objects.last()
        self.assertEqual(schedule_item_attendance.account_schedule_event_ticket, account_schedule_event_ticket)
        self.assertEqual(schedule_item_attendance.schedule_item, schedule_event_activity)

    def test_sell_subscrition_add_credits_for_next_month_when_startdate_day_of_month_gte_15(self):
        """
        Are credits for the next month added?
        The trick here is that next_month_credits_after_day are set to 1, when selling the subscription
        :return:
        """
        from ..dudes import DateToolsDude, SalesDude

        # Sell subscription
        organization_subscription_price = f.OrganizationSubscriptionPriceFactory.create()
        organization_subscription = organization_subscription_price.organization_subscription
        account = f.RegularUserFactory.create()

        direct_debit_payment_method = models.FinancePaymentMethod.objects.get(id=103)

        today = timezone.now().date()
        sales_dude = SalesDude()
        result = sales_dude.sell_subscription(
            account=account,
            organization_subscription=organization_subscription,
            date_start=today,
            finance_payment_method=direct_debit_payment_method,
            next_month_credits_after_day=1
        )

        account_subscription = result['account_subscription']

        # Check if cedits were added for current and next month
        qs_credits_current_month = models.AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription,
            subscription_year=today.year,
            subscription_month=today.month
        )
        self.assertEqual(qs_credits_current_month.exists(), True)

        # Next month
        date_tools_dude = DateToolsDude()
        first_day_next_month = date_tools_dude.get_first_day_of_next_month_from_date(today)
        qs_credits_next_month = models.AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription,
            subscription_year=first_day_next_month.year,
            subscription_month=first_day_next_month.month
        )
        self.assertEqual(qs_credits_next_month.exists(), True)
