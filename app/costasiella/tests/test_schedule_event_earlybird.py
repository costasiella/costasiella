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
from .helpers import clean_earlybird, execute_test_client_api_query
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

        self.schedule_event_earlybird = f.ScheduleEventMediaFactory.create()

        self.variables_query_list = {
            "scheduleEvent": to_global_id("ScheduleEventNode", self.schedule_event_earlybird.schedule_event.id)
        }

        self.variables_query_one = {
            "id": to_global_id("ScheduleEventMediaNode", self.schedule_event_earlybird.id)
        }

        self.variables_create = {
            "input": {
              "scheduleEvent": to_global_id("ScheduleEventNode", self.schedule_event_earlybird.schedule_event.id),
              "sortOrder": 0,
              "description": "test_image.jpg",
              "imageFileName": "test_image.jpg",
            }
        }

        self.variables_update = {
            "input": {
                "id": to_global_id("ScheduleEventMediaNode", self.schedule_event_earlybird.id),
                "sortOrder": 2,
                "description": "test_image.jpg",
                "imageFileName": "test_image.jpg",
            }
        }

        self.variables_delete = {
            "input": {
                "id": to_global_id('OrganizationDocumentNode', self.schedule_event_earlybird.id),
            }
        }

        self.schedule_event_earlybirds_query = '''
  query ScheduleEventEarlybirdss($before:String, $after:String, $scheduleEvent:ID!) {
    scheduleEventEarlybirdss(first: 100, before:$before, after:$after, scheduleEvent:$scheduleEvent) {
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
  query ScheduleEventMedia($id:ID!) {
    scheduleEventMedia(id: $id) {
      id
      sortOrder
      description
      urlImage
    }
  }
'''

        self.schedule_event_earlybird_create_mutation = ''' 
  mutation CreateScheduleEventMedia($input:CreateScheduleEventMediaInput!) {
    createScheduleEventMedia(input: $input) {
      scheduleEventMedia {
        id
        sortOrder
        description
        urlImage
      }
    }
  }
'''

        self.schedule_event_earlybird_update_mutation = '''
  mutation UpdateScheduleEventMedia($input:UpdateScheduleEventMediaInput!) {
    updateScheduleEventMedia(input: $input) {
      scheduleEventMedia {
        id
        sortOrder
        description
        urlImage
      }
    }
  }
'''

        self.schedule_event_earlybird_delete_mutation = '''
  mutation DeleteScheduleEventMedia($input: DeleteScheduleEventMediaInput!) {
    deleteScheduleEventMedia(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        clean_earlybird()

    def test_query(self):
        """ Query list of schedule event earlybirds """
        query = self.schedule_event_earlybirds_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['scheduleEventMedias']['edges'][0]['node']['id'],
            to_global_id('ScheduleEventMediaNode', self.schedule_event_earlybird.id)
        )
        self.assertEqual(data['scheduleEventMedias']['edges'][0]['node']['sortOrder'],
                         self.schedule_event_earlybird.sort_order)
        self.assertEqual(data['scheduleEventMedias']['edges'][0]['node']['description'],
                         self.schedule_event_earlybird.description)
        self.assertNotEqual(data['scheduleEventMedias']['edges'][0]['node']['urlImage'], False)
        self.assertNotEqual(data['scheduleEventMedias']['edges'][0]['node']['urlImageThumbnailSmall'], False)

    ##
    # No permission tests are required in this test, as there are no permission checks in the schema.
    # The listing of these documents is public, so users also don't need to be logged in.
    ##

    def test_query_one(self):
        """ Query one schedule event earlybird """
        query = self.schedule_event_earlybird_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['scheduleEventMedia']['id'], self.variables_query_one['id'])

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

        self.assertEqual(data['createScheduleEventMedia']['scheduleEventMedia']['sortOrder'],
                         variables['input']['sortOrder'])
        self.assertEqual(data['createScheduleEventMedia']['scheduleEventMedia']['description'],
                         variables['input']['description'])
        self.assertNotEqual(data['createScheduleEventMedia']['scheduleEventMedia']['urlImage'], "")

        schedule_event_earlybird = models.ScheduleEventMedia.objects.last()
        self.assertNotEqual(schedule_event_earlybird.image, None)

    def test_create_schedule_event_earlybird_anon_user(self):
        """ Don't allow creating schedule event earlybird for non-logged in users """
        query = self.schedule_event_earlybird_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
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
        self.assertEqual(data['createScheduleEventMedia']['scheduleEventMedia']['sortOrder'],
                         variables['input']['sortOrder'])

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
        data = executed.get('data')
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
        self.assertEqual(data['updateScheduleEventMedia']['scheduleEventMedia']['sortOrder'],
                         variables['input']['sortOrder'])
        self.assertEqual(data['updateScheduleEventMedia']['scheduleEventMedia']['description'],
                         variables['input']['description'])
        self.assertNotEqual(data['updateScheduleEventMedia']['scheduleEventMedia']['urlImage'], "")

        schedule_event_earlybird = models.ScheduleEventMedia.objects.last()
        self.assertNotEqual(schedule_event_earlybird.image, None)

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
        self.assertEqual(data['updateScheduleEventMedia']['scheduleEventMedia']['sortOrder'],
                         variables['input']['sortOrder'])

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

        self.assertEqual(data['deleteScheduleEventMedia']['ok'], True)

        exists = models.OrganizationDocument.objects.exists()
        self.assertEqual(exists, False)

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
        self.assertEqual(data['deleteScheduleEventMedia']['ok'], True)

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
