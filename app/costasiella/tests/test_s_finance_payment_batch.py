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


class GQLFinancePaymentBatch(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financepaymentbatch'
        self.permission_add = 'add_financepaymentbatch'
        self.permission_change = 'change_financepaymentbatch'
        self.permission_delete = 'delete_financepaymentbatch'

        self.variables_query_list = {
            "batchType": "COLLECTION"
        }

        self.variables_create = {
            "input": {
                "name": "New finance_payment_batch",
                "batchType": "COLLECTION",
                "description": "hello",
                "executionDate": "2020-01-01",
                "note": "Note here"
            }
        }

        self.variables_update = {
            "input": {
                "name": "Updated finance_payment_batch",
                "note": "Note here",
                "status": 'APPROVED'
            }
        }

        self.variables_delete = {
            "input": {}
        }

        self.finance_payment_batches_query = '''
  query FinancePaymentBatches($after: String, $before: String, $batchType: CostasiellaFinancePaymentBatchBatchTypeChoices!) {
    financePaymentBatches(first: 15, before: $before, after: $after, batchType: $batchType) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          name
          status
          financePaymentBatchCategory {
            id
            name
          }
          description
          batchType
          year
          month
          includeZeroAmounts
          executionDate
          note
        }
      }
    }
  }
'''

        self.finance_payment_batch_query = '''
  query FinancePaymentBatch($id: ID!) {
    financePaymentBatch(id:$id) {
      id
      name
      status
      executionDate
      financePaymentBatchCategory {
        id
        name
      }
      description
      batchType
      year
      month
      includeZeroAmounts
      note
      totalDisplay
      countItems     
    }
  }
'''

        self.finance_payment_batch_create_mutation = ''' 
  mutation CreateFinancePaymentBatch($input:CreateFinancePaymentBatchInput!) {
    createFinancePaymentBatch(input: $input) {
      financePaymentBatch {
        id
        name
        status
        executionDate
        financePaymentBatchCategory {
          id
          name
        }
        description
        batchType
        year
        month
        includeZeroAmounts
        note
        totalDisplay
        countItems
      }
    }
  }
'''

        self.finance_payment_batch_update_mutation = '''
  mutation UpdateFinancePaymentBatch($input:UpdateFinancePaymentBatchInput!) {
    updateFinancePaymentBatch(input: $input) {
      financePaymentBatch {
        id
        name
        note
        status
      }
    }
  }
'''

        self.finance_payment_batch_delete_mutation = '''
  mutation DeleteFinancePaymentBatch($input: DeleteFinancePaymentBatchInput!) {
    deleteFinancePaymentBatch(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of finance_payment_batches """
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        query = self.finance_payment_batches_query

        variables = self.variables_query_list

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)

        data = executed.get('data')
        self.assertEqual(data['financePaymentBatches']['edges'][0]['node']['name'], finance_payment_batch.name)
        self.assertEqual(data['financePaymentBatches']['edges'][0]['node']['batchType'],
                         finance_payment_batch.batch_type)
        self.assertEqual(data['financePaymentBatches']['edges'][0]['node']['status'],
                         finance_payment_batch.status)
        self.assertEqual(data['financePaymentBatches']['edges'][0]['node']['description'],
                         finance_payment_batch.description)
        self.assertEqual(data['financePaymentBatches']['edges'][0]['node']['note'],
                         finance_payment_batch.note)
        self.assertEqual(data['financePaymentBatches']['edges'][0]['node']['executionDate'],
                         str(finance_payment_batch.execution_date))

    def test_query_permission_denied(self):
        """ Query list of finance_payment_batches - check permission denied """
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        query = self.finance_payment_batches_query
        variables = self.variables_query_list

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of finance_payment_batches with view permission """
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        query = self.finance_payment_batches_query
        variables = self.variables_query_list

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all finance_payment_batches
        self.assertEqual(data['financePaymentBatches']['edges'][0]['node']['name'], finance_payment_batch.name)

    def test_query_anon_user(self):
        """ Query list of finance_payment_batches - anon user """
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        query = self.finance_payment_batches_query
        variables = self.variables_query_list

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one finance_payment_batch as admin """
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        node_id = to_global_id('FinancePaymentBatchNode', finance_payment_batch.id)

        # Now query single finance_payment_batch and check
        executed = execute_test_client_api_query(
            self.finance_payment_batch_query, self.admin_user, variables={"id": node_id}
        )
        data = executed.get('data')
        self.assertEqual(data['financePaymentBatch']['name'], finance_payment_batch.name)
        self.assertEqual(data['financePaymentBatch']['batchType'],
                         finance_payment_batch.batch_type)
        self.assertEqual(data['financePaymentBatch']['status'],
                         finance_payment_batch.status)
        self.assertEqual(data['financePaymentBatch']['description'],
                         finance_payment_batch.description)
        self.assertEqual(data['financePaymentBatch']['note'],
                         finance_payment_batch.note)
        self.assertEqual(data['financePaymentBatch']['executionDate'],
                         str(finance_payment_batch.execution_date))

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one finance payment batch """
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        node_id = to_global_id('FinancePaymentBatchNode', finance_payment_batch.id)

        # Now query single finance_payment_batch and check
        executed = execute_test_client_api_query(
            self.finance_payment_batch_query, self.anon_user, variables={"id": node_id}
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        user = f.RegularUserFactory.create()
        node_id = to_global_id('FinancePaymentBatchNode', finance_payment_batch.id)

        # Now query single finance_payment_batch and check
        executed = execute_test_client_api_query(self.finance_payment_batch_query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()
        # Payment method Cash from fixtures
        node_id = to_global_id('FinancePaymentBatchNode', finance_payment_batch.id)

        # Now query single location and check
        executed = execute_test_client_api_query(self.finance_payment_batch_query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financePaymentBatch']['name'], finance_payment_batch.name)

    def test_create_finance_payment_batch(self):
        """ Create a finance_payment_batch """
        query = self.finance_payment_batch_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createFinancePaymentBatch']['financePaymentBatch']['name'],
                         variables['input']['name'])
        self.assertEqual(data['createFinancePaymentBatch']['financePaymentBatch']['description'],
                         variables['input']['description'])
        self.assertEqual(data['createFinancePaymentBatch']['financePaymentBatch']['batchType'],
                         variables['input']['batchType'])
        self.assertEqual(data['createFinancePaymentBatch']['financePaymentBatch']['note'],
                         variables['input']['note'])
        self.assertEqual(data['createFinancePaymentBatch']['financePaymentBatch']['executionDate'],
                         variables['input']['executionDate'])
        self.assertEqual(data['createFinancePaymentBatch']['financePaymentBatch']['status'],
                         'AWAITING_APPROVAL')

    def test_create_finance_payment_batch_anon_user(self):
        """ Don't allow creating finance_payment_batches for non-logged in users """
        query = self.finance_payment_batch_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_finance_payment_batch_permission_granted(self):
        """ Allow creating finance_payment_batches for users with permissions """
        query = self.finance_payment_batch_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createFinancePaymentBatch']['financePaymentBatch']['name'],
                         variables['input']['name'])

    def test_create_finance_payment_batch_permission_denied(self):
        """ Check create finance_payment_batch permission denied error message """
        query = self.finance_payment_batch_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_finance_payment_batch(self):
        """ Update a finance_payment_batch """
        query = self.finance_payment_batch_update_mutation
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinancePaymentBatchNode', finance_payment_batch.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinancePaymentBatch']['financePaymentBatch']['id'],
                         variables['input']['id'])
        self.assertEqual(data['updateFinancePaymentBatch']['financePaymentBatch']['name'],
                         variables['input']['name'])
        self.assertEqual(data['updateFinancePaymentBatch']['financePaymentBatch']['note'],
                         variables['input']['note'])
        self.assertEqual(data['updateFinancePaymentBatch']['financePaymentBatch']['status'],
                         variables['input']['status'])

    def test_update_finance_payment_batch_anon_user(self):
        """ Don't allow updating finance_payment_batches for non-logged in users """
        query = self.finance_payment_batch_update_mutation
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinancePaymentBatchNode', finance_payment_batch.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_finance_payment_batch_permission_granted(self):
        """ Allow updating finance_payment_batches for users with permissions """
        query = self.finance_payment_batch_update_mutation
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinancePaymentBatchNode', finance_payment_batch.pk)

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinancePaymentBatch']['financePaymentBatch']['name'],
                         variables['input']['name'])

    def test_update_finance_payment_batch_permission_denied(self):
        """ Check update finance_payment_batch permission denied error message """
        query = self.finance_payment_batch_update_mutation
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinancePaymentBatchNode', finance_payment_batch.pk)

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_finance_payment_batch(self):
        """ Archive a finance_payment_batch """
        query = self.finance_payment_batch_delete_mutation
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('FinancePaymentBatchNode', finance_payment_batch.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinancePaymentBatch']['ok'], True)

    def test_delete_finance_payment_batch_anon_user(self):
        """ Archive finance_payment_batch denied for anon user """
        query = self.finance_payment_batch_delete_mutation
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('FinancePaymentBatchNode', finance_payment_batch.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_finance_payment_batch_permission_granted(self):
        """ Allow archiving finance_payment_batches for users with permissions """
        query = self.finance_payment_batch_delete_mutation
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('FinancePaymentBatchNode', finance_payment_batch.pk)

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinancePaymentBatch']['ok'], True)

    def test_delete_finance_payment_batch_permission_denied(self):
        """ Check delete finance_payment_batch permission denied error message """
        query = self.finance_payment_batch_delete_mutation
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('FinancePaymentBatchNode', finance_payment_batch.pk)

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

