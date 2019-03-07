import graphene
from django.test import RequestFactory
from graphene.test import Client

from .. import schema as cs_schema


# Create schema object
schema = graphene.Schema(
    query=cs_schema.Query,
    mutation=cs_schema.Mutation
)


def execute_test_client_api_query(query, user=None, variables=None, **kwargs):
    """
    Returns the results of executing a graphQL query using the graphene test client.  This is a helper method for our tests
    """
    request_factory = RequestFactory()
    context = request_factory.get('/graphql/')
    context.user = user
    client = Client(schema)
    executed = client.execute(query, context=context, variables=variables, **kwargs)
    return executed
