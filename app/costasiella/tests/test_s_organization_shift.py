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
from .helpers import execute_test_client_api_query
from .. import models


class GQLOrganizationShift(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationshift'
        self.permission_add = 'add_organizationshift'
        self.permission_change = 'change_organizationshift'
        self.permission_delete = 'delete_organizationshift'

        self.variables_create = {
            "input": {
                "name": "New shift",
            }
        }
        
        self.variables_update = {
            "input": {
                "name": "Updated shift",
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.shifts_query = '''
query OrganizationShifts($after: String, $before: String, $archived: Boolean) {
  organizationShifts(first: 15, before: $before, after: $after, archived: $archived) {
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
    }
    edges {
      node {
        id
        archived
        name
      }
    }
  }
}
'''

        self.shift_query = '''
query getOrganizationShift($id: ID!) {
    organizationShift(id:$id) {
      id
      archived
      name
    }
  }
'''

        self.shift_create_mutation = '''
mutation CreateOrganizationShift($input: CreateOrganizationShiftInput!) {
  createOrganizationShift(input: $input) {
    organizationShift {
      id
      archived
      name
    }
  }
}
'''

        self.shift_update_mutation = '''
  mutation UpdateOrganizationShift($input: UpdateOrganizationShiftInput!) {
    updateOrganizationShift(input: $input) {
      organizationShift {
        id
        archived
        name
      }
    }
  }
'''

        self.shift_archive_mutation = '''
mutation ArchiveOrganizationShift($input: ArchiveOrganizationShiftInput!) {
    archiveOrganizationShift(input: $input) {
        organizationShift {
        id
        archived
        }
    }
}
'''

    def tearDown(self):
        # This is run after every test
        pass

    def get_node_id_of_first_shift(self):
        # query shifts to get node id easily
        variables = {
            'archived': False
        }
        executed = execute_test_client_api_query(self.shifts_query, self.admin_user, variables=variables)
        data = executed.get('data')
        
        return data['organizationShifts']['edges'][0]['node']['id']

    def test_query(self):
        """ Query list of shifts """
        query = self.shifts_query
        shift = f.OrganizationShiftFactory.create()
        variables = {
            "archived": False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        item = data['organizationShifts']['edges'][0]['node']
        self.assertEqual(item['name'], shift.name)

    def test_query_permission_denied(self):
        """ Query list of shifts as user without permissions (Archived shouldn't be listed) """
        query = self.shifts_query
        shift = f.OrganizationShiftFactory.create()
        shift.archived = True
        shift.save()

        variables = {
            'archived': True
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of shifts with view permission """
        query = self.shifts_query
        shift = f.OrganizationShiftFactory.create()
        non_public_shift = f.OrganizationShiftFactory.build()
        non_public_shift.display_public = False
        non_public_shift.save()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')
        item = data['organizationShifts']['edges'][0]['node']
        self.assertEqual(item['name'], shift.name)

    def test_query_anon_user(self):
        """ Query list of shifts as anon user - archived shouldn't be visible"""
        query = self.shifts_query
        shift = f.OrganizationShiftFactory.create()
        shift.archived = True
        shift.save()

        variables = {
            'archived': True
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one shift """   
        shift = f.OrganizationShiftFactory.create()

        # First query shifts to get node id easily
        node_id = self.get_node_id_of_first_shift()

        # Now query single shift and check
        query = self.shift_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationShift']['name'], shift.name)
        self.assertEqual(data['organizationShift']['archived'], shift.archived)

    def test_query_one_anon_user(self):
        """ Deny permission to view archived shifts for anon users Query one shift """
        query = self.shift_query
        shift = f.OrganizationShiftFactory.create()
        shift.archived = True
        shift.save()
        node_id = to_global_id("OrganizationShiftNode", shift.id)
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ None returned when user lacks authorization to view shifts """
        query = self.shift_query
        
        user = f.RegularUserFactory.create()
        shift = f.OrganizationShiftFactory.create()
        node_id = to_global_id("OrganizationShiftNode", shift.id)

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        query = self.shift_query
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationshift')
        user.user_permissions.add(permission)
        user.save()

        shift = f.OrganizationShiftFactory.create()
        node_id = self.get_node_id_of_first_shift()

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationShift']['name'], shift.name)

    def test_create_shift(self):
        """ Create a shift """
        query = self.shift_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationShift']['organizationShift']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationShift']['organizationShift']['archived'], False)

    def test_create_shift_anon_user(self):
        """ Create a shift with anonymous user, check error message """
        query = self.shift_create_mutation

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_shift_permission_granted(self):
        """ Create a shift with a user having the add permission """
        query = self.shift_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationShift']['organizationShift']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationShift']['organizationShift']['archived'], False)

    def test_create_shift_permission_denied(self):
        """ Create a shift with a user not having the add permission """
        query = self.shift_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_shift(self):
        """ Update a shift as admin user """
        query = self.shift_update_mutation
        shift = f.OrganizationShiftFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_shift()


        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganizationShift']['organizationShift']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationShift']['organizationShift']['archived'], False)

    def test_update_shift_anon_user(self):
        """ Update a shift as anonymous user """
        query = self.shift_update_mutation
        shift = f.OrganizationShiftFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_shift()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_shift_permission_granted(self):
        """ Update a shift as user with permission """
        query = self.shift_update_mutation
        shift = f.OrganizationShiftFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_shift()

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
        self.assertEqual(data['updateOrganizationShift']['organizationShift']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationShift']['organizationShift']['archived'], False)

    def test_update_shift_permission_denied(self):
        """ Update a shift as user without permissions """
        query = self.shift_update_mutation
        shift = f.OrganizationShiftFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_shift()

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_archive_shift(self):
        """ Archive a shift """
        query = self.shift_archive_mutation
        shift = f.OrganizationShiftFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_shift()

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationShift']['organizationShift']['archived'], variables['input']['archived'])

    def test_archive_shift_anon_user(self):
        """ Archive a shift """
        query = self.shift_archive_mutation
        shift = f.OrganizationShiftFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_shift()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_archive_shift_permission_granted(self):
        """ Allow archiving shifts for users with permissions """
        query = self.shift_archive_mutation
        shift = f.OrganizationShiftFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_shift()

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
        self.assertEqual(data['archiveOrganizationShift']['organizationShift']['archived'], variables['input']['archived'])

    def test_archive_shift_permission_denied(self):
        """ Check archive shift permission denied error message """
        query = self.shift_archive_mutation
        shift = f.OrganizationShiftFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_shift()

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
