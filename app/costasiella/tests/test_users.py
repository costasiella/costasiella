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
        create a user
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


#     def test_tokenAuth(self):
#         """
#         Get user token
#         """
#         client = Client(schema)
#         executed = client.execute(
# '''
# mutation TokenAuth($username: String!, $password: String!) {
#     tokenAuth(username: $username, password: $password) {
#         token
#     }
# }
# ''', variables={'username': admin_email, 'password': admin_password })
#         print(executed)
#         # token = executed['data']['tokenAuth']['token']
#         # print(token)
#         # assert len(token) > 0
