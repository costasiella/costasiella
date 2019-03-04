import graphene
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from .. import models
from .. import schema as cs_schema

# Create schema object
schema = graphene.Schema(
    query=cs_schema.Query,
    mutation=cs_schema.Mutation
)

admin_email = 'admin@costasiella.com'
admin_password = 'CSAdmin1#'


class GQL_users(TestCase):

    def test_create(self):
        """
        create a SchoolLocation using GQL
        """
        client = Client(schema)
        executed = client.execute(
'''
    mutation CreateUser($email: String!, $password: String!) {
        createUser(email: $email, password: $password) {
            user {
            id
            email
            }
        }
    }
''', variables={'email': admin_email, 'password': admin_password })
        assert executed == {
            "data": {
                "createUser": {
                "user": {
                    "id": "1",
                    "email": admin_email
                }
                }
            }
        }
