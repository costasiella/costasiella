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


class GQLOrganizationLocationRoom(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationlocationroom'
        self.permission_add = 'add_organizationlocationroom'
        self.permission_change = 'change_organizationlocationroom'
        self.permission_delete = 'delete_organizationlocationroom'

        self.organization_location = f.OrganizationLocationFactory.create()
        self.organization_location_room = f.OrganizationLocationRoomFactory.create()

        self.variables_create = {
            "input": {
                "organizationLocation": to_global_id('OrganizationLocationNode', self.organization_location.pk),
                "displayPublic": True,
                "name": "First room",
            }
        }

        self.variables_update = {
            "input": {
                "id": to_global_id('OrganizationLocationRoomNode', self.organization_location_room.pk),
                "displayPublic": True,
                "name": "Updated room",
            }
        }

        self.variables_archive = {
            "input": {
                "id": to_global_id('OrganizationLocationRoomNode', self.organization_location_room.pk),
                "archived": True,
            }
        }

        self.location_rooms_query = '''
  query OrganizationLocationRooms($after: String, $before: String, $organizationLocation: ID!, $archived: Boolean!) {
    organizationLocationRooms(first: 15, before: $before, after: $after, organizationLocation: $organizationLocation, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationLocation {
            id
            name
          }
          archived,
          displayPublic
          name
        }
      }
    }
    organizationLocation(id: $organizationLocation) {
      id
      name
    }
  }
'''

        self.location_room_query = '''
  query OrganizationLocationRoom($id: ID!) {
    organizationLocationRoom(id:$id) {
      id
      organizationLocation {
        id
        name
      }
      name
      displayPublic
      archived
    }
  }
'''

        self.location_room_create_mutation = ''' 
  mutation CreateOrganizationLocationRoom($input: CreateOrganizationLocationRoomInput!) {
    createOrganizationLocationRoom(input: $input) {
      organizationLocationRoom {
        id
        organizationLocation {
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

        self.location_room_update_mutation = '''
  mutation UpdateOrganizationLocationRoom($input: UpdateOrganizationLocationRoomInput!) {
    updateOrganizationLocationRoom(input: $input) {
      organizationLocationRoom {
        id
        organizationLocation {
          id
          name
        }
        name
        displayPublic
      }
    }
  }
'''

        self.location_room_archive_mutation = '''
  mutation ArchiveOrganizationLocationRoom($input: ArchiveOrganizationLocationRoomInput!) {
    archiveOrganizationLocationRoom(input: $input) {
      organizationLocationRoom {
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
        query = self.location_rooms_query
        location_room = f.OrganizationLocationRoomFactory.create()

        variables = {
            'organizationLocation': to_global_id('OrganizationLocationNode', location_room.organization_location.pk),
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['organizationLocationRooms']['edges'][0]['node']['organizationLocation']['id'], 
            variables['organizationLocation']
        )
        self.assertEqual(data['organizationLocationRooms']['edges'][0]['node']['name'], location_room.name)
        self.assertEqual(data['organizationLocationRooms']['edges'][0]['node']['archived'], location_room.archived)
        self.assertEqual(data['organizationLocationRooms']['edges'][0]['node']['displayPublic'], location_room.display_public)


    def test_query_permission_denied(self):
        """ Query list of location rooms """
        query = self.location_rooms_query
        location_room = f.OrganizationLocationRoomFactory.create()
        non_public_location_room = f.OrganizationLocationRoomFactory.build()
        non_public_location_room.organization_location = location_room.organization_location
        non_public_location_room.display_public = False
        non_public_location_room.save()

        variables = {
            'organizationLocation': to_global_id('OrganizationLocationNode', location_room.organization_location.pk),
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # Public locations only
        non_public_found = False
        for item in data['organizationLocationRooms']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)

    def test_query_permission_granted(self):
        """ Query list of location rooms """
        query = self.location_rooms_query
        location_room = f.OrganizationLocationRoomFactory.create()
        non_public_location_room = f.OrganizationLocationRoomFactory.build()
        non_public_location_room.organization_location = location_room.organization_location
        non_public_location_room.display_public = False
        non_public_location_room.save()

        variables = {
            'organizationLocation': to_global_id('OrganizationLocationNode', location_room.organization_location.pk),
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationlocationroom')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all locations, including non public
        non_public_found = False
        for item in data['organizationLocationRooms']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        # Assert non public locations are listed
        self.assertEqual(non_public_found, True)


    def test_query_anon_user(self):
        """ Query list of location rooms """
        query = self.location_rooms_query
        location_room = f.OrganizationLocationRoomFactory.create()
        variables = {
            'organizationLocation': to_global_id('OrganizationLocationNode', location_room.organization_location.pk),
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one location room """   
        location_room = f.OrganizationLocationRoomFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationRoomNode', location_room.pk)

        # Now query single location and check
        query = self.location_room_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLocationRoom']['organizationLocation']['id'], 
          to_global_id('OrganizationLocationNode', location_room.organization_location.pk))
        self.assertEqual(data['organizationLocationRoom']['name'], location_room.name)
        self.assertEqual(data['organizationLocationRoom']['archived'], location_room.archived)
        self.assertEqual(data['organizationLocationRoom']['displayPublic'], location_room.display_public)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one location room """   
        location_room = f.OrganizationLocationRoomFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationRoomNode', location_room.pk)

        # Now query single location and check
        query = self.location_room_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLocationRoom']['name'], location_room.name)

    def test_query_one_anon_user_archived_or_non_public(self):
        """ Deny permission for anon users Query one location room """
        location_room = f.OrganizationLocationRoomFactory.create()
        location_room.archived = True
        location_room.display_public = False
        location_room.save()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationRoomNode', location_room.pk)

        # Now query single location and check
        query = self.location_room_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied_archived(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        location_room = f.OrganizationLocationRoomFactory.create()
        location_room.archived = True
        location_room.save()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationRoomNode', location_room.pk)

        # Now query single location and check
        query = self.location_room_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_denied_non_public(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        user = f.RegularUserFactory.create()
        location_room = f.OrganizationLocationRoomFactory.create()
        location_room.display_public = False
        location_room.save()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationRoomNode', location_room.pk)

        # Now query single location and check
        query = self.location_room_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_no_permission(self):
        """ Ok when user lacks authorization for archived & public """
        # Create regular user
        user = f.RegularUserFactory.create()
        location_room = f.OrganizationLocationRoomFactory.create()


        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationRoomNode', location_room.pk)

        # Now query single location and check
        query = self.location_room_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLocationRoom']['name'], location_room.name)


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission to view archived & non public rooms """
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationlocationroom')
        user.user_permissions.add(permission)
        user.save()
        location_room = f.OrganizationLocationRoomFactory.create()
        location_room.archived = True
        location_room.display_public = False
        location_room.save()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationRoomNode', location_room.pk)

        # Now query single location and check   
        query = self.location_room_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLocationRoom']['name'], location_room.name)


    def test_create_location_room(self):
        """ Create a location room """
        query = self.location_room_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
          data['createOrganizationLocationRoom']['organizationLocationRoom']['organizationLocation']['id'], 
          variables['input']['organizationLocation'])
        self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['archived'], False)
        self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['displayPublic'], variables['input']['displayPublic'])


    def test_create_location_room_anon_user(self):
        """ Don't allow creating locations rooms for non-logged in users """
        query = self.location_room_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_location_room_permission_granted(self):
        """ Allow creating location rooms for users with permissions """
        query = self.location_room_create_mutation

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
        self.assertEqual(
          data['createOrganizationLocationRoom']['organizationLocationRoom']['organizationLocation']['id'], 
          variables['input']['organizationLocation'])
        self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['archived'], False)
        self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['displayPublic'], variables['input']['displayPublic'])


    def test_create_location_room_permission_denied(self):
        """ Check create location room permission denied error message """
        query = self.location_room_create_mutation
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


    def test_update_location_room(self):
        """ Update a location room """
        query = self.location_room_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateOrganizationLocationRoom']['organizationLocationRoom']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationLocationRoom']['organizationLocationRoom']['displayPublic'], variables['input']['displayPublic'])


    def test_update_location_room_anon_user(self):
        """ Don't allow updating location rooms for non-logged in users """
        query = self.location_room_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_location_room_permission_granted(self):
        """ Allow updating location rooms for users with permissions """
        query = self.location_room_update_mutation
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
        self.assertEqual(data['updateOrganizationLocationRoom']['organizationLocationRoom']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationLocationRoom']['organizationLocationRoom']['displayPublic'], variables['input']['displayPublic'])


    def test_update_location_room_permission_denied(self):
        """ Check update location room permission denied error message """
        query = self.location_room_update_mutation
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


    def test_archive_location_room(self):
        """ Archive a location room"""
        query = self.location_room_archive_mutation
        variables = self.variables_archive

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationLocationRoom']['organizationLocationRoom']['archived'], variables['input']['archived'])


    def test_archive_location_room_anon_user(self):
        """ Archive a location room """
        query = self.location_room_archive_mutation
        variables = self.variables_archive

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_location_room_permission_granted(self):
        """ Allow archiving locations for users with permissions """
        query = self.location_room_archive_mutation
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
        self.assertEqual(data['archiveOrganizationLocationRoom']['organizationLocationRoom']['archived'], variables['input']['archived'])


    def test_archive_location_room_permission_denied(self):
        """ Check archive location room permission denied error message """
        query = self.location_room_archive_mutation
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

