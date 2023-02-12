# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema

from graphql_relay import to_global_id


class GQLAccountBankAccountMandate(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_account = 'view_account'
        self.permission_view_bank_account = 'view_accountbankaccount'
        self.permission_view = 'view_accountbankaccountmandate'
        self.permission_add = 'add_accountbankaccountmandate'
        self.permission_change = 'change_accountbankaccountmandate'
        self.permission_delete = 'delete_accountbankaccountmandate'

        self.variables_create = {
            "input": {
                "reference": "987878-dvg",
                "content": "Content here",
                "signatureDate": "2020-01-01"
            }
        }

        self.variables_update = {
            "input": {
                "reference": "987878-dvg",
                "content": "Content here",
                "signatureDate": "2020-01-01"
            }
        }

        self.variables_delete = {
            "input": {}
        }

        self.account_bank_account_mandates_query = '''
  query AccountBankAccountMandates($after: String, $before: String, $accountBankAccount: ID!) {
    accountBankAccountMandates(
      first: 100, 
      before: $before, 
      after: $after, 
      accountBankAccount: $accountBankAccount
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          accountBankAccount {
            id
            account {
              id
            }
          }
          reference
          content
          signatureDate
        }
      }
    }
  }
'''

        self.account_bank_account_mandate_query = '''
  query AccountBankAccountMandate($id: ID!) {
    accountBankAccountMandate(id:$id) {
      id
      accountBankAccount {
        id
      }
      reference
      content
      signatureDate
    }
  }
'''

        self.account_bank_account_mandate_create_mutation = ''' 
  mutation CreateAccountBankAccountMandate($input:CreateAccountBankAccountMandateInput!) {
    createAccountBankAccountMandate(input: $input) {
      accountBankAccountMandate {
          id
          accountBankAccount {
            id
          }
          reference
          content
          signatureDate
      }
    }
  }
'''

        self.account_bank_account_mandate_update_mutation = '''
  mutation UpdateAccountBankAccountMandate($input:UpdateAccountBankAccountMandateInput!) {
    updateAccountBankAccountMandate(input: $input) {
      accountBankAccountMandate {
          id
          accountBankAccount {
            id
          }
          reference
          content
          signatureDate
      }
    }
  }
'''

        self.account_bank_account_mandate_archive_mutation = '''
  mutation DeleteAccountBankAccountMandate($input:DeleteAccountBankAccountMandateInput!) {
    deleteAccountBankAccountMandate(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account bank account mandates """
        query = self.account_bank_account_mandates_query
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()

        variables = {
            'accountBankAccount': to_global_id('AccountBankAccountNode',
                                               account_bank_account_mandate.account_bank_account.pk),
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountBankAccountMandates']['edges'][0]['node']['accountBankAccount']['id'],
            variables['accountBankAccount']
        )
        self.assertEqual(data['accountBankAccountMandates']['edges'][0]['node']['reference'],
                         account_bank_account_mandate.reference)
        self.assertEqual(data['accountBankAccountMandates']['edges'][0]['node']['content'],
                         account_bank_account_mandate.content)
        self.assertEqual(data['accountBankAccountMandates']['edges'][0]['node']['signatureDate'],
                         str(account_bank_account_mandate.signature_date))

    def test_query_permission_denied_other_account_mandates(self):
        """ Only users's own mandates should be shown """
        query = self.account_bank_account_mandates_query
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()

        variables = {
            'accountBankAccount': to_global_id('AccountBankAccountNode',
                                               account_bank_account_mandate.account_bank_account.pk),
        }

        # Create regular user
        user = f.InstructorFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['accountBankAccountMandates'], None)

    def test_query_permission_denied_own_account_mandates(self):
        """ Only users's own mandates should be shown """
        query = self.account_bank_account_mandates_query
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()

        variables = {
            'accountBankAccount': to_global_id('AccountBankAccountNode',
                                               account_bank_account_mandate.account_bank_account.pk),
        }

        # Create regular user
        user = account_bank_account_mandate.account_bank_account.account
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['accountBankAccountMandates']['edges'][0]['node']['accountBankAccount']['id'],
            variables['accountBankAccount']
        )

    def test_query_permission_granted(self):
        """ With permissions, other users' mandates should be visible """
        query = self.account_bank_account_mandates_query
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()

        variables = {
            'accountBankAccount': to_global_id('AccountBankAccountNode',
                                               account_bank_account_mandate.account_bank_account.pk),
        }

        # Create regular user
        user = f.InstructorFactory.create()
        permission = Permission.objects.get(codename='view_accountbankaccountmandate')
        user.user_permissions.add(permission)
        # View bank account
        permission = Permission.objects.get(codename=self.permission_view_bank_account)
        user.user_permissions.add(permission)
        # View bank account
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        user.save()
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # The mandate of another use should be listed
        self.assertEqual(
            data['accountBankAccountMandates']['edges'][0]['node']['accountBankAccount']['id'],
            variables['accountBankAccount']
        )

    def test_query_anon_user(self):
        """ Anon users shouldn't be able to view mandates """
        query = self.account_bank_account_mandates_query
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        variables = {
            'accountBankAccount': to_global_id('AccountBankAccountNode',
                                               account_bank_account_mandate.account_bank_account.pk),
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account bank account mandate """
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('AccountBankAccountMandateNode', account_bank_account_mandate.pk)

        # Now query single location and check
        query = self.account_bank_account_mandate_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['accountBankAccountMandate']['accountBankAccount']['id'],
          to_global_id('AccountBankAccountNode', account_bank_account_mandate.account_bank_account.pk))
        self.assertEqual(data['accountBankAccountMandate']['reference'], account_bank_account_mandate.reference)
        self.assertEqual(data['accountBankAccountMandate']['content'], account_bank_account_mandate.content)
        self.assertEqual(data['accountBankAccountMandate']['signatureDate'],
                         str(account_bank_account_mandate.signature_date))

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one location room """
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('AccountBankAccountMandateNode', account_bank_account_mandate.pk)

        # Now query single location and check
        query = self.account_bank_account_mandate_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        user = account_bank_account_mandate.account_bank_account.account

        # First query locations to get node id easily
        node_id = to_global_id('AccountBankAccountMandateNode', account_bank_account_mandate.pk)

        # Now query single location and check
        query = self.account_bank_account_mandate_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        user = f.InstructorFactory.create()
        permission = Permission.objects.get(codename='view_accountbankaccountmandate')
        user.user_permissions.add(permission)
        # View bank account
        permission = Permission.objects.get(codename=self.permission_view_bank_account)
        user.user_permissions.add(permission)
        user.save()
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()

        # Now query single location and check
        query = self.account_bank_account_mandate_query
        executed = execute_test_client_api_query(query, user, variables={"id": to_global_id(
            "AccountBankAccountMandateNode", account_bank_account_mandate.id
        )})
        data = executed.get('data')
        self.assertEqual(data['accountBankAccountMandate']['accountBankAccount']['id'],
          to_global_id('AccountBankAccountNode', account_bank_account_mandate.account_bank_account.pk))

    def test_create_account_bank_account_mandate(self):
        """ Create a location room """
        query = self.account_bank_account_mandate_create_mutation
        account_bank_account = f.AccountBankAccountFactory.create()
        variables = self.variables_create
        variables['input']['accountBankAccount'] = to_global_id('AccountBankAccountNode', account_bank_account.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
          data['createAccountBankAccountMandate']['accountBankAccountMandate']['accountBankAccount']['id'],
          variables['input']['accountBankAccount'])

    def test_create_account_bank_account_mandate_anon_user(self):
        """ Don't allow creating locations rooms for non-logged in users """
        query = self.account_bank_account_mandate_create_mutation
        account_bank_account = f.AccountBankAccountFactory.create()
        variables = self.variables_create
        variables['input']['accountBankAccount'] = to_global_id('AccountBankAccountNode', account_bank_account.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_account_bank_account_mandate_permission_granted(self):
        """ Allow creating location rooms for users with permissions """
        query = self.account_bank_account_mandate_create_mutation
        account_bank_account = f.AccountBankAccountFactory.create()
        variables = self.variables_create
        variables['input']['accountBankAccount'] = to_global_id('AccountBankAccountNode', account_bank_account.pk)

        # Create regular user
        user = account_bank_account.account
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
          data['createAccountBankAccountMandate']['accountBankAccountMandate']['accountBankAccount']['id'],
          variables['input']['accountBankAccount'])

    def test_create_account_bank_account_mandate_permission_denied(self):
        """ Check create location room permission denied error message """
        query = self.account_bank_account_mandate_create_mutation
        account_bank_account = f.AccountBankAccountFactory.create()
        variables = self.variables_create
        variables['input']['accountBankAccount'] = to_global_id('AccountBankAccountNode', account_bank_account.pk)

        # Create regular user
        user = account_bank_account.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_account_bank_account_mandate(self):
        """ Update a bank account mandate """
        query = self.account_bank_account_mandate_update_mutation
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("AccountBankAccountMandateNode", account_bank_account_mandate.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
          data['updateAccountBankAccountMandate']['accountBankAccountMandate']['reference'],
          variables['input']['reference'])
        self.assertEqual(
          data['updateAccountBankAccountMandate']['accountBankAccountMandate']['content'],
          variables['input']['content'])
        self.assertEqual(
          data['updateAccountBankAccountMandate']['accountBankAccountMandate']['signatureDate'],
          variables['input']['signatureDate'])

    def test_update_account_bank_account_mandate_anon_user(self):
        """ Don't allow updating bank account mandates for non-logged in users """
        query = self.account_bank_account_mandate_update_mutation
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("AccountBankAccountMandateNode", account_bank_account_mandate.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_account_bank_account_mandate_permission_granted(self):
        """ Allow updating bank account mandate for users with permissions """
        query = self.account_bank_account_mandate_update_mutation
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("AccountBankAccountMandateNode", account_bank_account_mandate.pk)

        # Create regular user
        user = account_bank_account_mandate.account_bank_account.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        # View bank account
        permission = Permission.objects.get(codename=self.permission_view_bank_account)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
          data['updateAccountBankAccountMandate']['accountBankAccountMandate']['reference'],
          variables['input']['reference'])

    def test_update_account_bank_account_mandate_permission_denied(self):
        """ Check update bank account mandate permission denied error message """
        query = self.account_bank_account_mandate_update_mutation
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("AccountBankAccountMandateNode", account_bank_account_mandate.pk)

        # Create regular user
        user = account_bank_account_mandate.account_bank_account.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_account_bank_account_mandate(self):
        """ Archive a account bank account mandate"""
        query = self.account_bank_account_mandate_archive_mutation
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("AccountBankAccountMandateNode", account_bank_account_mandate.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountBankAccountMandate']['ok'], True)

    def test_delete_account_bank_account_mandate_anon_user(self):
        """ Anon users shouldn't be able to delete a account bank account mandate """
        query = self.account_bank_account_mandate_archive_mutation
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("AccountBankAccountMandateNode", account_bank_account_mandate.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_account_bank_account_mandate_permission_granted(self):
        """ Allow deleting bank account mandates for users with permissions """
        query = self.account_bank_account_mandate_archive_mutation
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("AccountBankAccountMandateNode", account_bank_account_mandate.pk)

        # Create regular user
        user = f.InstructorFactory.create()
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountBankAccountMandate']['ok'], True)

    def test_delete_account_bank_account_mandate_permission_denied(self):
        """ Check delete mandate permission denied error message """
        query = self.account_bank_account_mandate_archive_mutation
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("AccountBankAccountMandateNode", account_bank_account_mandate.pk)

        # Create regular user
        user = f.InstructorFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

