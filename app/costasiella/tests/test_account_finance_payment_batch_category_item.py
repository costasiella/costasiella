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


class GQLAccountFinancePaymentBatchCategoryItem(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountfinancepaymentbatchcategoryitem'
        self.permission_add = 'add_accountfinancepaymentbatchcategoryitem'
        self.permission_change = 'change_accountfinancepaymentbatchcategoryitem'
        self.permission_delete = 'delete_accountfinancepaymentbatchcategoryitem'

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

        self.account_finance_payment_batch_category_items_query = '''
  query AccountFinancePaymentBatchCategoryItems($after: String, $before: String, $account: ID!) {
    accountFinancePaymentBatchCategoryItems(first: 15, before: $before, after: $after, account: $account) {
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
          financePaymentBatchCategory {
            id
            name
          }
          year
          month
          amount
          amountDisplay
          description
        }
      }
    }
  }
'''

        self.account_finance_payment_batch_category_item_query = '''
  query AccountFinancePaymentBatchCategoryItem($id: ID!) {
    accountFinancePaymentBatchCategoryItem(id: $id) {
      id
      account {
        id
      }
      financePaymentBatchCategory {
        id
        name
      }
      year
      month
      amount
      description
    }
  }
'''

        self.account_finance_payment_batch_category_item_create_mutation = ''' 
  mutation CreateAccountFinancePaymentBatchCategoryItem($input: CreateAccountFinancePaymentBatchCategoryItemInput!) {
    createAccountFinancePaymentBatchCategoryItem(input: $input) {
      accountFinancePaymentBatchCategoryItem {
        id
      }
    }
  }
'''

        self.account_finance_payment_batch_category_item_update_mutation = '''
  mutation UpdateAccountFinancePaymentBatchCategoryItem($input: UpdateAccountFinancePaymentBatchCategoryItemInput!) {
    updateAccountFinancePaymentBatchCategoryItem(input: $input) {
      accountFinancePaymentBatchCategoryItem {
        id
      }
    }
  }
'''

        self.account_finance_payment_batch_category_item_delete_mutation = '''
  mutation DeleteAccountFinancePaymentBatchCategoryItem($input: DeleteAccountFinancePaymentBatchCategoryItemInput!) {
    deleteAccountFinancePaymentBatchCategoryItem(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account bank account mandates """
        query = self.account_finance_payment_batch_category_items_query
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        variables = {
            'account': to_global_id('AccountNode', account_finance_payment_batch_category_item.account.pk),
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItems']['edges'][0]['node']['account']['id'],
            variables['account']
        )
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItems']['edges'][0]['node']['financePaymentBatchCategory']['id'],
            to_global_id("FinancePaymentBatchCategoryNode",
                         account_finance_payment_batch_category_item.finance_payment_batch_category.id)
        )
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItems']['edges'][0]['node']['year'],
            account_finance_payment_batch_category_item.year
        )
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItems']['edges'][0]['node']['month'],
            account_finance_payment_batch_category_item.month
        )
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItems']['edges'][0]['node']['amount'],
            format(account_finance_payment_batch_category_item.amount, ".2f")
        )
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItems']['edges'][0]['node']['description'],
            account_finance_payment_batch_category_item.description
        )

    def test_query_permission_denied(self):
        """ Show permission denied message when a user without permission tries to query the list  """
        query = self.account_finance_payment_batch_category_items_query
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        variables = {
            'account': to_global_id('AccountNode', account_finance_payment_batch_category_item.account.pk),
        }

        # Create regular user
        user = account_finance_payment_batch_category_item.account
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ With permissions, listing should be possible """
        query = self.account_finance_payment_batch_category_items_query
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        variables = {
            'account': to_global_id('AccountNode', account_finance_payment_batch_category_item.account.pk),
        }

        # Create regular user
        user = account_finance_payment_batch_category_item.account
        permission = Permission.objects.get(codename='view_accountfinancepaymentbatchcategoryitem')
        user.user_permissions.add(permission)
        user.save()
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItems']['edges'][0]['node']['description'],
            account_finance_payment_batch_category_item.description
        )

    def test_query_anon_user(self):
        """ Anon users shouldn't be able to view mandates """
        query = self.account_finance_payment_batch_category_items_query
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        variables = {
            'account': to_global_id('AccountNode', account_finance_payment_batch_category_item.account.pk),
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account finance payment batch category item """
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('AccountFinancePaymentBatchCategoryItemNode',
                               account_finance_payment_batch_category_item.pk)

        # Now query single item and check
        query = self.account_finance_payment_batch_category_item_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})

        data = executed.get('data')
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItem']['account']['id'],
            to_global_id("AccountNode", account_finance_payment_batch_category_item.account.id)
        )
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItem']['financePaymentBatchCategory']['id'],
            to_global_id("FinancePaymentBatchCategoryNode",
                         account_finance_payment_batch_category_item.finance_payment_batch_category.id)
        )
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItem']['year'],
            account_finance_payment_batch_category_item.year
        )
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItem']['month'],
            account_finance_payment_batch_category_item.month
        )
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItem']['amount'],
            format(account_finance_payment_batch_category_item.amount, ".2f")
        )
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItem']['description'],
            account_finance_payment_batch_category_item.description
        )

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account finance payment batch category item """
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('AccountFinancePaymentBatchCategoryItemNode',
                               account_finance_payment_batch_category_item.pk)

        # Now query single location and check
        query = self.account_finance_payment_batch_category_item_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        user = account_finance_payment_batch_category_item.account

        # First query locations to get node id easily
        node_id = to_global_id('AccountFinancePaymentBatchCategoryItemNode',
                               account_finance_payment_batch_category_item.pk)

        # Now query single location and check
        query = self.account_finance_payment_batch_category_item_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        user = f.TeacherFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('AccountFinancePaymentBatchCategoryItemNode',
                               account_finance_payment_batch_category_item.pk)

        # Now query single location and check
        query = self.account_finance_payment_batch_category_item_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(
            data['accountFinancePaymentBatchCategoryItem']['account']['id'],
            to_global_id("AccountNode", account_finance_payment_batch_category_item.account.id)
        )

    # def test_create_account_finance_payment_batch_category_item(self):
    #     """ Create a location room """
    #     query = self.account_finance_payment_batch_category_item_create_mutation
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     variables = self.variables_create
    #     variables['input']['accountBankAccount'] = to_global_id('AccountBankAccountNode', account_bank_account.pk)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #
    #     data = executed.get('data')
    #     self.assertEqual(
    #       data['createAccountBankAccountMandate']['accountBankAccountMandate']['accountBankAccount']['id'],
    #       variables['input']['accountBankAccount'])
    #
    # def test_create_account_finance_payment_batch_category_item_anon_user(self):
    #     """ Don't allow creating locations rooms for non-logged in users """
    #     query = self.account_finance_payment_batch_category_item_create_mutation
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     variables = self.variables_create
    #     variables['input']['accountBankAccount'] = to_global_id('AccountBankAccountNode', account_bank_account.pk)
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
    # def test_create_account_finance_payment_batch_category_item_permission_granted(self):
    #     """ Allow creating location rooms for users with permissions """
    #     query = self.account_finance_payment_batch_category_item_create_mutation
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     variables = self.variables_create
    #     variables['input']['accountBankAccount'] = to_global_id('AccountBankAccountNode', account_bank_account.pk)
    #
    #     # Create regular user
    #     user = account_bank_account.account
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
    #       data['createAccountBankAccountMandate']['accountBankAccountMandate']['accountBankAccount']['id'],
    #       variables['input']['accountBankAccount'])
    #
    # def test_create_account_finance_payment_batch_category_item_permission_denied(self):
    #     """ Check create location room permission denied error message """
    #     query = self.account_finance_payment_batch_category_item_create_mutation
    #     account_bank_account = f.AccountBankAccountFactory.create()
    #     variables = self.variables_create
    #     variables['input']['accountBankAccount'] = to_global_id('AccountBankAccountNode', account_bank_account.pk)
    #
    #     # Create regular user
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
    # def test_update_account_finance_payment_batch_category_item(self):
    #     """ Update a bank account mandate """
    #     query = self.account_finance_payment_batch_category_item_update_mutation
    #     account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode", account_finance_payment_batch_category_item.pk)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #
    #     data = executed.get('data')
    #     self.assertEqual(
    #       data['updateAccountBankAccountMandate']['accountBankAccountMandate']['reference'],
    #       variables['input']['reference'])
    #     self.assertEqual(
    #       data['updateAccountBankAccountMandate']['accountBankAccountMandate']['content'],
    #       variables['input']['content'])
    #     self.assertEqual(
    #       data['updateAccountBankAccountMandate']['accountBankAccountMandate']['signatureDate'],
    #       variables['input']['signatureDate'])
    #
    # def test_update_account_finance_payment_batch_category_item_anon_user(self):
    #     """ Don't allow updating bank account mandates for non-logged in users """
    #     query = self.account_finance_payment_batch_category_item_update_mutation
    #     account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode", account_finance_payment_batch_category_item.pk)
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
    # def test_update_account_finance_payment_batch_category_item_permission_granted(self):
    #     """ Allow updating bank account mandate for users with permissions """
    #     query = self.account_finance_payment_batch_category_item_update_mutation
    #     account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode", account_finance_payment_batch_category_item.pk)
    #
    #     # Create regular user
    #     user = account_finance_payment_batch_category_item.account_bank_account.account
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
    #     self.assertEqual(
    #       data['updateAccountBankAccountMandate']['accountBankAccountMandate']['reference'],
    #       variables['input']['reference'])
    #
    # def test_update_account_finance_payment_batch_category_item_permission_denied(self):
    #     """ Check update bank account mandate permission denied error message """
    #     query = self.account_finance_payment_batch_category_item_update_mutation
    #     account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode", account_finance_payment_batch_category_item.pk)
    #
    #     # Create regular user
    #     user = account_finance_payment_batch_category_item.account_bank_account.account
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
    # def test_delete_account_finance_payment_batch_category_item(self):
    #     """ Archive a account bank account mandate"""
    #     query = self.account_finance_payment_batch_category_item_archive_mutation
    #     account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
    #     variables = self.variables_delete
    #     variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode", account_finance_payment_batch_category_item.pk)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['deleteAccountBankAccountMandate']['ok'], True)
    #
    # def test_delete_account_finance_payment_batch_category_item_anon_user(self):
    #     """ Anon users shouldn't be able to delete a account bank account mandate """
    #     query = self.account_finance_payment_batch_category_item_archive_mutation
    #     account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
    #     variables = self.variables_delete
    #     variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode", account_finance_payment_batch_category_item.pk)
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
    # def test_delete_account_finance_payment_batch_category_item_permission_granted(self):
    #     """ Allow deleting bank account mandates for users with permissions """
    #     query = self.account_finance_payment_batch_category_item_archive_mutation
    #     account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
    #     variables = self.variables_delete
    #     variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode", account_finance_payment_batch_category_item.pk)
    #
    #     # Create regular user
    #     user = f.TeacherFactory.create()
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
    #     self.assertEqual(data['deleteAccountBankAccountMandate']['ok'], True)
    #
    # def test_delete_account_finance_payment_batch_category_item_permission_denied(self):
    #     """ Check delete mandate permission denied error message """
    #     query = self.account_finance_payment_batch_category_item_archive_mutation
    #     account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
    #     variables = self.variables_delete
    #     variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode", account_finance_payment_batch_category_item.pk)
    #
    #     # Create regular user
    #     user = f.TeacherFactory.create()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
