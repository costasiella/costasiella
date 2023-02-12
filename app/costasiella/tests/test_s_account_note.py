# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser, Permission

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema


class GQLAccountNote(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountnote'
        self.permission_view_backoffice = 'view_accountnotebackoffice'
        self.permission_view_instructors = 'view_accountnoteinstructors'
        self.permission_view_account = 'view_account'
        self.permission_add = 'add_accountnote'
        self.permission_change = 'change_accountnote'
        self.permission_delete = 'delete_accountnote'

        self.variables_create = {
            "input": {
                "noteType": "BACKOFFICE",
                "note": "hello world",
                "injury": False,
            }
        }

        self.variables_update = {
            "input": {
                "note": "hello world",
                "injury": False,
            }
        }

        self.variables_delete = {
            "input": {}
        }

        self.account_notes_query = '''
  query AccountNotes($after: String, $before: String, $account: ID!, $noteType: CostasiellaAccountNoteNoteTypeChoices!) {
    accountNotes(first: 15, before: $before, after: $after, account: $account, noteType: $noteType ) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          account {
            id
          }
          note
          injury
          processed
          noteType
          noteBy {
            id
            fullName
          }
          createdAt
        }
      }
    }
  }
'''

        self.account_note_query = '''
  query AccountNote($id: ID!) {
    accountNote(id: $id) {
      id
      account {
        id
      }
      note
      injury
      processed
      noteType
      noteBy {
        id
        fullName
      }
      createdAt
    }
  }
'''

        self.account_note_create_mutation = ''' 
  mutation CreateAccountNote($input: CreateAccountNoteInput!) {
    createAccountNote(input: $input) {
      accountNote {
          id
          account {
            id
          }
          note
          injury
          processed
          noteType
          noteBy {
            id
            fullName
          }
          createdAt
      }
    }
  }
'''

        self.account_note_update_mutation = '''
  mutation UpdateAccountNote($input: UpdateAccountNoteInput!) {
    updateAccountNote(input: $input) {
      accountNote {
          id
          account {
            id
          }
          note
          injury
          processed
          noteType
          noteBy {
            id
            fullName
          }
          createdAt
      }
    }
  }
'''

        self.account_note_delete_mutation = '''
  mutation DeleteAccountNote($input: DeleteAccountNoteInput!) {
    deleteAccountNote(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account account_notes """
        query = self.account_notes_query
        account_note = f.AccountNoteBackofficeFactory.create()
        variables = {
            'account': to_global_id('AccountNoteNode', account_note.account.id),
            'noteType': "BACKOFFICE"
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)

        data = executed.get('data')
        self.assertEqual(
            data['accountNotes']['edges'][0]['node']['account']['id'],
            to_global_id("AccountNode", account_note.account.id)
        )
        self.assertEqual(
            data['accountNotes']['edges'][0]['node']['noteBy']['id'],
            to_global_id("AccountNode", account_note.note_by.id)
        )
        self.assertEqual(data['accountNotes']['edges'][0]['node']['note'], account_note.note)
        self.assertEqual(data['accountNotes']['edges'][0]['node']['noteType'], account_note.note_type)
        self.assertEqual(data['accountNotes']['edges'][0]['node']['injury'], account_note.injury)
        self.assertEqual(data['accountNotes']['edges'][0]['node']['processed'], account_note.processed)

    def test_query_permission_denied(self):
        """ Query list of account account_notes - check permission denied """
        query = self.account_notes_query
        account_note = f.AccountNoteBackofficeFactory.create()
        variables = {
            'account': to_global_id('AccountNoteNode', account_note.account.id),
            'noteType': "BACKOFFICE"
        }

        # Create regular user
        user = get_user_model().objects.get(pk=account_note.account.id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of account account_notes with view permission """
        query = self.account_notes_query
        account_note = f.AccountNoteBackofficeFactory.create()
        variables = {
            'account': to_global_id('AccountNoteNode', account_note.account.id),
            'noteType': "BACKOFFICE"
        }

        # Create regular user
        user = get_user_model().objects.get(pk=account_note.account.id)
        permission = Permission.objects.get(codename='view_accountnote')
        user.user_permissions.add(permission)
        # View account
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List account_notes
        self.assertEqual(
            data['accountNotes']['edges'][0]['node']['account']['id'],
            to_global_id("AccountNode", account_note.account.id)
        )

    def test_query_anon_user(self):
        """ Query list of account account_notes - anon user """
        query = self.account_notes_query
        account_note = f.AccountNoteBackofficeFactory.create()
        variables = {
            'account': to_global_id('AccountNoteNode', account_note.account.id),
            'noteType': "BACKOFFICE"
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account account_note as admin """
        account_note = f.AccountNoteBackofficeFactory.create()

        variables = {
            "id": to_global_id("AccountNoteNode", account_note.id),
        }

        # Now query single account_note and check
        executed = execute_test_client_api_query(self.account_note_query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountNote']['account']['id'],
            to_global_id('AccountNode', account_note.account.id)
        )
        self.assertEqual(
            data['accountNote']['noteBy']['id'],
            to_global_id('AccountNode', account_note.note_by.id)
        )
        self.assertEqual(data['accountNote']['note'], account_note.note)
        self.assertEqual(data['accountNote']['noteType'], account_note.note_type)
        self.assertEqual(data['accountNote']['injury'], account_note.injury)
        self.assertEqual(data['accountNote']['processed'], account_note.processed)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account account_note """
        account_note = f.AccountNoteBackofficeFactory.create()

        variables = {
            "id": to_global_id("AccountNoteNode", account_note.id),
        }

        # Now query single account_note and check
        executed = execute_test_client_api_query(self.account_note_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        account_note = f.AccountNoteBackofficeFactory.create()
        user = account_note.account

        variables = {
            "id": to_global_id("AccountNoteNode", account_note.id),
        }

        # Now query single account_note and check
        executed = execute_test_client_api_query(self.account_note_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        account_note = f.AccountNoteBackofficeFactory.create()
        user = account_note.account
        # General view permission
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        # View backoffice notes permission
        permission = Permission.objects.get(codename=self.permission_view_backoffice)
        user.user_permissions.add(permission)
        # View account
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)

        user.save()

        variables = {
            "id": to_global_id("AccountNoteNode", account_note.id),
        }

        # Now query single account_note and check
        executed = execute_test_client_api_query(self.account_note_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountNote']['account']['id'],
            to_global_id('AccountNode', account_note.account.id)
        )

    def test_create_account_note(self):
        """ Create an account account_note """
        query = self.account_note_create_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountNote']['accountNote']['account']['id'],
            variables['input']['account']
        )
        self.assertEqual(
            data['createAccountNote']['accountNote']['noteBy']['id'],
            to_global_id("AccountNode", self.admin_user.id)
        )
        self.assertEqual(
            data['createAccountNote']['accountNote']['note'],
            variables['input']['note']
        )
        self.assertEqual(
            data['createAccountNote']['accountNote']['injury'],
            variables['input']['injury']
        )

    def test_create_account_note_anon_user(self):
        """ Don't allow creating account account_notes for non-logged in users """
        query = self.account_note_create_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_account_note_permission_granted(self):
        """ Allow creating account_notes for users with permissions """
        query = self.account_note_create_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)

        # Create regular user
        user = account
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
            data['createAccountNote']['accountNote']['account']['id'],
            variables['input']['account']
        )

    def test_create_account_note_permission_denied(self):
        """ Check create account_note permission denied error message """
        query = self.account_note_create_mutation
        account = f.RegularUserFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)

        # Create regular user
        user = account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_account_note(self):
        """ Update a account_note """
        query = self.account_note_update_mutation
        account_note = f.AccountNoteBackofficeFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountNoteNode', account_note.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')

        self.assertEqual(
            data['updateAccountNote']['accountNote']['account']['id'],
            to_global_id("AccountNode", account_note.account.id)
        )
        self.assertEqual(
            data['updateAccountNote']['accountNote']['note'],
            variables['input']['note']
        )
        self.assertEqual(
            data['updateAccountNote']['accountNote']['injury'],
            variables['input']['injury']
        )

    def test_update_account_note_anon_user(self):
        """ Don't allow updating account_notes for non-logged in users """
        query = self.account_note_update_mutation
        account_note = f.AccountNoteBackofficeFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountNoteNode', account_note.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_account_note_permission_granted(self):
        """ Allow updating account_notes for users with permissions """
        query = self.account_note_update_mutation
        account_note = f.AccountNoteBackofficeFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountNoteNode', account_note.id)

        user = account_note.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        # View account
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
            data['updateAccountNote']['accountNote']['account']['id'],
            to_global_id("AccountNode", account_note.account.id)
        )

    def test_update_account_note_permission_denied(self):
        """ Check update account_note permission denied error message """
        query = self.account_note_update_mutation
        account_note = f.AccountNoteBackofficeFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountNoteNode', account_note.id)

        user = account_note.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_account_note(self):
        """ Delete an account account_note """
        query = self.account_note_delete_mutation
        account_note = f.AccountNoteBackofficeFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('AccountNoteNode', account_note.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountNote']['ok'], True)

    def test_delete_account_note_anon_user(self):
        """ Delete account_note denied for anon user """
        query = self.account_note_delete_mutation
        account_note = f.AccountNoteBackofficeFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('AccountNoteNode', account_note.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_account_note_permission_granted(self):
        """ Allow deleting account_notes for users with permissions """
        query = self.account_note_delete_mutation
        account_note = f.AccountNoteBackofficeFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('AccountNoteNode', account_note.id)

        # Give permissions
        user = account_note.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountNote']['ok'], True)

    def test_delete_account_note_permission_denied(self):
        """ Check delete account_note permission denied error message """
        query = self.account_note_delete_mutation
        account_note = f.AccountNoteBackofficeFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('AccountNoteNode', account_note.id)

        user = account_note.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
