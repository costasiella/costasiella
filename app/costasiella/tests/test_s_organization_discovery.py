# from graphql.error.located_error import GraphQLLocatedError
import graphql

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models


class GQLOrganizationDiscovery(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationdiscovery'
        self.permission_add = 'add_organizationdiscovery'
        self.permission_change = 'change_organizationdiscovery'
        self.permission_delete = 'delete_organizationdiscovery'

        self.variables_create = {
            "input": {
                "name": "New discovery",
            }
        }
        
        self.variables_update = {
            "input": {
                "name": "Updated discovery",
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }


        self.discoveries_query = '''
query OrganizationDiscoveries($after: String, $before: String, $archived: Boolean) {
  organizationDiscoveries(first: 15, before: $before, after: $after, archived: $archived) {
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

        self.discovery_query = '''
query getOrganizationDiscovery($id: ID!) {
    organizationDiscovery(id:$id) {
      id
      archived
      name
    }
  }
'''

        self.discovery_create_mutation = '''
mutation CreateOrganizationDiscovery($input: CreateOrganizationDiscoveryInput!) {
  createOrganizationDiscovery(input: $input) {
    organizationDiscovery {
      id
      archived
      name
    }
  }
}
'''

        self.discovery_update_mutation = '''
  mutation UpdateOrganizationDiscovery($input: UpdateOrganizationDiscoveryInput!) {
    updateOrganizationDiscovery(input: $input) {
      organizationDiscovery {
        id
        archived
        name
      }
    }
  }
'''

        self.discovery_archive_mutation = '''
mutation ArchiveOrganizationDiscovery($input: ArchiveOrganizationDiscoveryInput!) {
    archiveOrganizationDiscovery(input: $input) {
        organizationDiscovery {
        id
        archived
        }
    }
}
'''

    def tearDown(self):
        # This is run after every test
        pass

    def get_node_id_of_first_discovery(self):
        # query discoveries to get node id easily
        variables = {
            'archived': False
        }
        executed = execute_test_client_api_query(self.discoveries_query, self.admin_user, variables=variables)
        data = executed.get('data')
        
        return data['organizationDiscoveries']['edges'][0]['node']['id']

    def test_query(self):
        """ Query list of discoveries """
        query = self.discoveries_query
        discovery = f.OrganizationDiscoveryFactory.create()
        variables = {
            "archived": False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        item = data['organizationDiscoveries']['edges'][0]['node']
        self.assertEqual(item['name'], discovery.name)

    def test_query_permission_denied(self):
        """ Query list of discoveries as user without permissions """
        query = self.discoveries_query
        discovery = f.OrganizationDiscoveryFactory.create()
        non_public_discovery = f.OrganizationDiscoveryFactory.build()
        non_public_discovery.display_public = False
        non_public_discovery.save()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of discoveries with view permission """
        query = self.discoveries_query
        discovery = f.OrganizationDiscoveryFactory.create()
        non_public_discovery = f.OrganizationDiscoveryFactory.build()
        non_public_discovery.display_public = False
        non_public_discovery.save()

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
        item = data['organizationDiscoveries']['edges'][0]['node']
        self.assertEqual(item['name'], discovery.name)

    def test_query_anon_user(self):
        """ Query list of discoveries as anon user """
        query = self.discoveries_query
        discovery = f.OrganizationDiscoveryFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one discovery """   
        discovery = f.OrganizationDiscoveryFactory.create()

        # First query discoveries to get node id easily
        node_id = self.get_node_id_of_first_discovery()

        # Now query single discovery and check
        query = self.discovery_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')

        self.assertEqual(data['organizationDiscovery']['name'], discovery.name)
        self.assertEqual(data['organizationDiscovery']['archived'], discovery.archived)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one discovery """   
        query = self.discovery_query
        discovery = f.OrganizationDiscoveryFactory.create()
        node_id = self.get_node_id_of_first_discovery()
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        query = self.discovery_query
        
        user = f.RegularUserFactory.create()
        discovery = f.OrganizationDiscoveryFactory.create()
        node_id = self.get_node_id_of_first_discovery()

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        query = self.discovery_query
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationdiscovery')
        user.user_permissions.add(permission)
        user.save()

        discovery = f.OrganizationDiscoveryFactory.create()
        node_id = self.get_node_id_of_first_discovery()

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationDiscovery']['name'], discovery.name)

    def test_create_discovery(self):
        """ Create a discovery """
        query = self.discovery_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationDiscovery']['organizationDiscovery']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationDiscovery']['organizationDiscovery']['archived'], False)


    def test_create_discovery_anon_user(self):
        """ Create a discovery with anonymous user, check error message """
        query = self.discovery_create_mutation

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_discovery_permission_granted(self):
        """ Create a discovery with a user having the add permission """
        query = self.discovery_create_mutation
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
        self.assertEqual(data['createOrganizationDiscovery']['organizationDiscovery']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationDiscovery']['organizationDiscovery']['archived'], False)


    def test_create_discovery_permission_denied(self):
        """ Create a discovery with a user not having the add permission """
        query = self.discovery_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_update_discovery(self):
        """ Update a discovery as admin user """
        query = self.discovery_update_mutation
        discovery = f.OrganizationDiscoveryFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_discovery()


        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganizationDiscovery']['organizationDiscovery']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationDiscovery']['organizationDiscovery']['archived'], False)


    def test_update_discovery_anon_user(self):
        """ Update a discovery as anonymous user """
        query = self.discovery_update_mutation
        discovery = f.OrganizationDiscoveryFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_discovery()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_discovery_permission_granted(self):
        """ Update a discovery as user with permission """
        query = self.discovery_update_mutation
        discovery = f.OrganizationDiscoveryFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_discovery()

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
        self.assertEqual(data['updateOrganizationDiscovery']['organizationDiscovery']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationDiscovery']['organizationDiscovery']['archived'], False)


    def test_update_discovery_permission_denied(self):
        """ Update a discovery as user without permissions """
        query = self.discovery_update_mutation
        discovery = f.OrganizationDiscoveryFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_discovery()

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_archive_discovery(self):
        """ Archive a discovery """
        query = self.discovery_archive_mutation
        discovery = f.OrganizationDiscoveryFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_discovery()

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationDiscovery']['organizationDiscovery']['archived'], variables['input']['archived'])


    def test_archive_discovery_anon_user(self):
        """ Archive a discovery """
        query = self.discovery_archive_mutation
        discovery = f.OrganizationDiscoveryFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_discovery()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_discovery_permission_granted(self):
        """ Allow archiving discoveries for users with permissions """
        query = self.discovery_archive_mutation
        discovery = f.OrganizationDiscoveryFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_discovery()

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
        self.assertEqual(data['archiveOrganizationDiscovery']['organizationDiscovery']['archived'], variables['input']['archived'])


    def test_archive_discovery_permission_denied(self):
        """ Check archive discovery permission denied error message """
        query = self.discovery_archive_mutation
        discovery = f.OrganizationDiscoveryFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_discovery()

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


