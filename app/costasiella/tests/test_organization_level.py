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


class GQLOrganizationLevel(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationlevel'
        self.permission_add = 'add_organizationlevel'
        self.permission_change = 'change_organizationlevel'
        self.permission_delete = 'delete_organizationlevel'

        self.variables_create = {
            "input": {
                "name": "New level",
            }
        }
        
        self.variables_update = {
            "input": {
                "name": "Updated level",
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.levels_query = '''
query OrganizationLevels($after: String, $before: String, $archived: Boolean) {
  organizationLevels(first: 15, before: $before, after: $after, archived: $archived) {
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

        self.level_query = '''
query getOrganizationLevel($id: ID!) {
    organizationLevel(id:$id) {
      id
      archived
      name
    }
  }
'''

        self.level_create_mutation = '''
mutation CreateOrganizationLevel($input: CreateOrganizationLevelInput!) {
  createOrganizationLevel(input: $input) {
    organizationLevel {
      id
      archived
      name
    }
  }
}
'''

        self.level_update_mutation = '''
  mutation UpdateOrganizationLevel($input: UpdateOrganizationLevelInput!) {
    updateOrganizationLevel(input: $input) {
      organizationLevel {
        id
        archived
        name
      }
    }
  }
'''

        self.level_archive_mutation = '''
mutation ArchiveOrganizationLevel($input: ArchiveOrganizationLevelInput!) {
    archiveOrganizationLevel(input: $input) {
        organizationLevel {
        id
        archived
        }
    }
}
'''

    def tearDown(self):
        # This is run after every test
        pass

    def get_node_id_of_first_level(self):
        # query levels to get node id easily
        variables = {
            'archived': False
        }
        executed = execute_test_client_api_query(self.levels_query, self.admin_user, variables=variables)
        data = executed.get('data')
        
        return data['organizationLevels']['edges'][0]['node']['id']

    def test_query(self):
        """ Query list of levels """
        query = self.levels_query
        level = f.OrganizationLevelFactory.create()
        variables = {
            "archived": False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        item = data['organizationLevels']['edges'][0]['node']
        self.assertEqual(item['name'], level.name)

    def test_query_permission_denied(self):
        """ Query list of levels as user without permissions (Archived shouldn't be listed) """
        query = self.levels_query
        level = f.OrganizationLevelFactory.create()
        level.archived = True
        level.save()

        variables = {
            'archived': True
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(len(data['organizationLevels']['edges']), 0)

    def test_query_permission_granted(self):
        """ Query list of levels with view permission """
        query = self.levels_query
        level = f.OrganizationLevelFactory.create()
        non_public_level = f.OrganizationLevelFactory.build()
        non_public_level.display_public = False
        non_public_level.save()

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
        item = data['organizationLevels']['edges'][0]['node']
        self.assertEqual(item['name'], level.name)

    def test_query_anon_user(self):
        """ Query list of levels as anon user - archived shouldn't be visible"""
        query = self.levels_query
        level = f.OrganizationLevelFactory.create()
        level.archived = True
        level.save()

        variables = {
            'archived': True
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(len(data['organizationLevels']['edges']), 0)

    def test_query_one(self):
        """ Query one level """   
        level = f.OrganizationLevelFactory.create()

        # First query levels to get node id easily
        node_id = self.get_node_id_of_first_level()

        # Now query single level and check
        query = self.level_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLevel']['name'], level.name)
        self.assertEqual(data['organizationLevel']['archived'], level.archived)

    def test_query_one_anon_user(self):
        """ Deny permission to view archived levels for anon users Query one level """
        query = self.level_query
        level = f.OrganizationLevelFactory.create()
        level.archived = True
        level.save()
        node_id = to_global_id("OrganizationLevelNode", level.id)
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLevel'], None)

    def test_query_one_archived_without_permission(self):
        """ None returned when user lacks authorization to view archived levels """
        query = self.level_query
        
        user = f.RegularUserFactory.create()
        level = f.OrganizationLevelFactory.create()
        level.archived = True
        level.save()
        node_id = to_global_id("OrganizationLevelNode", level.id)

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLevel'], None)

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        query = self.level_query
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationlevel')
        user.user_permissions.add(permission)
        user.save()

        level = f.OrganizationLevelFactory.create()
        node_id = self.get_node_id_of_first_level()

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLevel']['name'], level.name)

    def test_create_level(self):
        """ Create a level """
        query = self.level_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationLevel']['organizationLevel']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationLevel']['organizationLevel']['archived'], False)


    def test_create_level_anon_user(self):
        """ Create a level with anonymous user, check error message """
        query = self.level_create_mutation

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_level_permission_granted(self):
        """ Create a level with a user having the add permission """
        query = self.level_create_mutation
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
        self.assertEqual(data['createOrganizationLevel']['organizationLevel']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationLevel']['organizationLevel']['archived'], False)


    def test_create_level_permission_denied(self):
        """ Create a level with a user not having the add permission """
        query = self.level_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_update_level(self):
        """ Update a level as admin user """
        query = self.level_update_mutation
        level = f.OrganizationLevelFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_level()


        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganizationLevel']['organizationLevel']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationLevel']['organizationLevel']['archived'], False)


    def test_update_level_anon_user(self):
        """ Update a level as anonymous user """
        query = self.level_update_mutation
        level = f.OrganizationLevelFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_level()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_level_permission_granted(self):
        """ Update a level as user with permission """
        query = self.level_update_mutation
        level = f.OrganizationLevelFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_level()

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
        self.assertEqual(data['updateOrganizationLevel']['organizationLevel']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationLevel']['organizationLevel']['archived'], False)


    def test_update_level_permission_denied(self):
        """ Update a level as user without permissions """
        query = self.level_update_mutation
        level = f.OrganizationLevelFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_level()

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_archive_level(self):
        """ Archive a level """
        query = self.level_archive_mutation
        level = f.OrganizationLevelFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_level()

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationLevel']['organizationLevel']['archived'], variables['input']['archived'])


    def test_archive_level_anon_user(self):
        """ Archive a level """
        query = self.level_archive_mutation
        level = f.OrganizationLevelFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_level()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_level_permission_granted(self):
        """ Allow archiving levels for users with permissions """
        query = self.level_archive_mutation
        level = f.OrganizationLevelFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_level()

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
        self.assertEqual(data['archiveOrganizationLevel']['organizationLevel']['archived'], variables['input']['archived'])


    def test_archive_level_permission_denied(self):
        """ Check archive level permission denied error message """
        query = self.level_archive_mutation
        level = f.OrganizationLevelFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_level()

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


