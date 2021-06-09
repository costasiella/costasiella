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

        self.permission_view = 'view_financepaymentbatch'

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
        """ Query list of finance_payment_batches """
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

    # def test_query_permission_denied(self):
    #     """ Query list of finance_payment_batches - check permission denied """
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     query = self.finance_payment_batches_query
    #     variables = self.variables_query_list
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     errors = executed.get('errors')
    # 
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    # 
    # def test_query_permission_granted(self):
    #     """ Query list of finance_payment_batches with view permission """
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     query = self.finance_payment_batches_query
    #     variables = self.variables_query_list
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_view)
    #     user.user_permissions.add(permission)
    #     user.save()
    # 
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')
    # 
    #     # List all finance_payment_batches
    #     self.assertEqual(data['financePaymentBatchItems']['edges'][0]['node']['name'], finance_payment_batch.name)
    # 
    # def test_query_anon_user(self):
    #     """ Query list of finance_payment_batches - anon user """
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     query = self.finance_payment_batches_query
    #     variables = self.variables_query_list
    # 
    #     executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # def test_query_one(self):
    #     """ Query one finance_payment_batch as admin """
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     node_id = to_global_id('FinancePaymentBatchNode', finance_payment_batch.id)
    # 
    #     # Now query single finance_payment_batch and check
    #     executed = execute_test_client_api_query(
    #         self.finance_payment_batch_query, self.admin_user, variables={"id": node_id}
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['financePaymentBatch']['name'], finance_payment_batch.name)
    #     self.assertEqual(data['financePaymentBatch']['batchType'],
    #                      finance_payment_batch.batch_type)
    #     self.assertEqual(data['financePaymentBatch']['status'],
    #                      finance_payment_batch.status)
    #     self.assertEqual(data['financePaymentBatch']['description'],
    #                      finance_payment_batch.description)
    #     self.assertEqual(data['financePaymentBatch']['note'],
    #                      finance_payment_batch.note)
    #     self.assertEqual(data['financePaymentBatch']['executionDate'],
    #                      str(finance_payment_batch.execution_date))
    # 
    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one finance payment batch """
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     node_id = to_global_id('FinancePaymentBatchNode', finance_payment_batch.id)
    # 
    #     # Now query single finance_payment_batch and check
    #     executed = execute_test_client_api_query(
    #         self.finance_payment_batch_query, self.anon_user, variables={"id": node_id}
    #     )
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """
    #     # Create regular user
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     user = f.RegularUserFactory.create()
    #     node_id = to_global_id('FinancePaymentBatchNode', finance_payment_batch.id)
    # 
    #     # Now query single finance_payment_batch and check
    #     executed = execute_test_client_api_query(self.finance_payment_batch_query, user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    # 
    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_view)
    #     user.user_permissions.add(permission)
    #     user.save()
    #     # Payment method Cash from fixtures
    #     node_id = to_global_id('FinancePaymentBatchNode', finance_payment_batch.id)
    # 
    #     # Now query single location and check
    #     executed = execute_test_client_api_query(self.finance_payment_batch_query, user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['financePaymentBatch']['name'], finance_payment_batch.name)
    # 
