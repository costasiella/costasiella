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

from ..tasks.account.subscription.enrollments.tasks import cancel_booked_classes_after_enrollment_end


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

    def test_classes_booked_after_enrollment_end_cancelled(self):
        """ Test adding subscription credits """
        class_date = datetime.date(2022, 1, 31)
        enrollment_end = class_date - datetime.timedelta(days=1)
        account_subscription = f.AccountSubscriptionFactory.create()
        schedule_item_attendance = f.ScheduleItemAttendanceSubscriptionFactory.create(
            date=class_date,
            account_subscription=account_subscription
        )
        schedule_item_enrollment = f.ScheduleItemEnrollmentFactory.create(
            account_subscription=account_subscription,
            schedule_item=schedule_item_attendance.schedule_item,
            date_end=enrollment_end
        )

        result = cancel_booked_classes_after_enrollment_end(
            account_subscription_id=schedule_item_enrollment.account_subscription.id,
            schedule_item_id=schedule_item_enrollment.schedule_item.id,
            cancel_bookings_from_date=schedule_item_enrollment.date_end
        )
        self.assertEqual(result, "OK")

        # Refetch attendance item and check status has been set to CANCELLED
        schedule_item_attendance = models.ScheduleItemAttendance.objects.get(id=schedule_item_attendance.id)
        self.assertEqual(schedule_item_attendance.booking_status, 'CANCELLED')
