# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema

from graphql_relay import to_global_id


class GQLOrganizationAppointment(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_category = 'view_organizationappointmentcategory'
        self.permission_view = 'view_organizationappointment'
        self.permission_add = 'add_organizationappointment'
        self.permission_change = 'change_organizationappointment'
        self.permission_delete = 'delete_organizationappointment'

        self.organization_appointment_category = f.OrganizationAppointmentCategoryFactory.create()
        self.organization_appointment = f.OrganizationAppointmentFactory.create()

        self.variables_create = {
            "input": {
                "organizationAppointmentCategory": to_global_id('OrganizationAppointmentCategoryNode', self.organization_appointment_category.pk),
                "displayPublic": True,
                "name": "First room",
            }
        }

        self.variables_update = {
            "input": {
                "id": to_global_id('OrganizationAppointmentNode', self.organization_appointment.pk),
                "displayPublic": True,
                "name": "Updated room",
            }
        }

        self.variables_archive = {
            "input": {
                "id": to_global_id('OrganizationAppointmentNode', self.organization_appointment.pk),
                "archived": True,
            }
        }

        self.appointments_query = '''
  query OrganizationAppointments($after: String, $before: String, $organizationAppointmentCategory: ID!, $archived: Boolean!) {
    organizationAppointments(first: 15, before: $before, after: $after, organizationAppointmentCategory: $organizationAppointmentCategory, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationAppointmentCategory {
            id
            name
          }
          archived,
          displayPublic
          name
        }
      }
    }
    organizationAppointmentCategory(id: $organizationAppointmentCategory) {
      id
      name
    }
  }
'''

        self.appointment_query = '''
  query OrganizationAppointment($id: ID!) {
    organizationAppointment(id:$id) {
      id
      organizationAppointmentCategory {
        id
        name
      }
      name
      displayPublic
      archived
    }
  }
'''

        self.appointment_create_mutation = ''' 
  mutation CreateOrganizationAppointment($input: CreateOrganizationAppointmentInput!) {
    createOrganizationAppointment(input: $input) {
      organizationAppointment {
        id
        organizationAppointmentCategory {
          id
          name
        }
        archived
        displayPublic
        name
      }
    }
  }
'''

        self.appointment_update_mutation = '''
  mutation UpdateOrganizationAppointment($input: UpdateOrganizationAppointmentInput!) {
    updateOrganizationAppointment(input: $input) {
      organizationAppointment {
        id
        organizationAppointmentCategory {
          id
          name
        }
        name
        displayPublic
      }
    }
  }
'''

        self.appointment_archive_mutation = '''
  mutation ArchiveOrganizationAppointment($input: ArchiveOrganizationAppointmentInput!) {
    archiveOrganizationAppointment(input: $input) {
      organizationAppointment {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of locations """
        query = self.appointments_query
        appointment = f.OrganizationAppointmentFactory.create()

        variables = {
            'organizationAppointmentCategory': to_global_id('OrganizationAppointmentCategoryNode', appointment.organization_appointment_category.pk),
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['organizationAppointments']['edges'][0]['node']['organizationAppointmentCategory']['id'], 
            variables['organizationAppointmentCategory']
        )
        self.assertEqual(data['organizationAppointments']['edges'][0]['node']['name'], appointment.name)
        self.assertEqual(data['organizationAppointments']['edges'][0]['node']['archived'], appointment.archived)
        self.assertEqual(data['organizationAppointments']['edges'][0]['node']['displayPublic'], appointment.display_public)


    def test_query_permission_denied(self):
        """ Query list of appointment_category rooms """
        query = self.appointments_query
        appointment = f.OrganizationAppointmentFactory.create()
        non_public_appointment = f.OrganizationAppointmentFactory.build()
        non_public_appointment.organization_appointment_category = appointment.organization_appointment_category
        non_public_appointment.display_public = False
        non_public_appointment.save()

        variables = {
            'organizationAppointmentCategory': to_global_id('OrganizationAppointmentCategoryNode', appointment.organization_appointment_category.pk),
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        # Category
        permission = Permission.objects.get(codename=self.permission_view_category)
        user.user_permissions.add(permission)
        # Check
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # Public locations only
        non_public_found = False
        for item in data['organizationAppointments']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)


    def test_query_permission_granted(self):
        """ Query list of appointment_category rooms """
        query = self.appointments_query
        appointment = f.OrganizationAppointmentFactory.create()
        non_public_appointment = f.OrganizationAppointmentFactory.build()
        non_public_appointment.organization_appointment_category = appointment.organization_appointment_category
        non_public_appointment.display_public = False
        non_public_appointment.save()

        variables = {
            'organizationAppointmentCategory': to_global_id('OrganizationAppointmentCategoryNode', appointment.organization_appointment_category.pk),
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationappointment')
        user.user_permissions.add(permission)
        # Category
        permission = Permission.objects.get(codename=self.permission_view_category)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all locations, including non public
        non_public_found = False
        for item in data['organizationAppointments']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        # Assert non public locations are listed
        self.assertEqual(non_public_found, True)


    def test_query_anon_user(self):
        """ Query list of appointment_category rooms """
        query = self.appointments_query
        appointment = f.OrganizationAppointmentFactory.create()
        variables = {
            'organizationAppointmentCategory': to_global_id('OrganizationAppointmentCategoryNode', appointment.organization_appointment_category.pk),
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one appointment_category room """   
        appointment = f.OrganizationAppointmentFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationAppointmentNode', appointment.pk)

        # Now query single appointment_category and check
        query = self.appointment_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationAppointment']['organizationAppointmentCategory']['id'], 
          to_global_id('OrganizationAppointmentCategoryNode', appointment.organization_appointment_category.pk))
        self.assertEqual(data['organizationAppointment']['name'], appointment.name)
        self.assertEqual(data['organizationAppointment']['archived'], appointment.archived)
        self.assertEqual(data['organizationAppointment']['displayPublic'], appointment.display_public)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one appointment_category room """   
        appointment = f.OrganizationAppointmentFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationAppointmentNode', appointment.pk)

        # Now query single appointment_category and check
        query = self.appointment_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        appointment = f.OrganizationAppointmentFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationAppointmentNode', appointment.pk)

        # Now query single appointment_category and check
        query = self.appointment_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationappointment')
        user.user_permissions.add(permission)
        # Category
        permission = Permission.objects.get(codename=self.permission_view_category)
        user.user_permissions.add(permission)
        user.save()
        appointment = f.OrganizationAppointmentFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationAppointmentNode', appointment.pk)

        # Now query single appointment_category and check   
        query = self.appointment_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationAppointment']['name'], appointment.name)


    def test_create_appointment(self):
        """ Create a appointment_category room """
        query = self.appointment_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
          data['createOrganizationAppointment']['organizationAppointment']['organizationAppointmentCategory']['id'], 
          variables['input']['organizationAppointmentCategory'])
        self.assertEqual(data['createOrganizationAppointment']['organizationAppointment']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationAppointment']['organizationAppointment']['archived'], False)
        self.assertEqual(data['createOrganizationAppointment']['organizationAppointment']['displayPublic'], variables['input']['displayPublic'])


    def test_create_appointment_anon_user(self):
        """ Don't allow creating locations rooms for non-logged in users """
        query = self.appointment_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_appointment_permission_granted(self):
        """ Allow creating appointment_category rooms for users with permissions """
        query = self.appointment_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        # Category
        permission = Permission.objects.get(codename=self.permission_view_category)
        user.user_permissions.add(permission)
        user.save()

        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
          data['createOrganizationAppointment']['organizationAppointment']['organizationAppointmentCategory']['id'], 
          variables['input']['organizationAppointmentCategory'])
        self.assertEqual(data['createOrganizationAppointment']['organizationAppointment']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationAppointment']['organizationAppointment']['archived'], False)
        self.assertEqual(data['createOrganizationAppointment']['organizationAppointment']['displayPublic'], variables['input']['displayPublic'])


    def test_create_appointment_permission_denied(self):
        """ Check create appointment_category room permission denied error message """
        query = self.appointment_create_mutation
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


    def test_update_appointment(self):
        """ Update a appointment_category room """
        query = self.appointment_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateOrganizationAppointment']['organizationAppointment']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationAppointment']['organizationAppointment']['displayPublic'], variables['input']['displayPublic'])


    def test_update_appointment_anon_user(self):
        """ Don't allow updating appointment_category rooms for non-logged in users """
        query = self.appointment_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_appointment_permission_granted(self):
        """ Allow updating appointment_category rooms for users with permissions """
        query = self.appointment_update_mutation
        variables = self.variables_update

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        # Appointment category
        permission = Permission.objects.get(codename=self.permission_view_category)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganizationAppointment']['organizationAppointment']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationAppointment']['organizationAppointment']['displayPublic'], variables['input']['displayPublic'])


    def test_update_appointment_permission_denied(self):
        """ Check update appointment_category room permission denied error message """
        query = self.appointment_update_mutation
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


    def test_archive_appointment(self):
        """ Archive a appointment_category room"""
        query = self.appointment_archive_mutation
        variables = self.variables_archive

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationAppointment']['organizationAppointment']['archived'], variables['input']['archived'])


    def test_archive_appointment_anon_user(self):
        """ Archive a appointment_category room """
        query = self.appointment_archive_mutation
        variables = self.variables_archive

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_appointment_permission_granted(self):
        """ Allow archiving locations for users with permissions """
        query = self.appointment_archive_mutation
        variables = self.variables_archive

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
        self.assertEqual(data['archiveOrganizationAppointment']['organizationAppointment']['archived'], variables['input']['archived'])


    def test_archive_appointment_permission_denied(self):
        """ Check archive appointment_category room permission denied error message """
        query = self.appointment_archive_mutation
        variables = self.variables_archive
        
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

