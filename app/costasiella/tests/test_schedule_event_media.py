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
from .helpers import clean_media, execute_test_client_api_query
from .. import models
from .. import schema

from app.settings.development import MEDIA_ROOT


class GQLScheduleEventMedia(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleeventmedia'
        self.permission_add = 'add_scheduleeventmedia'
        self.permission_change = 'change_scheduleeventmedia'
        self.permission_delete = 'delete_scheduleeventmedia'

        self.schedule_event_media = f.ScheduleEventMediaFactory.create()

        self.variables_query_list = {
            "scheduleEvent": to_global_id("ScheduleEventNode", self.schedule_event_media.schedule_event.id)
        }

        self.variables_query_one = {
            "id": to_global_id("ScheduleEventMediaNode", self.schedule_event_media.id)
        }

        with open(os.path.join(os.getcwd(), "costasiella", "tests", "files", "test_image.txt"), 'r') as input_file:
            input_image = input_file.read().replace("\n", "")

            self.variables_create = {
                "input": {
                  "scheduleEvent": to_global_id("ScheduleEventNode", self.schedule_event_media.schedule_event.id),
                  "sortOrder": 0,
                  "description": "test_image.jpg",
                  "imageFileName": "test_image.jpg",
                  "image": input_image
                }
            }

            self.variables_update = {
                "input": {
                    "id": to_global_id("ScheduleEventMediaNode", self.schedule_event_media.id),
                    "sortOrder": 2,
                    "description": "test_image.jpg",
                    "imageFileName": "test_image.jpg",
                    "image": input_image
                }
            }

        self.variables_delete = {
            "input": {
                "id": to_global_id('OrganizationDocumentNode', self.schedule_event_media.id),
            }
        }

        self.schedule_event_medias_query = '''
  query ScheduleEventMedias($before:String, $after:String, $scheduleEvent:ID!) {
    scheduleEventMedias(first: 100, before:$before, after:$after, scheduleEvent:$scheduleEvent) {
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
          sortOrder
          description
          urlImage
          urlImageThumbnailSmall
          image
        }
      }
    }
  }
'''

        self.schedule_event_media_query = '''
  query ScheduleEventMedia($id:ID!) {
    scheduleEventMedia(id: $id) {
      id
      sortOrder
      description
      urlImage
    }
  }
'''

        self.schedule_event_media_create_mutation = ''' 
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

        self.schedule_event_media_update_mutation = '''
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

        self.schedule_event_media_delete_mutation = '''
  mutation DeleteScheduleEventMedia($input: DeleteScheduleEventMediaInput!) {
    deleteScheduleEventMedia(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        clean_media()

    def test_query(self):
        """ Query list of schedule event medias """
        query = self.schedule_event_medias_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['scheduleEventMedias']['edges'][0]['node']['id'],
            to_global_id('ScheduleEventMediaNode', self.schedule_event_media.id)
        )
        self.assertEqual(data['scheduleEventMedias']['edges'][0]['node']['sortOrder'],
                         self.schedule_event_media.sort_order)
        self.assertEqual(data['scheduleEventMedias']['edges'][0]['node']['description'],
                         self.schedule_event_media.description)
        self.assertNotEqual(data['scheduleEventMedias']['edges'][0]['node']['urlImage'], False)
        self.assertNotEqual(data['scheduleEventMedias']['edges'][0]['node']['urlImageThumbnailSmall'], False)

    ##
    # No permission tests are required in this test, as there are no permission checks in the schema.
    # The listing of these documents is public, so users also don't need to be logged in.
    ##

    def test_query_one(self):
        """ Query one schedule event media """
        query = self.schedule_event_media_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['scheduleEventMedia']['id'], self.variables_query_one['id'])

    def test_create_schedule_event_media(self):
        """ Create schedule event media """
        query = self.schedule_event_media_create_mutation
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

        schedule_event_media = models.ScheduleEventMedia.objects.last()
        self.assertNotEqual(schedule_event_media.image, None)

    def test_create_schedule_event_media_anon_user(self):
        """ Don't allow creating schedule event media for non-logged in users """
        query = self.schedule_event_media_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_schedule_event_media_permission_granted(self):
        """ Allow creating schedule event media for users with permissions """
        query = self.schedule_event_media_create_mutation

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

    def test_create_schedule_event_media_permission_denied(self):
        """ Check create schedule event media permission denied error message """
        query = self.schedule_event_media_create_mutation
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

    def test_update_schedule_event_media(self):
        """ Update schedule event media """
        query = self.schedule_event_media_update_mutation
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

        schedule_event_media = models.ScheduleEventMedia.objects.last()
        self.assertNotEqual(schedule_event_media.image, None)

    def test_update_schedule_event_media_anon_user(self):
        """ Don't allow updating schedule event media for non-logged in users """
        query = self.schedule_event_media_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_schedule_event_media_permission_granted(self):
        """ Allow updating schedule event media for users with permissions """
        query = self.schedule_event_media_update_mutation
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

    def test_update_schedule_event_media_permission_denied(self):
        """ Check update schedule event media permission denied error message """
        query = self.schedule_event_media_update_mutation
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

    def test_delete_schedule_event_media(self):
        """ Delete a schedule event media """
        query = self.schedule_event_media_delete_mutation
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

    def test_delete_schedule_event_media_anon_user(self):
        """ Delete a schedule event media """
        query = self.schedule_event_media_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_schedule_event_media_permission_granted(self):
        """ Allow deleting schedule event medias for users with permissions """
        query = self.schedule_event_media_delete_mutation
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

    def test_delete_schedule_event_media_permission_denied(self):
        """ Check delete schedule event media permission denied error message """
        query = self.schedule_event_media_delete_mutation
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
