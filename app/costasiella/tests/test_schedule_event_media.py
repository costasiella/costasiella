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
          "id": to_global_id("OrganizationDocumentNode", self.schedule_event_media.id)
        }

        with open(os.path.join(os.getcwd(), "costasiella", "tests", "files", "test_pdf.txt"), 'r') as input_file:
          self.variables_create = {
              "input": {
                  "documentFileName": "test.pdf",
                  "documentType": "TERMS_AND_CONDITIONS",
                  "version": "1.1",
                  "dateStart": "2019-12-01",
                  "document": input_file.read().replace("\n", "")
              }
          }

        self.variables_update = {
            "input": {
                "id": to_global_id("OrganizationDocumentNode", self.schedule_event_media.id),
                "version": "1.2",
                "dateStart": "2019-11-01",
                "dateEnd": "2019-12-31",
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
      image
    }
  }
'''

        self.schedule_event_media_create_mutation = ''' 
  mutation CreateScheduleEventMedia($input:CreateScheduleEventMediaInput!) {
    createScheduleEventMedia(input: $input) {
      scheduleEventMedia {
        id
      }
    }
  }
'''

        self.schedule_event_media_update_mutation = '''
  mutation UpdateScheduleEventMedia($input:UpdateScheduleEventMediaInput!) {
    updateScheduleEventMedia(input: $input) {
      scheduleEventMedia {
        id
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
        """ Query list of organization documents """
        query = self.schedule_event_medias_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['organizationDocuments']['edges'][0]['node']['id'], 
            to_global_id('OrganizationDocumentNode', self.schedule_event_media.id)
        )
        self.assertEqual(data['organizationDocuments']['edges'][0]['node']['documentType'], self.schedule_event_media.document_type)
        self.assertEqual(data['organizationDocuments']['edges'][0]['node']['version'], str(self.schedule_event_media.version))
        self.assertEqual(data['organizationDocuments']['edges'][0]['node']['dateStart'], str(self.schedule_event_media.date_start))
        self.assertEqual(data['organizationDocuments']['edges'][0]['node']['document'], self.schedule_event_media.document)

    ##
    # No permission tests are required in this test, as there are no permission checks in the schema.
    # The listing of these documents is public, so users also don't need to be logged in.
    ##

    def test_query_one(self):
        """ Query one organization document """   
        query = self.schedule_event_media_query
      
        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['organizationDocument']['id'], self.variables_query_one['id'])


    def test_create_schedule_event_media(self):
        """ Create an organization document """
        query = self.schedule_event_media_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['createOrganizationDocument']['organizationDocument']['documentType'], variables['input']['documentType'])
        self.assertEqual(data['createOrganizationDocument']['organizationDocument']['version'], variables['input']['version'])
        self.assertEqual(data['createOrganizationDocument']['organizationDocument']['dateStart'], variables['input']['dateStart'])
        # self.assertEqual(data['createOrganizationDocument']['organizationDocument']['document'], variables['input']['document'])


    def test_create_schedule_event_media_anon_user(self):
        """ Don't allow creating organization documents for non-logged in users """
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
        """ Allow creating organization documents for users with permissions """
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
        self.assertEqual(data['createOrganizationDocument']['organizationDocument']['documentType'], variables['input']['documentType'])


    def test_create_schedule_event_media_permission_denied(self):
        """ Check create organization document permission denied error message """
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
        """ Update a organization document """
        query = self.schedule_event_media_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateOrganizationDocument']['organizationDocument']['id'], variables['input']['id'])
        self.assertEqual(data['updateOrganizationDocument']['organizationDocument']['version'], variables['input']['version'])
        self.assertEqual(data['updateOrganizationDocument']['organizationDocument']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['updateOrganizationDocument']['organizationDocument']['dateEnd'], variables['input']['dateEnd'])


    def test_update_schedule_event_media_anon_user(self):
        """ Don't allow updating organization documents for non-logged in users """
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
        """ Allow updating organization documents for users with permissions """
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
        self.assertEqual(data['updateOrganizationDocument']['organizationDocument']['version'], variables['input']['version'])


    def test_update_schedule_event_media_permission_denied(self):
        """ Check update organization document permission denied error message """
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
        """ Delete a organization document """
        query = self.schedule_event_media_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        
        self.assertEqual(data['deleteOrganizationDocument']['ok'], True)

        exists = models.OrganizationDocument.objects.exists()
        self.assertEqual(exists, False)


    def test_delete_schedule_event_media_anon_user(self):
        """ Delete a organization documentm """
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
        """ Allow deleting organization documents for users with permissions """
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
        self.assertEqual(data['deleteOrganizationDocument']['ok'], True)


    def test_delete_schedule_event_media_permission_denied(self):
        """ Check delete organization document permission denied error message """
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

