# from graphql.error.located_error import GraphQLLocatedError
import datetime
import graphql

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils import timezone
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema
from ..modules.finance_tools import display_float_as_amount
from ..modules.validity_tools import display_validity_unit

from graphql_relay import to_global_id


class GQLInsightClassAttendance(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleitemattendance'

        self.schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        self.schedule_item_attendance.date = datetime.date(2029, 12, 31)
        self.schedule_item_attendance.save()

        self.variables_query = {
            'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item_attendance.schedule_item.id),
            'year': 2030
        }   

        self.query_class_attendance = '''
  query InsightClassAttendanceQuery($year: Int!, $scheduleItem: ID!) {
    insightClassAttendanceCountYear(scheduleItem: $scheduleItem, year: $year) {
      year
      scheduleItem {
        id
      }
      weeks {
        week
        attendanceCountCurrentYear
        attendanceCountPreviousYear
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query_class_attendance(self):
        """ Query class attendance for given year """
        query = self.query_class_attendance

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightClassAttendanceCountYear']['year'], self.variables_query['year'])
        self.assertEqual(data['insightClassAttendanceCountYear']['scheduleItem']['id'],
                         self.variables_query['scheduleItem'])
        self.assertEqual(data['insightClassAttendanceCountYear']['weeks'][0]['attendanceCountCurrentYear'], 1)
        self.assertEqual(data['insightClassAttendanceCountYear']['weeks'][1]['attendanceCountCurrentYear'], 0)
        self.assertEqual(data['insightClassAttendanceCountYear']['weeks'][0]['attendanceCountPreviousYear'], 0)
        self.assertEqual(data['insightClassAttendanceCountYear']['weeks'][52]['attendanceCountPreviousYear'], 1)
        # self.assertEqual(data['insightClassAttendanceCountYear']['dataCurrent'][0], 1)
        # self.assertEqual(data['insightClassAttendanceCountYear']['dataCurrent'][1], 0)
        # self.assertEqual(data['insightClassAttendanceCountYear']['dataPrevious'][0], 0)
        # self.assertEqual(data['insightClassAttendanceCountYear']['dataPrevious'][52], 1)

    def test_query_total_permission_denied(self):
        """ Query class attendance for given year - check permission denied """
        query = self.query_class_attendance

        # Create regular user
        user = self.schedule_item_attendance.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_total_permission_granted(self):
        """ Query class attendance for given year - check permission granted """
        query = self.query_class_attendance

        # Create regular user
        user = self.schedule_item_attendance.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightClassAttendanceCountYear']['year'], self.variables_query['year'])

    def test_query_total_anon_user(self):
        """ Query class attendance for given year - anon user """
        query = self.query_class_attendance

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
