import os
import shutil

import graphene
from django.test import RequestFactory
from graphene.test import Client

from .. import schema as cs_schema

from app.settings.development import MEDIA_ROOT


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


def clean_media():
    """ Clean up media files """
    if 'GITHUB_WORKFLOW' not in os.environ:
        # Clean test media root after each test to prevent stray files after testing
        # But don't run on Travis-CI, as we don't seem to be allowed to remove stuff from dirs
        # in the tests
        for root, dirs, files in os.walk(MEDIA_ROOT):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        # write gitignore for media root
        with open(os.path.join(MEDIA_ROOT, ".gitignore"), 'w') as file_writer:
            file_writer.write("# Ignore everything in this directory\n")
            file_writer.write("*\n")
            file_writer.write("# Except this file\n")
            file_writer.write("!.gitignore\n")
