# from graphql.error.located_error import GraphQLLocatedError
import os
import shutil
import graphql
import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema

from app.settings.development import MEDIA_ROOT


class GQLScheduleEventEarlybird(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleeventearlybird'
        self.permission_add = 'add_scheduleeventearlybird'
        self.permission_change = 'change_scheduleeventearlybird'
        self.permission_delete = 'delete_scheduleeventearlybird'

        self.schedule_event_earlybird = f.ScheduleEventEarlybirdFactory.create()

        self.variables_query_list = {
            "scheduleEvent": to_global_id("ScheduleEventNode", self.schedule_event_earlybird.schedule_event.id)
        }

        self.variables_query_one = {
            "id": to_global_id("ScheduleEventEarlybirdNode", self.schedule_event_earlybird.id)
        }

        self.variables_create = {
            "input": {
                "scheduleEvent": to_global_id("ScheduleEventNode", self.schedule_event_earlybird.schedule_event.id),
                "dateStart": "2020-01-01",
                "dateEnd": "2999-12-31",
                "discountPercentage": "50",
            }
        }

        self.variables_update = {
            "input": {
                "id": to_global_id("ScheduleEventEarlybirdNode", self.schedule_event_earlybird.id),
                "dateStart": "2020-01-01",
                "dateEnd": "2999-12-31",
                "discountPercentage": "50",
            }
        }

        self.variables_delete = {
            "input": {
                "id": to_global_id('ScheduleEventEarlybirdNode', self.schedule_event_earlybird.id),
            }
        }

        self.schedule_event_earlybirds_query = '''
  query ScheduleEventEarlybirds($before:String, $after:String, $scheduleEvent:ID!) {
    scheduleEventEarlybirds(first: 100, before:$before, after:$after, scheduleEvent:$scheduleEvent) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          scheduleEvent {
            id
          }
          dateStart
          dateEnd
          discountPercentage
        }
      }
    }
  }
'''

        self.schedule_event_earlybird_query = '''
  query ScheduleEventEarlybird($id:ID!) {
    scheduleEventEarlybird(id: $id) {
      id
      scheduleEvent {
        id
      }
      dateStart
      dateEnd
      discountPercentage
    }
  }
'''

        self.schedule_event_earlybird_create_mutation = ''' 
  mutation CreateScheduleEventEarlybird($input:CreateScheduleEventEarlybirdInput!) {
    createScheduleEventEarlybird(input: $input) {
      scheduleEventEarlybird {
        id
        scheduleEvent {
          id
        }
        dateStart
        dateEnd
        discountPercentage
      }
    }
  }
'''

        self.schedule_event_earlybird_update_mutation = '''
  mutation UpdateScheduleEventEarlybird($input:UpdateScheduleEventEarlybirdInput!) {
    updateScheduleEventEarlybird(input: $input) {
      scheduleEventEarlybird {
        id
        scheduleEvent {
          id
        }
        dateStart
        dateEnd
        discountPercentage
      }
    }
  }
'''

        self.schedule_event_earlybird_delete_mutation = '''
  mutation DeleteScheduleEventEarlybird($input: DeleteScheduleEventEarlybirdInput!) {
    deleteScheduleEventEarlybird(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of schedule event earlybirds """
        query = self.schedule_event_earlybirds_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['scheduleEventEarlybirds']['edges'][0]['node']['id'],
            to_global_id('ScheduleEventEarlybirdNode', self.schedule_event_earlybird.id)
        )
        self.assertEqual(
            data['scheduleEventEarlybirds']['edges'][0]['node']['scheduleEvent']['id'],
            to_global_id('ScheduleEventNode', self.schedule_event_earlybird.schedule_event.id)
        )
        self.assertEqual(data['scheduleEventEarlybirds']['edges'][0]['node']['dateStart'],
                         str(self.schedule_event_earlybird.date_start))
        self.assertEqual(data['scheduleEventEarlybirds']['edges'][0]['node']['dateEnd'],
                         str(self.schedule_event_earlybird.date_end))

    def test_query_non_public_not_displayed(self):
        """ Query list of earlybird discounts - check non public """
        query = self.schedule_event_earlybirds_query
        schedule_event = self.schedule_event_earlybird.schedule_event
        schedule_event.display_public = False
        schedule_event.display_shop = False
        schedule_event.save()

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(len(data['scheduleEventEarlybirds']['edges']), 0)

    def test_query_anon_user_can_query_public_discounts(self):
        """ Query list of earlybird discounts as anon user """
        query = self.schedule_event_earlybirds_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
        errors = executed.get('errors')
        data = executed.get('data')

        self.assertEqual(
            data['scheduleEventEarlybirds']['edges'][0]['node']['id'],
            to_global_id('ScheduleEventEarlybirdNode', self.schedule_event_earlybird.id)
        )

    def test_query_one(self):
        """ Query one schedule event earlybird """
        query = self.schedule_event_earlybird_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['scheduleEventEarlybird']['id'], self.variables_query_one['id'])
        self.assertEqual(
            data['scheduleEventEarlybird']['scheduleEvent']['id'],
            to_global_id('ScheduleEventNode', self.schedule_event_earlybird.schedule_event.id)
        )
        self.assertEqual(data['scheduleEventEarlybird']['dateStart'],
                         str(self.schedule_event_earlybird.date_start))
        self.assertEqual(data['scheduleEventEarlybird']['dateEnd'],
                         str(self.schedule_event_earlybird.date_end))

    def test_query_one_dont_display_non_public(self):
        """ Query one schedule event earlybird """
        query = self.schedule_event_earlybird_query
        schedule_event = self.schedule_event_earlybird.schedule_event
        schedule_event.display_public = False
        schedule_event.display_shop = False
        schedule_event.save()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['scheduleEventEarlybird']['id'], self.variables_query_one['id'])

    def test_query_one_dont_display_non_public_anon(self):
        """ Query one schedule event earlybird """
        query = self.schedule_event_earlybird_query
        schedule_event = self.schedule_event_earlybird.schedule_event
        schedule_event.display_public = False
        schedule_event.display_shop = False
        schedule_event.save()

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['scheduleEventEarlybird'], None)

    def test_query_one_display_public_anon(self):
        """ Query one schedule event earlybird """
        query = self.schedule_event_earlybird_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['scheduleEventEarlybird']['id'], self.variables_query_one['id'])

    def test_create_schedule_event_earlybird(self):
        """ Create schedule event earlybird """
        query = self.schedule_event_earlybird_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['createScheduleEventEarlybird']['scheduleEventEarlybird']['scheduleEvent']['id'],
                         variables['input']['scheduleEvent'])
        self.assertEqual(data['createScheduleEventEarlybird']['scheduleEventEarlybird']['dateStart'],
                         variables['input']['dateStart'])
        self.assertEqual(data['createScheduleEventEarlybird']['scheduleEventEarlybird']['dateEnd'],
                         variables['input']['dateEnd'])
        self.assertEqual(data['createScheduleEventEarlybird']['scheduleEventEarlybird']['discountPercentage'],
                         variables['input']['discountPercentage'])

    def test_create_schedule_event_earlybird_anon_user(self):
        """ Don't allow creating schedule event earlybird for non-logged in users """
        query = self.schedule_event_earlybird_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_schedule_event_earlybird_permission_granted(self):
        """ Allow creating schedule event earlybird for users with permissions """
        query = self.schedule_event_earlybird_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createScheduleEventEarlybird']['scheduleEventEarlybird']['discountPercentage'],
                         variables['input']['discountPercentage'])

    def test_create_schedule_event_earlybird_permission_denied(self):
        """ Check create schedule event earlybird permission denied error message """
        query = self.schedule_event_earlybird_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_schedule_event_earlybird(self):
        """ Update schedule event earlybird """
        query = self.schedule_event_earlybird_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateScheduleEventEarlybird']['scheduleEventEarlybird']['dateStart'],
                         variables['input']['dateStart'])
        self.assertEqual(data['updateScheduleEventEarlybird']['scheduleEventEarlybird']['dateEnd'],
                         variables['input']['dateEnd'])
        self.assertEqual(data['updateScheduleEventEarlybird']['scheduleEventEarlybird']['discountPercentage'],
                         variables['input']['discountPercentage'])

    def test_update_schedule_event_earlybird_anon_user(self):
        """ Don't allow updating schedule event earlybird for non-logged in users """
        query = self.schedule_event_earlybird_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_schedule_event_earlybird_permission_granted(self):
        """ Allow updating schedule event earlybird for users with permissions """
        query = self.schedule_event_earlybird_update_mutation
        variables = self.variables_update

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateScheduleEventEarlybird']['scheduleEventEarlybird']['discountPercentage'],
                         variables['input']['discountPercentage'])

    def test_update_schedule_event_earlybird_permission_denied(self):
        """ Check update schedule event earlybird permission denied error message """
        query = self.schedule_event_earlybird_update_mutation
        variables = self.variables_update

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_schedule_event_earlybird(self):
        """ Delete a schedule event earlybird """
        query = self.schedule_event_earlybird_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['deleteScheduleEventEarlybird']['ok'], True)

    def test_delete_schedule_event_earlybird_anon_user(self):
        """ Delete a schedule event earlybird """
        query = self.schedule_event_earlybird_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_schedule_event_earlybird_permission_granted(self):
        """ Allow deleting schedule event earlybirds for users with permissions """
        query = self.schedule_event_earlybird_delete_mutation
        variables = self.variables_delete

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleEventEarlybird']['ok'], True)

    def test_delete_schedule_event_earlybird_permission_denied(self):
        """ Check delete schedule event earlybird permission denied error message """
        query = self.schedule_event_earlybird_delete_mutation
        variables = self.variables_delete

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
