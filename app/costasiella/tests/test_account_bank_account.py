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

        self.permission_view = 'view_accountaccountbankaccount'
        self.permission_add = 'add_accountaccountbankaccount'
        self.permission_change = 'change_accountaccountbankaccount'
        self.permission_delete = 'delete_accountaccountbankaccount'

        self.variables_create = {
            "input": {
                "dateStart": "2019-01-01",
                "note": "creation note",
            }
        }

        self.variables_update = {
            "input": {
                "dateStart": "2017-01-01",
                "dateEnd": "2020-12-31",
                "note": "Update note",
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
        other_user = f.TeacherFactory.create()
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
        permission = Permission.objects.get(codename='view_accountbankaccount')
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

    # 
    # def test_query_one(self):
    #     """ Query one account account_bank_account as admin """   
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     
    #     variables = {
    #         "id": to_global_id("AccountBankAccountNode", account_bank_account.id),
    #         "archived": False,
    #     }
    # 
    #     # Now query single account_bank_account and check
    #     executed = execute_test_client_api_query(self.account_bank_account_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['accountClasspass']['account']['id'], 
    #         to_global_id('AccountNode', account_bank_account.account.id)
    #     )
    #     self.assertEqual(
    #         data['accountClasspass']['organizationClasspass']['id'], 
    #         to_global_id('OrganizationClasspassNode', account_bank_account.organization_account_bank_account.id)
    #     )
    #     self.assertEqual(data['accountClasspass']['dateStart'], str(account_bank_account.date_start))
    #     self.assertEqual(data['accountClasspass']['dateEnd'], str(account_bank_account.date_end))
    #     self.assertEqual(data['accountClasspass']['note'], account_bank_account.note)
    # 
    # 
    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one account account_bank_account """   
    #     account_bank_account = f.AccountBankAccountFactory.create()
    # 
    #     variables = {
    #         "id": to_global_id("AccountBankAccountNode", account_bank_account.id),
    #         "archived": False,
    #     }
    # 
    #     # Now query single account_bank_account and check
    #     executed = execute_test_client_api_query(self.account_bank_account_query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # 
    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     user = account_bank_account.account
    # 
    #     variables = {
    #         "id": to_global_id("AccountBankAccountNode", account_bank_account.id),
    #         "archived": False,
    #     }
    # 
    #     # Now query single account_bank_account and check
    #     executed = execute_test_client_api_query(self.account_bank_account_query, user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    # 
    # 
    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     user = account_bank_account.account
    #     permission = Permission.objects.get(codename='view_accountaccount_bank_account')
    #     user.user_permissions.add(permission)
    #     user.save()
    #     
    # 
    #     variables = {
    #         "id": to_global_id("AccountBankAccountNode", account_bank_account.id),
    #         "archived": False,
    #     }
    # 
    #     # Now query single account_bank_account and check   
    #     executed = execute_test_client_api_query(self.account_bank_account_query, user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['accountClasspass']['organizationClasspass']['id'], 
    #         to_global_id('OrganizationClasspassNode', account_bank_account.organization_account_bank_account.id)
    #     )
    # 
    # 
    # def test_create_account_bank_account(self):
    #     """ Create an account account_bank_account """
    #     query = self.account_bank_account_create_mutation
    # 
    #     account = f.RegularUserFactory.create()
    #     organization_account_bank_account = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_account_bank_account.id)
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    # 
    #     self.assertEqual(
    #         data['createAccountClasspass']['accountClasspass']['account']['id'], 
    #         variables['input']['account']
    #     )
    #     self.assertEqual(
    #         data['createAccountClasspass']['accountClasspass']['organizationClasspass']['id'], 
    #         variables['input']['organizationClasspass']
    #     )
    #     self.assertEqual(data['createAccountClasspass']['accountClasspass']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['createAccountClasspass']['accountClasspass']['note'], variables['input']['note'])
    # 
    # 
    # def test_create_account_bank_account_valid_3_days(self):
    #     """ End date should be set 3 days from start """
    #     query = self.account_bank_account_create_mutation
    # 
    #     account = f.RegularUserFactory.create()
    #     organization_account_bank_account = f.OrganizationClasspassFactory.create()
    #     organization_account_bank_account.validity_unit = 'DAYS'
    #     organization_account_bank_account.validity = 3
    #     organization_account_bank_account.save()
    # 
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_account_bank_account.id)
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    # 
    #     self.assertEqual(
    #         data['createAccountClasspass']['accountClasspass']['dateEnd'], 
    #         str(datetime.date(2019, 1, 1) + datetime.timedelta(days=2))
    #     )
    # 
    # 
    # def test_create_account_bank_account_valid_2_weeks(self):
    #     """ End date should be set 2 weeks from start """
    #     query = self.account_bank_account_create_mutation
    # 
    #     account = f.RegularUserFactory.create()
    #     organization_account_bank_account = f.OrganizationClasspassFactory.create()
    #     organization_account_bank_account.validity_unit = 'WEEKS'
    #     organization_account_bank_account.validity = 2
    #     organization_account_bank_account.save()
    # 
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_account_bank_account.id)
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    # 
    #     self.assertEqual(
    #         data['createAccountClasspass']['accountClasspass']['dateEnd'], 
    #         str(datetime.date(2019, 1, 1) + datetime.timedelta(days=13))
    #     )
    # 
    # 
    # def test_create_account_bank_account_valid_2_months(self):
    #     """ End date should be set 2 weeks from start """
    #     query = self.account_bank_account_create_mutation
    # 
    #     account = f.RegularUserFactory.create()
    #     organization_account_bank_account = f.OrganizationClasspassFactory.create()
    #     organization_account_bank_account.validity_unit = 'MONTHS'
    #     organization_account_bank_account.validity = 2
    #     organization_account_bank_account.save()
    # 
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_account_bank_account.id)
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    # 
    #     self.assertEqual(
    #         data['createAccountClasspass']['accountClasspass']['dateEnd'], 
    #         str(datetime.date(2019, 2, 28))
    #     )
    # 
    # 
    # def test_create_account_bank_account_anon_user(self):
    #     """ Don't allow creating account accountbankaccounts for non-logged in users """
    #     query = self.account_bank_account_create_mutation
    #     
    #     account = f.RegularUserFactory.create()
    #     organization_account_bank_account = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_account_bank_account.id)
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # 
    # def test_create_account_bank_account_permission_granted(self):
    #     """ Allow creating accountbankaccounts for users with permissions """
    #     query = self.account_bank_account_create_mutation
    # 
    #     account = f.RegularUserFactory.create()
    #     organization_account_bank_account = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_account_bank_account.id)
    # 
    #     # Create regular user
    #     user = account
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['createAccountClasspass']['accountClasspass']['organizationClasspass']['id'], 
    #         variables['input']['organizationClasspass']
    #     )
    # 
    # 
    # def test_create_account_bank_account_permission_denied(self):
    #     """ Check create account_bank_account permission denied error message """
    #     query = self.account_bank_account_create_mutation
    #     account = f.RegularUserFactory.create()
    #     organization_account_bank_account = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_account_bank_account.id)
    # 
    #     # Create regular user
    #     user = account
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    # 
    # 
    # def test_update_account_bank_account(self):
    #     """ Update a account_bank_account """
    #     query = self.account_bank_account_update_mutation
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     organization_account_bank_account = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)
    #     variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_account_bank_account.id)
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    # 
    #     self.assertEqual(
    #       data['updateAccountClasspass']['accountClasspass']['organizationClasspass']['id'], 
    #       variables['input']['organizationClasspass']
    #     )
    #     self.assertEqual(data['updateAccountClasspass']['accountClasspass']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['updateAccountClasspass']['accountClasspass']['dateEnd'], variables['input']['dateEnd'])
    #     self.assertEqual(data['updateAccountClasspass']['accountClasspass']['note'], variables['input']['note'])
    # 
    # 
    # def test_update_account_bank_account_anon_user(self):
    #     """ Don't allow updating accountbankaccounts for non-logged in users """
    #     query = self.account_bank_account_update_mutation
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     organization_account_bank_account = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)
    #     variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_account_bank_account.id)
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # 
    # def test_update_account_bank_account_permission_granted(self):
    #     """ Allow updating accountbankaccounts for users with permissions """
    #     query = self.account_bank_account_update_mutation
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     organization_account_bank_account = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)
    #     variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_account_bank_account.id)
    # 
    #     user = account_bank_account.account
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateAccountClasspass']['accountClasspass']['dateStart'], variables['input']['dateStart'])
    # 
    # 
    # def test_update_account_bank_account_permission_denied(self):
    #     """ Check update account_bank_account permission denied error message """
    #     query = self.account_bank_account_update_mutation
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     organization_account_bank_account = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)
    #     variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_account_bank_account.id)
    # 
    #     user = account_bank_account.account
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    # 
    # 
    # def test_delete_account_bank_account(self):
    #     """ Delete an account account_bank_account """
    #     query = self.account_bank_account_delete_mutation
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     print(data)
    #     self.assertEqual(data['deleteAccountClasspass']['ok'], True)
    # 
    # 
    # def test_delete_account_bank_account_anon_user(self):
    #     """ Delete account_bank_account denied for anon user """
    #     query = self.account_bank_account_delete_mutation
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # 
    # def test_delete_account_bank_account_permission_granted(self):
    #     """ Allow deleting accountbankaccounts for users with permissions """
    #     query = self.account_bank_account_delete_mutation
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)
    # 
    #     # Give permissions
    #     user = account_bank_account.account
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['deleteAccountClasspass']['ok'], True)
    # 
    # 
    # def test_delete_account_bank_account_permission_denied(self):
    #     """ Check delete account_bank_account permission denied error message """
    #     query = self.account_bank_account_delete_mutation
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountBankAccountNode', account_bank_account.id)
    #     
    #     user = account_bank_account.account
    # 
    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    # 
