# from graphql.error.located_error import GraphQLLocatedError
import graphql
import datetime

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


class GQLAccountBankAccount(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = []

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountbankaccount'
        self.permission_add = 'add_accountbankaccount'
        self.permission_change = 'change_accountbankaccount'
        self.permission_delete = 'delete_accountbankaccount'

        self.variables_update = {
            "input": {
                "number": "12345AB",
                "holder": "Account Holder",
                "bic": "ABNANL2A"
            }
        }

        self.accountbankaccounts_query = '''
  query AccountBankAccounts($after: String, $before: String, $account: ID!) {
    accountBankAccounts(
      first: 1, 
      before: $before, 
      after: $after, 
      account: $account
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
          account {
            id
          }
          number
          holder
          bic
        }
      }
    }
  }
'''

        self.account_bank_account_update_mutation = '''
  mutation UpdateAccountBanKAccount($input:UpdateAccountBankAccountInput!) {
    updateAccountBankAccount(input: $input) {
      accountBankAccount {
        id
        number
        holder
        bic
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of accountbankaccounts """
        query = self.accountbankaccounts_query
        account_bank_account = f.AccountBankAccountFactory.create()
        variables = {
            'account': to_global_id('AccountBankAccountNode', account_bank_account.account.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['accountBankAccounts']['edges'][0]['node']['account']['id'],
            to_global_id("AccountNode", account_bank_account.account.id)
        )
        self.assertEqual(data['accountBankAccounts']['edges'][0]['node']['number'], account_bank_account.number)
        self.assertEqual(data['accountBankAccounts']['edges'][0]['node']['holder'], account_bank_account.holder)
        self.assertEqual(data['accountBankAccounts']['edges'][0]['node']['bic'], account_bank_account.bic)

    def test_query_permission_denied(self):
        """ Query list of account account_bank_account - check permission denied
        A user can query the class passes linked to their account, so an error will never be thrown
        But a user shouldn't be able to view orders from other accounts without additional permission
        """
        query = self.accountbankaccounts_query
        account_bank_account = f.AccountBankAccountFactory.create()
        variables = {
            'account': to_global_id('AccountBankAccountNode', account_bank_account.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=account_bank_account.account.id)
        other_user = f.InstructorFactory.create()
        executed = execute_test_client_api_query(query, other_user, variables=variables)
        data = executed.get('data')

        for item in data['accountBankAccounts']['edges']:
            node = item['node']
            self.assertNotEqual(node['account']['id'], to_global_id("AccountNode", user.id))

    def test_query_permission_granted(self):
        """ Query list of account accountbankaccounts with view permission """
        query = self.accountbankaccounts_query
        account_bank_account = f.AccountBankAccountFactory.create()
        variables = {
            'account': to_global_id('AccountBankAccountNode', account_bank_account.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=account_bank_account.account.id)
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all accountbankaccounts
        self.assertEqual(
            data['accountBankAccounts']['edges'][0]['node']['account']['id'],
            to_global_id("AccountNode", account_bank_account.account.id)
        )

    def test_query_anon_user(self):
        """ Query list of account accountbankaccounts - anon user """
        query = self.accountbankaccounts_query
        account_bank_account = f.AccountBankAccountFactory.create()
        variables = {
            'account': to_global_id('AccountBankAccountNode', account_bank_account.account.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_account_bank_account(self):
        """ Update a account_bank_account """
        query = self.account_bank_account_update_mutation
        account_bank_account = f.AccountBankAccountFactory.create()
        organization_account_bank_account = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateAccountBankAccount']['accountBankAccount']['number'],
          variables['input']['number']
        )
        self.assertEqual(
          data['updateAccountBankAccount']['accountBankAccount']['holder'],
          variables['input']['holder']
        )
        self.assertEqual(
          data['updateAccountBankAccount']['accountBankAccount']['bic'],
          variables['input']['bic']
        )

    def test_update_account_bank_account_number_has_to_be_iban_fail(self):
        """ Update a account_bank_account """
        from ..dudes.system_setting_dude import SystemSettingDude

        system_setting_dude = SystemSettingDude()
        system_setting_dude.set(
            setting="finance_bank_accounts_iban",
            value="true"
        )

        query = self.account_bank_account_update_mutation
        account_bank_account = f.AccountBankAccountFactory.create()
        organization_account_bank_account = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Number is not a valid IBAN!')

    def test_update_account_bank_account_number_has_to_be_iban_success(self):
        """ Update a account_bank_account """
        from ..dudes.system_setting_dude import SystemSettingDude

        system_setting_dude = SystemSettingDude()
        system_setting_dude.set(
            setting="finance_bank_accounts_iban",
            value="true"
        )

        query = self.account_bank_account_update_mutation
        account_bank_account = f.AccountBankAccountFactory.create()
        organization_account_bank_account = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)
        variables['input']['number'] = "GB33BUKB20201555555555"

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
          data['updateAccountBankAccount']['accountBankAccount']['number'],
          variables['input']['number']
        )

    def test_update_account_bank_account_anon_user(self):
        """ Don't allow updating accountbankaccounts for non-logged in users """
        query = self.account_bank_account_update_mutation
        account_bank_account = f.AccountBankAccountFactory.create()
        organization_account_bank_account = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_account_bank_account_permission_granted(self):
        """ Allow updating accountbankaccounts for users with permissions """
        query = self.account_bank_account_update_mutation
        account_bank_account = f.AccountBankAccountFactory.create()
        organization_account_bank_account = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)

        user = account_bank_account.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
          data['updateAccountBankAccount']['accountBankAccount']['number'],
          variables['input']['number']
        )

    def test_update_account_bank_account_permission_denied(self):
        """ Check update account_bank_account permission denied error message """
        query = self.account_bank_account_update_mutation
        account_bank_account = f.AccountBankAccountFactory.create()
        organization_account_bank_account = f.OrganizationClasspassFactory.create()
        instructor = f.InstructorFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)

        user = account_bank_account.account

        executed = execute_test_client_api_query(
            query,
            instructor,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_account_bank_account_allowed_own_account(self):
        """ Check update account_bank_account permission denied error message """
        query = self.account_bank_account_update_mutation
        account_bank_account = f.AccountBankAccountFactory.create()
        organization_account_bank_account = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)

        user = account_bank_account.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
          data['updateAccountBankAccount']['accountBankAccount']['number'],
          variables['input']['number']
        )
