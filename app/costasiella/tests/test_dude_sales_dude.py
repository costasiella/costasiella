# from graphql.error.located_error import GraphQLLocatedError
import graphql

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .. import models
from ..modules.gql_tools import get_rid
from .helpers import execute_test_client_api_query


class SalesDudeTestCase(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

    def tearDown(self):
        # This is run after every test
        pass

    def test_sell_schedule_event_ticket_add_schedule_item_attendances(self):
        """ Are all schedule item attendances added? """
        from ..dudes.sales_dude import SalesDude

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
