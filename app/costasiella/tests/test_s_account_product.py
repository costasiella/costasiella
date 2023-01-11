# from graphql.error.located_error import GraphQLLocatedError
import graphql
from decimal import Decimal

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


class GQLAccountProduct(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = [
        'app_settings.json',
        'finance_invoice_group.json',
        'finance_invoice_group_defaults.json',
        'finance_payment_methods.json'
    ]

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_account = 'view_account'
        self.permission_view_organization_product = 'view_organizationproduct'
        self.permission_view = 'view_accountproduct'
        self.permission_add = 'add_accountproduct'
        self.permission_change = 'change_accountproduct'
        self.permission_delete = 'delete_accountproduct'

        self.account_product = f.AccountProductFactory.create()

        self.variables_query = {
            "account": to_global_id("accountId", self.account_product.account.id)
        }

        self.variables_create = {
            "input": {
                "account": to_global_id("AccountNode", self.account_product.account.id),
                "organizationProduct": to_global_id("OrganizationProductNode",
                                                    self.account_product.organization_product.id),
            }
        }

        # Currently no update mutations are supported, so these variables are not present in the tests either.

        self.variables_delete = {
            "input": {
                "id": to_global_id("AccountProductNode", self.account_product.id),
            }
        }

        self.account_products_query = '''
  query AccountProducts($after: String, $before: String, $account: ID!) {
    accountProducts(first: 15, before: $before, after: $after, account: $account) {
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
          organizationProduct {
            id
            name
            description
            urlImageThumbnailSmall
          }
          quantity
          createdAt
          invoiceItems {
            edges {
              node {
                financeInvoice {
                  invoiceNumber
                  id
                }
              }
            }
          }
        }
      }
    }
  }
'''

        self.account_product_create_mutation = ''' 
  mutation CreateAccountProduct($input: CreateAccountProductInput!) {
    createAccountProduct(input: $input) {
      accountProduct {
        id
        account {
          id
        }
        organizationProduct {
          id
        }
        quantity
      }
    }
  }
'''

        self.account_product_delete_mutation = '''
  mutation DeleteAccountProduct($input: DeleteAccountProductInput!) {
    deleteAccountProduct(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account account_products """
        query = self.account_products_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')
        self.assertEqual(
            data['accountProducts']['edges'][0]['node']['account']['id'],
            to_global_id("AccountNode", self.account_product.account.id)
        )
        self.assertEqual(
            data['accountProducts']['edges'][0]['node']['organizationProduct']['id'],
            to_global_id("OrganizationProductNode", self.account_product.organization_product.id)
        )
        self.assertEqual(
            data['accountProducts']['edges'][0]['node']['quantity'],
            format(1, ".2f")
        )

    def test_query_not_listed_for_other_account_without_permission(self):
        """ Query list of account account_products - check permission denied """
        query = self.account_products_query
        other_user = f.Instructor2Factory.create()

        # Create regular user
        # user = get_user_model().objects.get(pk=self.account_product.account.id)
        executed = execute_test_client_api_query(query, other_user, variables=self.variables_query)
        data = executed.get('data')
        self.assertEqual(len(data['accountProducts']['edges']), 0)

    def test_query_listed_for_other_account_with_permission(self):
        """ Query list of account account_products - check permission granted """
        query = self.account_products_query
        other_user = f.Instructor2Factory.create()

        # Create regular user
        permission = Permission.objects.get(codename=self.permission_view)
        other_user.user_permissions.add(permission)
        # View account
        permission = Permission.objects.get(codename=self.permission_view_account)
        other_user.user_permissions.add(permission)
        # View organization product
        permission = Permission.objects.get(codename=self.permission_view_organization_product)
        other_user.user_permissions.add(permission)
        other_user.save()
        executed = execute_test_client_api_query(query, other_user, variables=self.variables_query)

        data = executed.get('data')
        self.assertEqual(
            data['accountProducts']['edges'][0]['node']['account']['id'],
            to_global_id("AccountNode", self.account_product.account.id)
        )

    def test_query_list_for_own_account(self):
        """ Query list of account account_products - allow listing of products for own account """
        query = self.account_products_query
        user = self.account_product.account

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')
        self.assertEqual(
            data['accountProducts']['edges'][0]['node']['account']['id'],
            to_global_id("AccountNode", self.account_product.account.id)
        )

    def test_query_anon_user(self):
        """ Query list of account account_products - anon user """
        query = self.account_products_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    # # Query one is currently not required by the frontend, skipped writing tests for now.
    #

    def test_create_account_product(self):
        """ Create an account product """
        query = self.account_product_create_mutation

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_create
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountProduct']['accountProduct']['account']['id'],
            self.variables_create['input']['account']
        )
        self.assertEqual(
            data['createAccountProduct']['accountProduct']['organizationProduct']['id'],
            self.variables_create['input']['organizationProduct']
        )

    def test_create_account_product_anon_user(self):
        """ Don't allow creating account account_product for non-logged in users """
        query = self.account_product_create_mutation

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_account_product_permission_granted(self):
        """ Allow creating account_product for users with permissions """
        query = self.account_product_create_mutation

        # Create regular user
        user = self.account_product.account
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_create
        )
        data = executed.get('data')
        self.assertEqual(
            data['createAccountProduct']['accountProduct']['account']['id'],
            self.variables_create['input']['account']
        )

    def test_create_account_product_permission_denied(self):
        """ Check create account_product permission denied error message """
        query = self.account_product_create_mutation

        # Create regular user
        user = self.account_product.account
        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_account_product(self):
        """ Delete an account account_product """
        query = self.account_product_delete_mutation

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_delete
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountProduct']['ok'], True)

    def test_delete_account_product_anon_user(self):
        """ Delete account_product denied for anon user """
        query = self.account_product_delete_mutation

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_delete
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_account_product_permission_granted(self):
        """ Allow deleting account_product for users with permissions """
        query = self.account_product_delete_mutation

        # Give permissions
        user = self.account_product.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_delete
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountProduct']['ok'], True)

    def test_delete_account_product_permission_denied(self):
        """ Check delete account_product permission denied error message """
        query = self.account_product_delete_mutation
        user = self.account_product.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_delete
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
