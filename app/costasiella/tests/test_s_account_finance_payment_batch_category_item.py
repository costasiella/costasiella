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

        self.permission_view_account = 'view_account'
        self.permission_view_category = 'view_financepaymentbatchcategory'
        self.permission_view = 'view_accountfinancepaymentbatchcategoryitem'
        self.permission_add = 'add_accountfinancepaymentbatchcategoryitem'
        self.permission_change = 'change_accountfinancepaymentbatchcategoryitem'
        self.permission_delete = 'delete_accountfinancepaymentbatchcategoryitem'

        self.variables_create = {
            "input": {
                "year": 2020,
                "month": 1,
                "amount": "20",
                "description": "test description"
            }
        }

        self.variables_update = {
            "input": {
                "year": 2023,
                "month": 1,
                "amount": "20",
                "description": "test description"
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
  }
'''

        self.account_finance_payment_batch_category_item_update_mutation = '''
  mutation UpdateAccountFinancePaymentBatchCategoryItem($input: UpdateAccountFinancePaymentBatchCategoryItemInput!) {
    updateAccountFinancePaymentBatchCategoryItem(input: $input) {
      accountFinancePaymentBatchCategoryItem {
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
        user = f.InstructorFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        # View category
        permission = Permission.objects.get(codename=self.permission_view_account)
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

    def test_create_account_finance_payment_batch_category_item(self):
        """ Create a account finance payment batch category item  """
        query = self.account_finance_payment_batch_category_item_create_mutation
        account = f.RegularUserFactory.create()
        finance_payment_batch_category = f.FinancePaymentBatchCategoryCollectionFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id("AccountNode", account.id)
        variables['input']['financePaymentBatchCategory'] = to_global_id('FinancePaymentBatchCategoryNode',
                                                                         finance_payment_batch_category.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        item = data['createAccountFinancePaymentBatchCategoryItem']['accountFinancePaymentBatchCategoryItem']
        self.assertEqual(
          item['financePaymentBatchCategory']['id'], variables['input']['financePaymentBatchCategory']
        )
        self.assertEqual(
          item['account']['id'], variables['input']['account']
        )
        self.assertEqual(item['year'], variables['input']['year'])
        self.assertEqual(item['month'], variables['input']['month'])
        self.assertEqual(item['description'], variables['input']['description'])
        self.assertEqual(item['amount'], str(variables['input']['amount']))

    def test_create_account_finance_payment_batch_category_item_anon_user(self):
        """ Don't allow creating account finance payment batch items for non-logged in users """
        query = self.account_finance_payment_batch_category_item_create_mutation
        account = f.RegularUserFactory.create()
        finance_payment_batch_category = f.FinancePaymentBatchCategoryCollectionFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id("AccountNode", account.id)
        variables['input']['financePaymentBatchCategory'] = to_global_id('FinancePaymentBatchCategoryNode',
                                                                         finance_payment_batch_category.pk)
        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_account_finance_payment_batch_category_item_permission_granted(self):
        """ Allow creating account finance payment batch category items for users with permissions """
        query = self.account_finance_payment_batch_category_item_create_mutation
        account = f.RegularUserFactory.create()
        finance_payment_batch_category = f.FinancePaymentBatchCategoryCollectionFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id("AccountNode", account.id)
        variables['input']['financePaymentBatchCategory'] = to_global_id('FinancePaymentBatchCategoryNode',
                                                                         finance_payment_batch_category.pk)

        # Create regular user
        user = account
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        # View category
        permission = Permission.objects.get(codename=self.permission_view_category)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        item = data['createAccountFinancePaymentBatchCategoryItem']['accountFinancePaymentBatchCategoryItem']
        self.assertEqual(
          item['financePaymentBatchCategory']['id'], variables['input']['financePaymentBatchCategory']
        )

    def test_create_account_finance_payment_batch_category_item_permission_denied(self):
        """ Check create location room permission denied error message """
        query = self.account_finance_payment_batch_category_item_create_mutation
        account = f.RegularUserFactory.create()
        finance_payment_batch_category = f.FinancePaymentBatchCategoryCollectionFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id("AccountNode", account.id)
        variables['input']['financePaymentBatchCategory'] = to_global_id('FinancePaymentBatchCategoryNode',
                                                                         finance_payment_batch_category.pk)
        # Create regular user
        user = account
        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_account_finance_payment_batch_category_item(self):
        """ Update an account finance payment batch category item """
        query = self.account_finance_payment_batch_category_item_update_mutation
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode",
                                                account_finance_payment_batch_category_item.pk)
        variables['input']['financePaymentBatchCategory'] = to_global_id(
            "FinancePaymentBatchCategoryNode",
            account_finance_payment_batch_category_item.finance_payment_batch_category.id
        )

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        item = data['updateAccountFinancePaymentBatchCategoryItem']['accountFinancePaymentBatchCategoryItem']
        self.assertEqual(
          item['financePaymentBatchCategory']['id'], variables['input']['financePaymentBatchCategory']
        )
        self.assertEqual(item['year'], variables['input']['year'])
        self.assertEqual(item['month'], variables['input']['month'])
        self.assertEqual(item['description'], variables['input']['description'])
        self.assertEqual(item['amount'], str(variables['input']['amount']))

    def test_update_account_finance_payment_batch_category_item_anon_user(self):
        """ Don't allow updating account finance payment batch category items for non-logged in users """
        query = self.account_finance_payment_batch_category_item_update_mutation
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode",
                                                account_finance_payment_batch_category_item.pk)
        variables['input']['financePaymentBatchCategory'] = to_global_id(
            "FinancePaymentBatchCategoryNode",
            account_finance_payment_batch_category_item.finance_payment_batch_category.id
        )

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_account_finance_payment_batch_category_item_permission_granted(self):
        """ Allow updating account finance payment batch category items for users with permissions """
        query = self.account_finance_payment_batch_category_item_update_mutation
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode",
                                                account_finance_payment_batch_category_item.pk)
        variables['input']['financePaymentBatchCategory'] = to_global_id(
            "FinancePaymentBatchCategoryNode",
            account_finance_payment_batch_category_item.finance_payment_batch_category.id
        )

        # Create regular user
        user = account_finance_payment_batch_category_item.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        # View category
        permission = Permission.objects.get(codename=self.permission_view_category)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        item = data['updateAccountFinancePaymentBatchCategoryItem']['accountFinancePaymentBatchCategoryItem']
        self.assertEqual(
          item['financePaymentBatchCategory']['id'], variables['input']['financePaymentBatchCategory']
        )

    def test_update_account_finance_payment_batch_category_item_permission_denied(self):
        """ Check update account finance payment batch category item permission denied error message """
        query = self.account_finance_payment_batch_category_item_update_mutation
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode",
                                                account_finance_payment_batch_category_item.pk)
        variables['input']['financePaymentBatchCategory'] = to_global_id(
            "FinancePaymentBatchCategoryNode",
            account_finance_payment_batch_category_item.finance_payment_batch_category.id
        )

        # Create regular user
        user = account_finance_payment_batch_category_item.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_account_finance_payment_batch_category_item(self):
        """ Delete an account finance payment batch category item """
        query = self.account_finance_payment_batch_category_item_delete_mutation
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode",
                                                account_finance_payment_batch_category_item.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountFinancePaymentBatchCategoryItem']['ok'], True)

    def test_delete_account_finance_payment_batch_category_item_anon_user(self):
        """ Anon users shouldn't be able to delete an account finance payment batch category item """
        query = self.account_finance_payment_batch_category_item_delete_mutation
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode",
                                                account_finance_payment_batch_category_item.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_account_finance_payment_batch_category_item_permission_granted(self):
        """ Allow deleting account finance payment batch category items for users with permissions """
        query = self.account_finance_payment_batch_category_item_delete_mutation
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode",
                                                account_finance_payment_batch_category_item.pk)

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
        self.assertEqual(data['deleteAccountFinancePaymentBatchCategoryItem']['ok'], True)

    def test_delete_account_finance_payment_batch_category_item_permission_denied(self):
        """ Check delete mandate permission denied error message """
        query = self.account_finance_payment_batch_category_item_delete_mutation
        account_finance_payment_batch_category_item = f.AccountFinancePaymentBatchCategoryItemFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("AccountFinancePaymentBatchCategoryItemNode",
                                                account_finance_payment_batch_category_item.pk)

        # Create regular user
        user = f.InstructorFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
