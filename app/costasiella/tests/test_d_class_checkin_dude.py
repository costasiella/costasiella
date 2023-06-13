# This file holds tests for the finance invoice model as it has code to create invoice items
# These invoice items will change depending on values set in the database and should therefore be tested to be sure
# that the correct values are being set for the new invoice items.

import datetime

from django.test import TestCase
from ..modules.date_tools import last_day_month

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .. import dudes
from .. import models

from ..modules.cs_errors import \
    CSClassBookingSubscriptionAlreadyBookedError, \
    CSClassBookingSubscriptionBlockedError, \
    CSClassBookingSubscriptionPausedError, \
    CSClassBookingSubscriptionNoCreditsError



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

        # Expired credit
        account_subscription_credit_1 = f.AccountSubscriptionCreditFactory.create()
        account_subscription_credit_1.expiration = datetime.date(2020, 1, 1)
        account_subscription_credit_1.created_at = datetime.date(2020, 1, 1)
        account_subscription_credit_1.save()

        # Valid credit 1
        account_subscription_credit_2 = f.AccountSubscriptionCreditFactory.create(
            account_subscription=account_subscription_credit_1.account_subscription
        )
        account_subscription_credit_2.created_at = datetime.date(2020, 1, 1)
        account_subscription_credit_2.save()

        # Valid credit 2
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

    def test_subscription_checkin_unlimted_credit_granted(self):
        """
        Unlimitec subscriptions get credit on check-in
        :return:
        """
        from ..dudes import ClassCheckinDude

        class_checkin_dude = ClassCheckinDude()

        account_subscription = f.AccountSubscriptionFactory.create()
        organzation_subscription = account_subscription.organization_subscription
        organzation_subscription.unlimited = True
        organzation_subscription.classes = 0
        organzation_subscription.save()

        weekly_class = f.SchedulePublicWeeklyClassFactory.create()

        qs = models.AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription
        )
        self.assertEqual(qs.exists(), False)

        # Do check-in and there should be a credit.
        # Class takes place on a monday
        a_monday = datetime.date(2023, 1, 2)

        class_checkin_dude.class_checkin_subscription(
            account=account_subscription.account,
            account_subscription=account_subscription,
            schedule_item=weekly_class,
            date=a_monday
        )
        qs = models.AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription
        )
        self.assertEqual(qs.exists(), True)

    def test_subscription_checkin_limited_advance_credit_granted(self):
        """
        Check that an advance credit is granted
        :return:
        """
        from ..dudes import ClassCheckinDude

        class_checkin_dude = ClassCheckinDude()

        account_subscription = f.AccountSubscriptionFactory.create()
        organization_subscription = account_subscription.organization_subscription
        organization_subscription.unlimited = False
        organization_subscription.reconciliation_classes = 1
        organization_subscription.save()
        weekly_class = f.SchedulePublicWeeklyClassFactory.create()

        qs = models.AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription
        )
        self.assertEqual(qs.exists(), False)

        # Do check-in and there should be a credit.
        # Class takes place on a monday
        a_monday = datetime.date(2023, 1, 2)

        class_checkin_dude.class_checkin_subscription(
            account=account_subscription.account,
            account_subscription=account_subscription,
            schedule_item=weekly_class,
            date=a_monday
        )
        qs = models.AccountSubscriptionCredit.objects.filter(
            advance=True,
            account_subscription=account_subscription
        )
        self.assertEqual(qs.exists(), True)

    def test_subscription_checkin_without_credits_raises_no_credits_exception(self):
        """
        No Credits exception should be raised when trying to do a check-in without credits & not unlimited
        :return:
        """
        from ..dudes import ClassCheckinDude

        class_checkin_dude = ClassCheckinDude()

        account_subscription = f.AccountSubscriptionFactory.create()
        organization_subscription = account_subscription.organization_subscription
        organization_subscription.unlimited = False
        organization_subscription.reconciliation_classes = 0
        organization_subscription.save()
        weekly_class = f.SchedulePublicWeeklyClassFactory.create()

        qs = models.AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription
        )
        self.assertEqual(qs.exists(), False)

        # Do check-in and there should be a credit.
        # Class takes place on a monday
        a_monday = datetime.date(2023, 1, 2)

        self.assertRaises(
            CSClassBookingSubscriptionNoCreditsError,
            class_checkin_dude.class_checkin_subscription,
            account=account_subscription.account,
            account_subscription=account_subscription,
            schedule_item=weekly_class,
            date=a_monday
        )

    def test_subscription_checkin_expired_credits_raises_no_credits_exception(self):
        """
        No Credits exception should be raised when trying to do a check-in without credits & not unlimited
        :return:
        """
        from ..dudes import ClassCheckinDude

        class_checkin_dude = ClassCheckinDude()

        account_subscription_credit = f.AccountSubscriptionCreditFactory.create()
        # Expire one day before "a_monday" (scroll down)
        account_subscription_credit.expiration = datetime.date(2023, 1, 1)
        account_subscription_credit.save()
        account_subscription = account_subscription_credit.account_subscription
        organization_subscription = account_subscription.organization_subscription
        organization_subscription.unlimited = False
        organization_subscription.reconciliation_classes = 0
        organization_subscription.save()
        weekly_class = f.SchedulePublicWeeklyClassFactory.create()

        # Do check-in and there should be a credit.
        # Class takes place on a monday
        a_monday = datetime.date(2023, 1, 2)

        self.assertRaises(
            CSClassBookingSubscriptionNoCreditsError,
            class_checkin_dude.class_checkin_subscription,
            account=account_subscription.account,
            account_subscription=account_subscription,
            schedule_item=weekly_class,
            date=a_monday
        )
