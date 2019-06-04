import graphene
import os
from django.test import TransactionTestCase
from graphene.test import Client
from django.contrib.auth.models import AnonymousUser, Permission
from django.contrib.auth import get_user_model

# Create your tests here.
from graphql_relay import to_global_id
from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema

from .factories import AdminUserFactory


class GQLAccount(TransactionTestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_account'
        self.permission_add = 'add_account'
        self.permission_change = 'change_account'
        self.permission_delete = 'delete_account'

        self.variables_query_list = {
            "isActive": True
        }

        self.variables_create = {
            "input": {
                "name": "New account",
                "code" : "8000"
            }
        }

        self.variables_update = {
            "input": {
                "name": "Updated account",
                "code" : "9000"
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.accounts_query = '''
  query Accounts($after: String, $before: String, $isActive: Boolean!) {
    accounts(first: 15, before: $before, after: $after, isActive: $isActive) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          firstName
          lastName
          email
          isActive
        }
      }
    }
  }
'''

        self.account_query = '''
  query Account($id: ID!) {
    account(id:$id) {
      id
      firstName
      lastName
      email
      isActive
    }
  }
'''

#         self.account_create_mutation = ''' 
#   mutation CreateFinanceCostCenter($input:CreateFinanceCostCenterInput!) {
#     createFinanceCostcenter(input: $input) {
#       financeCostcenter{
#         id
#         archived
#         name
#         code
#       }
#     }
#   }
# '''

#         self.account_update_mutation = '''
#   mutation UpdateFinanceCostCenter($input: UpdateFinanceCostCenterInput!) {
#     updateFinanceCostcenter(input: $input) {
#       financeCostcenter {
#         id
#         name
#         code
#       }
#     }
#   }
# '''

#         self.account_archive_mutation = '''
#   mutation ArchiveFinanceCostCenter($input: ArchiveFinanceCostCenterInput!) {
#     archiveFinanceCostcenter(input: $input) {
#       financeCostcenter {
#         id
#         archived
#       }
#     }
#   }
# '''

    def tearDown(self):
        # This is run after every test
        # pass
        # Clean up accounts in costasiella_account table
        get_user_model().objects.all().delete()


    def test_query(self):
        """ Query list of accounts """
        query = self.accounts_query
        account = f.RegularUserFactory()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(len(data['accounts']['edges']), 1) # Ensure the Admin super use isn't listed
        self.assertEqual(data['accounts']['edges'][0]['node']['isActive'], account.is_active)
        self.assertEqual(data['accounts']['edges'][0]['node']['firstName'], account.first_name)
        self.assertEqual(data['accounts']['edges'][0]['node']['lastName'], account.last_name)
        self.assertEqual(data['accounts']['edges'][0]['node']['email'], account.email)


    def test_query_permision_denied(self):
        """ Query list of accounts - check permission denied """
        query = self.accounts_query
        account = f.RegularUserFactory()
        
        # User created account
        executed = execute_test_client_api_query(query, account, variables=self.variables_query_list)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permision_granted(self):
        """ Query list of accounts with view permission """
        query = self.accounts_query
        account = f.RegularUserFactory.create()

        # Create regular user
        permission = Permission.objects.get(codename='view_account')
        account.user_permissions.add(permission)
        account.save()

        executed = execute_test_client_api_query(query, account, variables=self.variables_query_list)
        data = executed.get('data')

        # List all accounts
        self.assertEqual(data['accounts']['edges'][0]['node']['isActive'], account.is_active)
        self.assertEqual(data['accounts']['edges'][0]['node']['firstName'], account.first_name)
        self.assertEqual(data['accounts']['edges'][0]['node']['lastName'], account.last_name)
        self.assertEqual(data['accounts']['edges'][0]['node']['email'], account.email)


    def test_query_anon_user(self):
        """ Query list of accounts - anon user """
        query = self.accounts_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one account as admin """   
        account = f.RegularUserFactory.create()
        node_id = to_global_id('AccountNode', account.pk)

        # Now query single account and check
        executed = execute_test_client_api_query(self.account_query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['account']['firstName'], account.first_name)
        self.assertEqual(data['account']['lastName'], account.last_name)
        self.assertEqual(data['account']['email'], account.email)
        self.assertEqual(data['account']['isActive'], account.is_active)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one glacount """   
        account = f.RegularUserFactory.create()
        node_id = to_global_id('AccountNode', account.pk)

        # Now query single account and check
        executed = execute_test_client_api_query(self.account_query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        account = f.RegularUserFactory.create()
        node_id = to_global_id('AccountNode', account.pk)

        # Now query single account and check
        executed = execute_test_client_api_query(self.account_query, account, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_account')
    #     user.user_permissions.add(permission)
    #     user.save()
    #     account = f.RegularUserFactory.create()

    #     # First query accounts to get node id easily
    #     node_id = self.get_node_id_of_first_account()

    #     # Now query single location and check   
    #     executed = execute_test_client_api_query(self.account_query, user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['financeCostcenter']['name'], account.name)


    # def test_create_account(self):
    #     """ Create a account """
    #     query = self.account_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['name'], variables['input']['name'])
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['archived'], False)
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['code'], variables['input']['code'])


    # def test_create_account_anon_user(self):
    #     """ Don't allow creating accounts for non-logged in users """
    #     query = self.account_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_create_location_permission_granted(self):
    #     """ Allow creating accounts for users with permissions """
    #     query = self.account_create_mutation
    #     variables = self.variables_create

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['name'], variables['input']['name'])
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['archived'], False)
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['code'], variables['input']['code'])


    # def test_create_account_permission_denied(self):
    #     """ Check create account permission denied error message """
    #     query = self.account_create_mutation
    #     variables = self.variables_create

    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_update_account(self):
    #     """ Update a account """
    #     query = self.account_update_mutation
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_account()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateFinanceCostcenter']['financeCostcenter']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateFinanceCostcenter']['financeCostcenter']['code'], variables['input']['code'])


    # def test_update_account_anon_user(self):
    #     """ Don't allow updating accounts for non-logged in users """
    #     query = self.account_update_mutation
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_account()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_account_permission_granted(self):
    #     """ Allow updating accounts for users with permissions """
    #     query = self.account_update_mutation
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_account()

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateFinanceCostcenter']['financeCostcenter']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateFinanceCostcenter']['financeCostcenter']['code'], variables['input']['code'])


    # def test_update_account_permission_denied(self):
    #     """ Check update account permission denied error message """
    #     query = self.account_update_mutation
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_account()

    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_archive_account(self):
    #     """ Archive a account """
    #     query = self.account_archive_mutation
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_account()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     print(data)
    #     self.assertEqual(data['archiveFinanceCostcenter']['financeCostcenter']['archived'], variables['input']['archived'])


    # def test_archive_account_anon_user(self):
    #     """ Archive account denied for anon user """
    #     query = self.account_archive_mutation
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_account()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_archive_account_permission_granted(self):
    #     """ Allow archiving accounts for users with permissions """
    #     query = self.account_archive_mutation
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_account()

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveFinanceCostcenter']['financeCostcenter']['archived'], variables['input']['archived'])


    # def test_archive_account_permission_denied(self):
    #     """ Check archive account permission denied error message """
    #     query = self.account_archive_mutation
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_account()
        
    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')

