# from graphql.error.located_error import GraphQLLocatedError
import os
import shutil
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
from .helpers import clean_media, execute_test_client_api_query
from .. import models
from .. import schema

from app.settings.development import MEDIA_ROOT


class GQLAccountDocument(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountdocument'
        self.permission_add = 'add_accountdocument'
        self.permission_change = 'change_accountdocument'
        self.permission_delete = 'delete_accountdocument'

        self.account_document = f.AccountDocumentFactory.create()

        self.variables_query_list = {
            "account": to_global_id("AccountNode", self.account_document.account.id)
        }

        self.variables_query_one = {
            "id": to_global_id("AccountDocumentNode", self.account_document.id)
        }

        with open(os.path.join(os.getcwd(), "costasiella", "tests", "files", "test_image.txt"), 'r') as input_file:
            input_image = input_file.read().replace("\n", "")

            self.variables_create = {
                "input": {
                  "account": to_global_id("AccountNode", self.account_document.account.id),
                  "description": "test_image.jpg",
                  "documentFileName": "test_image.jpg",
                  "document": input_image
                }
            }

            self.variables_update = {
                "input": {
                    "id": to_global_id("AccountDocumentNode", self.account_document.id),
                    "description": "new description here",
                }
            }

        self.variables_delete = {
            "input": {
                "id": to_global_id("AccountDocumentNode", self.account_document.id)
            }
        }

        self.account_documents_query = '''
  query AccountDocuments($account: ID!) {
    accountDocuments(account:$account) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          description
          urlProtectedDocument
          createdAt
        }
      }
    }
  }
'''

        self.account_document_query = '''
  query AccountDocument($id: ID!) {
    accountDocument(id:$id) {
      id
      description
      urlProtectedDocument
    }
  }
'''

        self.account_document_create_mutation = ''' 
  mutation CreateAccountDocument($input:CreateAccountDocumentInput!) {
    createAccountDocument(input: $input) {
      accountDocument{
        id
        account {
            id
        }
        description
        urlProtectedDocument
      }
    }
  }
'''

        self.account_document_update_mutation = '''
  mutation UpdateAccountDocument($input:UpdateAccountDocumentInput!) {
    updateAccountDocument(input: $input) {
      accountDocument{
        id
        account {
            id
        }
        description
        urlProtectedDocument
      }
    }
  }
'''

        self.account_document_delete_mutation = '''
  mutation DeleteAccountDocument($input:DeleteAccountDocumentInput!) {
    deleteAccountDocument(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        clean_media()

    def test_query(self):
        """ Query list of account documents """
        query = self.account_documents_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['accountDocuments']['edges'][0]['node']['id'],
            to_global_id('AccountDocumentNode', self.account_document.id)
        )
        self.assertEqual(data['accountDocuments']['edges'][0]['node']['description'],
                         self.account_document.description)
        self.assertNotEqual(data['accountDocuments']['edges'][0]['node']['urlProtectedDocument'], False)

    def test_query_permission_granted(self):
        """ Query list of account documents """
        query = self.account_documents_query
        user = self.account_document.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['accountDocuments']['edges'][0]['node']['id'],
            to_global_id('AccountDocumentNode', self.account_document.id)
        )

    def test_query_permission_denied(self):
        """ Query list of account documents """
        query = self.account_documents_query
        user = self.account_document.account

        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], "Permission denied!")

    def test_query_anon_user(self):
        """ Query list of account documents """
        query = self.account_documents_query
        user = self.account_document.account

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], "Not logged in!")

    def test_query_one(self):
        """ Query one account document """
        query = self.account_document_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['accountDocument']['id'], self.variables_query_one['id'])
        self.assertEqual(data['accountDocument']['description'], self.account_document.description)
        self.assertNotEqual(data['accountDocument']['urlProtectedDocument'], False)

    def test_query_one_permission_granted(self):
        """ Query one account document with user having permissions """
        query = self.account_document_query
        user = self.account_document.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['accountDocument']['id'], self.variables_query_one['id'])
        self.assertEqual(data['accountDocument']['description'], self.account_document.description)
        self.assertNotEqual(data['accountDocument']['urlProtectedDocument'], False)

    def test_query_one_permission_denied(self):
        """ Query one account document - permission denied """
        query = self.account_document_query
        user = self.account_document.account

        executed = execute_test_client_api_query(query, user, variables=self.variables_query_one)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], "Permission denied!")

    def test_query_one_anon_user(self):
        """ Query one account document - not logged in """
        query = self.account_document_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_one)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], "Not logged in!")

    def test_create_account_document(self):
        """ Create account document """
        query = self.account_document_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['createAccountDocument']['accountDocument']['description'],
                         variables['input']['description'])
        self.assertNotEqual(data['createAccountDocument']['accountDocument']['urlProtectedDocument'], "")

        account_document = models.AccountDocument.objects.last()
        self.assertNotEqual(account_document.document, None)

    def test_create_account_document_anon_user(self):
        """ Don't allow creating account document for non-logged in users """
        query = self.account_document_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_account_document_permission_granted(self):
        """ Allow creating account document for users with permissions """
        query = self.account_document_create_mutation

        # Create regular user
        user = self.account_document.account
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
        self.assertEqual(data['createAccountDocument']['accountDocument']['description'],
                         variables['input']['description'])

    def test_create_account_document_permission_denied(self):
        """ Check create account document permission denied error message """
        query = self.account_document_create_mutation
        variables = self.variables_create

        # Create regular user
        user = self.account_document.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_account_document(self):
        """ Update account document """
        query = self.account_document_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateAccountDocument']['accountDocument']['description'],
                         variables['input']['description'])

    def test_update_account_document_anon_user(self):
        """ Don't allow updating account document for non-logged in users """
        query = self.account_document_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_account_document_permission_granted(self):
        """ Allow updating account document for users with permissions """
        query = self.account_document_update_mutation
        variables = self.variables_update

        # Create regular user
        user = self.account_document.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateAccountDocument']['accountDocument']['description'],
                         variables['input']['description'])

    def test_update_account_document_permission_denied(self):
        """ Check update account document permission denied error message """
        query = self.account_document_update_mutation
        variables = self.variables_update

        # Create regular user
        user = self.account_document.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_account_document(self):
        """ Delete a account document """
        query = self.account_document_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['deleteAccountDocument']['ok'], True)

        exists = models.OrganizationDocument.objects.exists()
        self.assertEqual(exists, False)

    def test_delete_account_document_anon_user(self):
        """ Delete a account document """
        query = self.account_document_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_account_document_permission_granted(self):
        """ Allow deleting schedule event medias for users with permissions """
        query = self.account_document_delete_mutation
        variables = self.variables_delete

        # Create regular user
        user = self.account_document.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountDocument']['ok'], True)

    def test_delete_account_document_permission_denied(self):
        """ Check delete account document permission denied error message """
        query = self.account_document_delete_mutation
        variables = self.variables_delete

        # Create regular user
        user = self.account_document.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
