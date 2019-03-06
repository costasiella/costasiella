# from graphql.error.located_error import GraphQLLocatedError
import graphql

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from .factories import AdminFactory, RegularUserFactory, SchoolLocationFactory
from .helpers import execute_test_client_api_query
from .. import models

## Use django client?
# https://www.sam.today/blog/testing-graphql-with-graphene-django/
# https://stackoverflow.com/questions/45493295/testing-graphene-django


class GQLSchoolLocation(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = AdminFactory.create()
        self.anon_user = AnonymousUser()

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of locations """
        query = '''
  query SchoolLocations($archived: Boolean!) {
    schoolLocations(archived:$archived) {
      id
      name
      displayPublic
      archived
    }
  }
        '''
        location = SchoolLocationFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['schoolLocations'][0]['name'], location.name)
        self.assertEqual(data['schoolLocations'][0]['archived'], location.archived)
        self.assertEqual(data['schoolLocations'][0]['displayPublic'], location.display_public)


    def test_query_anon_user(self):
        """ Query list of locations """
        query = '''
  query SchoolLocations($archived: Boolean!) {
    schoolLocations(archived:$archived) {
      id
      name
      displayPublic
      archived
    }
  }
        '''
        location = SchoolLocationFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one location """   
        query = '''
query getSchoolLocation($id: ID!) {
    schoolLocation(id:$id) {
      id
      name
      displayPublic
      archived
    }
  }
        '''
        location = SchoolLocationFactory.create()
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": location.id})
        data = executed.get('data')
        self.assertEqual(data['schoolLocation']['name'], location.name)
        self.assertEqual(data['schoolLocation']['archived'], location.archived)
        self.assertEqual(data['schoolLocation']['displayPublic'], location.display_public)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one location """   
        query = '''
query getSchoolLocation($id: ID!) {
    schoolLocation(id:$id) {
      id
      name
      displayPublic
      archived
    }
  }
        '''
        location = SchoolLocationFactory.create()
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": location.id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        query = '''
query getSchoolLocation($id: ID!) {
    schoolLocation(id:$id) {
      id
      name
      displayPublic
      archived
    }
  }
        '''
        # Create regular user
        user = RegularUserFactory.create()
        location = SchoolLocationFactory.create()

        executed = execute_test_client_api_query(query, user, variables={"id": location.id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        query = '''
query getSchoolLocation($id: ID!) {
    schoolLocation(id:$id) {
      id
      name
      displayPublic
      archived
    }
  }
        '''
        # Create regular user
        user = RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_schoollocation')
        user.user_permissions.add(permission)
        user.save()

        location = SchoolLocationFactory.create()

        executed = execute_test_client_api_query(query, user, variables={"id": location.id})
        data = executed.get('data')
        self.assertEqual(data['schoolLocation']['name'], location.name)


    def test_create_location(self):
        """ Create a location """
        query = '''
mutation CreateSchoolLocation($name: String!, $displayPublic:Boolean!) {
    createSchoolLocation(name: $name, displayPublic: $displayPublic) {
        schoolLocation {
            id
            archived
            name
            displayPublic
        }
    }
}
        '''

        variables = {
            "name": "New location",
            "displayPublic": True
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createSchoolLocation']['schoolLocation']['name'], variables['name'])
        self.assertEqual(data['createSchoolLocation']['schoolLocation']['archived'], False)
        self.assertEqual(data['createSchoolLocation']['schoolLocation']['displayPublic'], variables['displayPublic'])


    def test_update_location(self):
        """ Update a location """
        query = '''
mutation UpdateSchoolLocation($id: ID!, $name: String!, $displayPublic:Boolean!) {
    updateSchoolLocation(id: $id, name: $name, displayPublic: $displayPublic) {
        schoolLocation {
        id
        archived
        name
        displayPublic
        }
    }
}
        '''
        location = SchoolLocationFactory.create()

        variables = {
            "id": location.id,
            "name": "Updated name",
            "displayPublic": False
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateSchoolLocation']['schoolLocation']['name'], variables['name'])
        self.assertEqual(data['updateSchoolLocation']['schoolLocation']['archived'], False)
        self.assertEqual(data['updateSchoolLocation']['schoolLocation']['displayPublic'], variables['displayPublic'])


    def test_archive_location(self):
        """ Archive a location """
        query = '''
mutation ArchiveSchoolLocation($id: ID!, $archived: Boolean!) {
    archiveSchoolLocation(id: $id, archived: $archived) {
        schoolLocation {
        id
        archived
        }
    }
}
        '''
        location = SchoolLocationFactory.create()

        variables = {
            "id": location.id,
            "archived": True
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveSchoolLocation']['schoolLocation']['archived'], variables['archived'])
