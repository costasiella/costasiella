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


class GQLInsightInstructorClassesMonth(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_insightinstructorclassesmonth'


        self.schedule_item_account = f.ScheduleItemAccountFactory.create()
        instructor =  self.schedule_item_account.account

        self.variables_query = {
            'instructor': to_global_id('AccountNode', instructor.id),
            'year': 2023,
            'month': 1
        }   

        self.query_instructor_classes_month = '''
query InsightInstructorClassesMonth($year:Int!, $month:Int!, $instructor: ID!) {
  insightInstructorClassesMonth(year: $year, month:$month, instructor: $instructor) {
    year
    month
    instructor
    classes {
      scheduleItemId,
    }
  }
}
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query_instructor_classes_month(self):
        """ Query instructor classes for given year & month """
        query = self.query_instructor_classes_month

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightInstructorClassesMonth']['year'], self.variables_query['year'])
        self.assertEqual(data['insightInstructorClassesMonth']['month'], self.variables_query['month'])
        self.assertEqual(data['insightInstructorClassesMonth']['classes'][0]['scheduleItemId'],
                         to_global_id('ScheduleItemNode', self.schedule_item_account.schedule_item.id))
        self.assertEqual(data['insightInstructorClassesMonth']['classes'][1]['scheduleItemId'],
                         to_global_id('ScheduleItemNode', self.schedule_item_account.schedule_item.id))
        self.assertEqual(data['insightInstructorClassesMonth']['classes'][2]['scheduleItemId'],
                         to_global_id('ScheduleItemNode', self.schedule_item_account.schedule_item.id))
        self.assertEqual(data['insightInstructorClassesMonth']['classes'][3]['scheduleItemId'],
                         to_global_id('ScheduleItemNode', self.schedule_item_account.schedule_item.id))
        self.assertEqual(data['insightInstructorClassesMonth']['classes'][4]['scheduleItemId'],
                         to_global_id('ScheduleItemNode', self.schedule_item_account.schedule_item.id))

    def test_query_total_permission_denied(self):
        """ Query instructor classes for given year & month - check permission denied """
        query = self.query_instructor_classes_month

        # Create regular user
        user = self.schedule_item_account.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_total_permission_granted(self):
        """ Query class attendance for given year - check permission granted """
        query = self.query_instructor_classes_month

        # Create regular user
        user = self.schedule_item_account.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightInstructorClassesMonth']['year'], self.variables_query['year'])

    def test_query_total_anon_user(self):
        """ Query instructor classes for given year & month - anon user """
        query = self.query_instructor_classes_month

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
