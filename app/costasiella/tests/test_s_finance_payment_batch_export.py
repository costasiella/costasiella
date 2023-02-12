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


class GQLFinancePaymentBatchExport(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_batch = 'view_financepaymentbatch'
        self.permission_view = 'view_financepaymentbatchexport'

        self.finance_payment_batch_export = f.FinancePaymentBatchExportFactory.create()

        self.variables_query_list = {
            "financePaymentBatch": to_global_id("FinancePaymentBatchNode",
                                                self.finance_payment_batch_export.finance_payment_batch.id)
        }

        self.finance_payment_batch_exports_query = '''
  query FinancePaymentBatchExports($after: String, $before: String, $financePaymentBatch: ID!) {
    financePaymentBatchExports(first: 15, before: $before, after: $after, financePaymentBatch: $financePaymentBatch) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          financePaymentBatch {
            id
          }
          account {
            id
          }
        }
      }
    }
  }
'''

        self.finance_payment_batch_export_query = '''
  query FinancePaymentBatchExport($id: ID!) {
    financePaymentBatchExport(id:$id) {
      id
      financePaymentBatch {
        id
      }
      account {
        id
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of finance_payment_batch exports """
        query = self.finance_payment_batch_exports_query
        variables = self.variables_query_list

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)

        data = executed.get('data')
        self.assertEqual(data['financePaymentBatchExports']['edges'][0]['node']['financePaymentBatch']['id'],
                         to_global_id('FinancePaymentBatchNode',
                                      self.finance_payment_batch_export.finance_payment_batch.id))
        self.assertEqual(data['financePaymentBatchExports']['edges'][0]['node']['account']['id'],
                         to_global_id('AccountNode',
                                      self.finance_payment_batch_export.account.id))

    def test_query_permission_denied(self):
        """ Query list of finance_payment_batch exports - check permission denied """
        query = self.finance_payment_batch_exports_query
        variables = self.variables_query_list

        # Create regular user
        user = self.finance_payment_batch_export.account
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of finance_payment_batch exports with view permission """
        query = self.finance_payment_batch_exports_query
        variables = self.variables_query_list

        # Create regular user
        user = self.finance_payment_batch_export.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        # Batch
        permission = Permission.objects.get(codename=self.permission_view_batch)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all finance_payment_batch exports
        self.assertEqual(data['financePaymentBatchExports']['edges'][0]['node']['financePaymentBatch']['id'],
                         to_global_id('FinancePaymentBatchNode',
                                      self.finance_payment_batch_export.finance_payment_batch.id))

    def test_query_anon_user(self):
        """ Query list of finance_payment_batch exports - anon user """
        query = self.finance_payment_batch_exports_query
        variables = self.variables_query_list

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one finance_payment_batch_export as admin """
        node_id = to_global_id('FinancePaymentBatchExportNode', self.finance_payment_batch_export.id)

        # Now query single finance_payment_batch and check
        executed = execute_test_client_api_query(
            self.finance_payment_batch_export_query, self.admin_user, variables={"id": node_id}
        )
        data = executed.get('data')
        self.assertEqual(data['financePaymentBatchExport']['financePaymentBatch']['id'],
                         to_global_id('FinancePaymentBatchNode',
                                      self.finance_payment_batch_export.finance_payment_batch.id))
        self.assertEqual(data['financePaymentBatchExport']['account']['id'],
                         to_global_id('AccountNode',
                                      self.finance_payment_batch_export.account.id))

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one finance payment batch """
        node_id = to_global_id('FinancePaymentBatchExportNode', self.finance_payment_batch_export.id)

        # Now query single finance_payment_batch and check
        executed = execute_test_client_api_query(
            self.finance_payment_batch_export_query, self.anon_user, variables={"id": node_id}
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        user = self.finance_payment_batch_export.account
        node_id = to_global_id('FinancePaymentBatchExportNode', self.finance_payment_batch_export.id)

        # Now query single finance_payment_batch and check
        executed = execute_test_client_api_query(self.finance_payment_batch_export_query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        user = self.finance_payment_batch_export.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        # Batch
        permission = Permission.objects.get(codename=self.permission_view_batch)
        user.user_permissions.add(permission)
        user.save()
        # Payment method Cash from fixtures
        node_id = to_global_id('FinancePaymentBatchExportNode', self.finance_payment_batch_export.id)

        # Now query single location and check
        executed = execute_test_client_api_query(self.finance_payment_batch_export_query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financePaymentBatchExport']['financePaymentBatch']['id'],
                         to_global_id('FinancePaymentBatchNode',
                                      self.finance_payment_batch_export.finance_payment_batch.id))
