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
    def test_query_one(self):
        # This is the test method.
        # Let's assume that there's a user object "my_test_user" that was already setup        
        query = '''
query SchoolLocation($id: ID!) {
    schoolLocation(id: $id) {
        id
        name
        archived
        displayPublic
    }
}
        '''
        admin_user = AdminFactory.create()
        # print('admin:')
        # print(admin_user)
        location = SchoolLocationFactory.create()
        print ('location:')
        print(location)
        print(location.id)

        executed = execute_test_client_api_query(query, admin_user, variables={"id": 1})
        print(executed)
        data = executed.get('data')
        self.assertEqual(data['schoolLocation']['name'], location.name)
        self.assertEqual(data['schoolLocation']['archived'], location.archived)
        self.assertEqual(data['schoolLocation']['displayPublic'], location.display_public)

# class GQL_school_location(TestCase):

#     def test_create(self):
#         """
#         create a SchoolLocation using GQL
#         """
#         class MockUser:
#             is_authenticated = True

#         client = Client(schema)
#         executed = client.execute(
# '''
#     mutation CreateSchoolLocation($name: String!, $displayPublic:Boolean!) {
#         createSchoolLocation(name: $name, displayPublic: $displayPublic) {
#         id
#         name
#         displayPublic
#         }
#     }
# ''',
# variables={'name': 'test', 'displayPublic': True},
# info={
#     'context': {
#         'user': MockUser()
#         }
#     }
# )
#         print(executed)
#         assert 1 == 1
