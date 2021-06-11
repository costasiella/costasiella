# from graphql.error.located_error import GraphQLLocatedError
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
from ..modules.gql_tools import get_rid
from .. import models
from .. import schema


class GQLOrganizationLocation(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationlocation'
        self.permission_add = 'add_organizationlocation'
        self.permission_change = 'change_organizationlocation'
        self.permission_delete = 'delete_organizationlocation'

        self.locations_query = '''
  query OrganizationLocations($after: String, $before: String, $archived: Boolean) {
    organizationLocations(first: 15, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id,
          archived,
          displayPublic,
          name
        }
      }
    }
  }
'''

        self.location_query = '''
query getOrganizationLocation($id: ID!) {
    organizationLocation(id:$id) {
      id
      name
      displayPublic
      archived
    }
  }
'''

        self.location_create_mutation = ''' 
  mutation CreateOrganizationLocation($input: CreateOrganizationLocationInput!) {
    createOrganizationLocation(input: $input) {
      organizationLocation {
        id
        archived
        displayPublic
        name
      }
    }
  }
'''

        self.location_update_mutation = '''
  mutation UpdateOrganizationLocation($input: UpdateOrganizationLocationInput!) {
    updateOrganizationLocation(input: $input) {
      organizationLocation {
        id
        name
        displayPublic
      }
    }
  }
'''

        self.location_archive_mutation = '''
  mutation ArchiveOrganizationLocation($input: ArchiveOrganizationLocationInput!) {
    archiveOrganizationLocation(input: $input) {
      organizationLocation {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def get_node_id_of_first_location(self):
        # query locations to get node id easily
        variables = {
            'archived': False
        }
        executed = execute_test_client_api_query(self.locations_query, self.admin_user, variables=variables)
        data = executed.get('data')
        
        return data['organizationLocations']['edges'][0]['node']['id']

    def test_query(self):
        """ Query list of locations """
        query = self.locations_query
        location = f.OrganizationLocationFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['organizationLocations']['edges'][0]['node']['name'], location.name)
        self.assertEqual(data['organizationLocations']['edges'][0]['node']['archived'], location.archived)
        self.assertEqual(data['organizationLocations']['edges'][0]['node']['displayPublic'], location.display_public)

    def test_query_permission_denied(self):
        """ Query list of locations """
        query = self.locations_query
        location = f.OrganizationLocationFactory.create()
        non_public_location = f.OrganizationLocationFactory.build()
        non_public_location.display_public = False
        non_public_location.save()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # Public locations only
        non_public_found = False
        for item in data['organizationLocations']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)

    def test_query_permission_granted(self):
        """ Query list of locations """
        query = self.locations_query
        location = f.OrganizationLocationFactory.create()
        non_public_location = f.OrganizationLocationFactory.build()
        non_public_location.display_public = False
        non_public_location.save()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationlocation')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all locations, including non public
        non_public_found = False
        for item in data['organizationLocations']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        # Assert non public locations are listed
        self.assertEqual(non_public_found, True)

    def test_query_anon_user_show_public_non_archived_locations(self):
        """ Query list of locations """
        query = self.locations_query
        location = f.OrganizationLocationFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['organizationLocations']['edges'][0]['node']['name'], location.name)

    def test_query_anon_user_dont_show_non_public_archived_locations(self):
        """ Query list of locations """
        query = self.locations_query
        location = f.OrganizationLocationFactory.create()
        location.archived = True
        location.save()

        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(len(data['organizationLocations']['edges']), 0)

    def test_query_one(self):
        """ Query one location """   
        location = f.OrganizationLocationFactory.create()

        # First query locations to get node id easily
        node_id = self.get_node_id_of_first_location()

        # Now query single location and check
        query = self.location_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLocation']['name'], location.name)
        self.assertEqual(data['organizationLocation']['archived'], location.archived)
        self.assertEqual(data['organizationLocation']['displayPublic'], location.display_public)

    def test_query_one_anon_user_show_public_non_archived_location(self):
        """ Check permission for anon users Query one location """
        location = f.OrganizationLocationFactory.create()

        # First query locations to get node id easily
        node_id = self.get_node_id_of_first_location()

        # Now query single location and check
        query = self.location_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLocation']['name'], location.name)

    def test_query_one_anon_user_dont_show_non_public_archived_location(self):
        """ Check permission for anon users Query one location """
        location = f.OrganizationLocationFactory.create()
        location.archived = True
        location.save()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationNode', location.id)

        # Now query single location and check
        query = self.location_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLocation'], None)

    def test_query_one_user_no_permissions_only_public_non_archived(self):
        """ Only list public, non archived locations when user lacks authorization """
        # Create regular user
        user = f.RegularUserFactory.create()
        location = f.OrganizationLocationFactory.create()

        # First query locations to get node id easily
        node_id = self.get_node_id_of_first_location()

        # Now query single location and check
        query = self.location_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLocation']['name'], location.name)

    def test_query_one_user_no_permissions_hide_nonpublic_archived(self):
        """ Only list public, non archived locations when user lacks authorization """
        # Create regular user
        user = f.RegularUserFactory.create()
        location = f.OrganizationLocationFactory.create()
        location.archived = True
        location.save()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationNode', location.id)

        # Now query single location and check
        query = self.location_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLocation'], None)

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationlocation')
        user.user_permissions.add(permission)
        user.save()
        location = f.OrganizationLocationFactory.create()

        # First query locations to get node id easily
        node_id = self.get_node_id_of_first_location()

        # Now query single location and check   
        query = self.location_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLocation']['name'], location.name)


    def test_create_location(self):
        """ Create a location """
        query = self.location_create_mutation

        variables = {
            "input": {
                "name": "New location",
                "displayPublic": True
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationLocation']['organizationLocation']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationLocation']['organizationLocation']['archived'], False)
        self.assertEqual(data['createOrganizationLocation']['organizationLocation']['displayPublic'], variables['input']['displayPublic'])

        # Check creation of a default room
        rid = get_rid(data['createOrganizationLocation']['organizationLocation']['id'])
        location = models.OrganizationLocation.objects.get(pk=rid.id)
        rooms = models.OrganizationLocationRoom.objects.filter(organization_location = location)
        room = rooms[0]
        self.assertEqual(room.name, 'Room 1')


    def test_create_location_anon_user(self):
        """ Don't allow creating locations for non-logged in users """
        query = self.location_create_mutation

        variables = {
            "input": {
                "name": "New location",
                "displayPublic": True
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_location_permission_granted(self):
        """ Allow creating locations for users with permissions """
        query = self.location_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        variables = {
            "input": {
                "name": "New location",
                "displayPublic": True
            }
        }

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationLocation']['organizationLocation']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationLocation']['organizationLocation']['archived'], False)
        self.assertEqual(data['createOrganizationLocation']['organizationLocation']['displayPublic'], variables['input']['displayPublic'])


    def test_create_location_permission_denied(self):
        """ Check create location permission denied error message """
        query = self.location_create_mutation
        
        variables = {
            "input": {
                "name": "New location",
                "displayPublic": True
            }
        }

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


    def test_update_location(self):
        """ Update a location """
        query = self.location_update_mutation
        location = f.OrganizationLocationFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_location(),
                "name": "Updated name",
                "displayPublic": False
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganizationLocation']['organizationLocation']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationLocation']['organizationLocation']['displayPublic'], variables['input']['displayPublic'])


    def test_update_location_anon_user(self):
        """ Don't allow updating locations for non-logged in users """
        query = self.location_update_mutation
        location = f.OrganizationLocationFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_location(),
                "name": "Updated name",
                "displayPublic": False
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_location_permission_granted(self):
        """ Allow updating locations for users with permissions """
        query = self.location_update_mutation

        location = f.OrganizationLocationFactory.create()
        variables = {
            "input": {
                "id": self.get_node_id_of_first_location(),
                "name": "Updated name",
                "displayPublic": False
            }
        }

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
        self.assertEqual(data['updateOrganizationLocation']['organizationLocation']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationLocation']['organizationLocation']['displayPublic'], variables['input']['displayPublic'])


    def test_update_location_permission_denied(self):
        """ Check update location permission denied error message """
        query = self.location_update_mutation
        location = f.OrganizationLocationFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_location(),
                "name": "Updated name",
                "displayPublic": False
            }
        }

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


    def test_archive_location(self):
        """ Archive a location """
        query = self.location_archive_mutation
        location = f.OrganizationLocationFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_location(),
                "archived": True
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationLocation']['organizationLocation']['archived'], variables['input']['archived'])


    def test_archive_location_anon_user(self):
        """ Archive a location """
        query = self.location_archive_mutation
        location = f.OrganizationLocationFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_location(),
                "archived": True
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_location_permission_granted(self):
        """ Allow archiving locations for users with permissions """
        query = self.location_archive_mutation

        location = f.OrganizationLocationFactory.create()
        variables = {
            "input": {
                "id": self.get_node_id_of_first_location(),
                "archived": True
            }
        }
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
        self.assertEqual(data['archiveOrganizationLocation']['organizationLocation']['archived'], variables['input']['archived'])


    def test_archive_location_permission_denied(self):
        """ Check archive location permission denied error message """
        query = self.location_archive_mutation

        location = f.OrganizationLocationFactory.create()
        variables = {
            "input": {
                "id": self.get_node_id_of_first_location(),
                "archived": True
            }
        }
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

