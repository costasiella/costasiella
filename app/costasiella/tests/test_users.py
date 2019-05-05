import graphene
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from .factories import AdminFactory
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema as cs_schema


# Create schema object
schema = graphene.Schema(
    query=cs_schema.Query,
    mutation=cs_schema.Mutation
)

admin_email = 'admin@costasiella.com'
admin_password = 'CSAdmin1#'


class GQLAccount(TestCase):

    def test_query_user(self):
        # This is the test method.
        # Let's assume that there's a user object "my_test_user" that was already setup        
        query = '''
{
  account {
    id
    firstName
    lastName
  }
}
        '''
        admin_user = AdminFactory.create()
        executed = execute_test_client_api_query(query, admin_user)
        data = executed.get('data')
        self.assertEqual(data['account']['firstName'], admin_user.first_name)
        self.assertEqual(data['account']['lastName'], admin_user.last_name)
