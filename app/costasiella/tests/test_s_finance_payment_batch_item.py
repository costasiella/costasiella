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


class GQLFinancePaymentBatchItem(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_batch = 'view_financepaymentbatch'
        self.permission_view = 'view_financepaymentbatchitem'

        self.finance_payment_batch_item = f.FinancePaymentBatchItemFactory.create()

        self.variables_query_list = {
            "financePaymentBatch": to_global_id("FinancePaymentBatchNode",
                                                self.finance_payment_batch_item.finance_payment_batch.id)
        }

        self.finance_payment_batch_items_query = '''
  query FinancePaymentBatchItems($after: String, $before: String, $financePaymentBatch: ID!) {
    financePaymentBatchItems(first: 15, before: $before, after: $after, financePaymentBatch: $financePaymentBatch) {
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
          financeInvoice {
            id
          }
          account {
            id
          }
          accountHolder
          accountNumber
          accountBic
          mandateSignatureDate
          mandateReference
          currency
          description
        }
      }
    }
  }
'''

        self.finance_payment_batch_item_query = '''
  query FinancePaymentBatchItem($id: ID!) {
    financePaymentBatchItem(id:$id) {
      id
      financePaymentBatch {
        id
      }
      financeInvoice {
        id
      }
      account {
        id
      }
      accountHolder
      accountNumber
      accountBic
      mandateSignatureDate
      mandateReference
      currency
      description
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of finance_payment_batch items """
        query = self.finance_payment_batch_items_query
        variables = self.variables_query_list

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)

        data = executed.get('data')
        self.assertEqual(data['financePaymentBatchItems']['edges'][0]['node']['financePaymentBatch']['id'],
                         to_global_id('FinancePaymentBatchNode',
                                      self.finance_payment_batch_item.finance_payment_batch.id))
        self.assertEqual(data['financePaymentBatchItems']['edges'][0]['node']['account']['id'],
                         to_global_id('AccountNode',
                                      self.finance_payment_batch_item.account.id))
        self.assertEqual(data['financePaymentBatchItems']['edges'][0]['node']['accountHolder'],
                         self.finance_payment_batch_item.account_holder)
        self.assertEqual(data['financePaymentBatchItems']['edges'][0]['node']['accountNumber'],
                         self.finance_payment_batch_item.account_number)
        self.assertEqual(data['financePaymentBatchItems']['edges'][0]['node']['accountBic'],
                         self.finance_payment_batch_item.account_bic)
        self.assertEqual(data['financePaymentBatchItems']['edges'][0]['node']['mandateSignatureDate'],
                         str(self.finance_payment_batch_item.mandate_signature_date))
        self.assertEqual(data['financePaymentBatchItems']['edges'][0]['node']['mandateReference'],
                         self.finance_payment_batch_item.mandate_reference)
        self.assertEqual(data['financePaymentBatchItems']['edges'][0]['node']['currency'],
                         self.finance_payment_batch_item.currency)
        self.assertEqual(data['financePaymentBatchItems']['edges'][0]['node']['description'],
                         self.finance_payment_batch_item.description)

    def test_query_permission_denied(self):
        """ Query list of finance_payment_batch items - check permission denied """
        query = self.finance_payment_batch_items_query
        variables = self.variables_query_list

        # Create regular user
        user = self.finance_payment_batch_item.account
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of finance_payment_batch items with view permission """
        query = self.finance_payment_batch_items_query
        variables = self.variables_query_list

        # Create regular user
        user = self.finance_payment_batch_item.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        # Batch
        permission = Permission.objects.get(codename=self.permission_view_batch)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all finance_payment_batch items
        self.assertEqual(data['financePaymentBatchItems']['edges'][0]['node']['financePaymentBatch']['id'],
                         to_global_id('FinancePaymentBatchNode',
                                      self.finance_payment_batch_item.finance_payment_batch.id))

    def test_query_anon_user(self):
        """ Query list of finance_payment_batch items - anon user """
        query = self.finance_payment_batch_items_query
        variables = self.variables_query_list

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one finance_payment_batch_item as admin """
        node_id = to_global_id('FinancePaymentBatchItemNode', self.finance_payment_batch_item.id)

        # Now query single finance_payment_batch and check
        executed = execute_test_client_api_query(
            self.finance_payment_batch_item_query, self.admin_user, variables={"id": node_id}
        )
        data = executed.get('data')
        self.assertEqual(data['financePaymentBatchItem']['financePaymentBatch']['id'],
                         to_global_id('FinancePaymentBatchNode',
                                      self.finance_payment_batch_item.finance_payment_batch.id))
        self.assertEqual(data['financePaymentBatchItem']['account']['id'],
                         to_global_id('AccountNode',
                                      self.finance_payment_batch_item.account.id))
        self.assertEqual(data['financePaymentBatchItem']['accountHolder'],
                         self.finance_payment_batch_item.account_holder)
        self.assertEqual(data['financePaymentBatchItem']['accountNumber'],
                         self.finance_payment_batch_item.account_number)
        self.assertEqual(data['financePaymentBatchItem']['accountBic'],
                         self.finance_payment_batch_item.account_bic)
        self.assertEqual(data['financePaymentBatchItem']['mandateSignatureDate'],
                         str(self.finance_payment_batch_item.mandate_signature_date))
        self.assertEqual(data['financePaymentBatchItem']['mandateReference'],
                         self.finance_payment_batch_item.mandate_reference)
        self.assertEqual(data['financePaymentBatchItem']['currency'],
                         self.finance_payment_batch_item.currency)
        self.assertEqual(data['financePaymentBatchItem']['description'],
                         self.finance_payment_batch_item.description)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one finance payment batch """
        node_id = to_global_id('FinancePaymentBatchItemNode', self.finance_payment_batch_item.id)

        # Now query single finance_payment_batch and check
        executed = execute_test_client_api_query(
            self.finance_payment_batch_item_query, self.anon_user, variables={"id": node_id}
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        user = self.finance_payment_batch_item.account
        node_id = to_global_id('FinancePaymentBatchItemNode', self.finance_payment_batch_item.id)

        # Now query single finance_payment_batch and check
        executed = execute_test_client_api_query(self.finance_payment_batch_item_query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        user = self.finance_payment_batch_item.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        # Category
        permission = Permission.objects.get(codename=self.permission_view_batch)
        user.user_permissions.add(permission)
        user.save()
        # Payment method Cash from fixtures
        node_id = to_global_id('FinancePaymentBatchItemNode', self.finance_payment_batch_item.id)

        # Now query single location and check
        executed = execute_test_client_api_query(self.finance_payment_batch_item_query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financePaymentBatchItem']['financePaymentBatch']['id'],
                         to_global_id('FinancePaymentBatchNode',
                                      self.finance_payment_batch_item.finance_payment_batch.id))
