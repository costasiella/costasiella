from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from .factories import AdminFactory, SchoolLocationFactory
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
