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

        self.permission_view = 'view_financefinance_payment_batch'
        self.permission_add = 'add_financefinance_payment_batch'
        self.permission_change = 'change_financefinance_payment_batch'
        self.permission_delete = 'delete_financefinance_payment_batch'

        self.variables_create = {
            "input": {
                "name": "New finance_payment_batch",
                "description": "hello",
                "batchCategoryType": "COLLECTION"
                
            }
        }

        self.variables_update = {
            "input": {
                "name": "Updated finance_payment_batch",
                "description": "hello",
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.financefinance_payment_batches_query = '''
  query FinancePaymentBatches($after: String, $before: String, $batchType: String!) {
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
      }
    }
  }
'''

        self.finance_payment_batch_update_mutation = '''
  mutation UpdateFinancePaymentBatch($input:UpdateFinancePaymentBatchInput!) {
    updateFinancePaymentBatch(input: $input) {
      financePaymentBatch {
        id
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
        """ Query list of financefinance_payment_batches """
        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        query = self.financefinance_payment_batches_query

        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        print(executed)

        data = executed.get('data')
        self.assertEqual(data['financePaymentBatches']['edges'][0]['node']['name'], finance_payment_batch.name)
        self.assertEqual(data['financePaymentBatches']['edges'][0]['node']['archived'],
                         finance_payment_batch.archived)
        self.assertEqual(data['financePaymentBatches']['edges'][0]['node']['description'],
                         finance_payment_batch.description)
        self.assertEqual(data['financePaymentBatches']['edges'][0]['node']['batchCategoryType'],
                         finance_payment_batch.batch_category_type)

    # def test_query_permission_denied(self):
    #     """ Query list of financefinance_payment_batches - check permission denied """
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     query = self.financefinance_payment_batches_query
    #     variables = {
    #         'archived': False
    #     }
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     errors = executed.get('errors')
    # 
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    # 
    # def test_query_permission_granted(self):
    #     """ Query list of financefinance_payment_batches with view permission """
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     query = self.financefinance_payment_batches_query
    #     variables = {
    #         'archived': False
    #     }
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_financefinance_payment_batch')
    #     user.user_permissions.add(permission)
    #     user.save()
    # 
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')
    # 
    #     # List all financefinance_payment_batches
    #     self.assertEqual(data['financePaymentBatches']['edges'][0]['node']['name'], finance_payment_batch.name)
    # 
    # def test_query_anon_user(self):
    #     """ Query list of financefinance_payment_batches - anon user """
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     query = self.financefinance_payment_batches_query
    #     variables = {
    #         'archived': False
    #     }
    # 
    #     executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # def test_query_one(self):
    #     """ Query one finance_payment_batch as admin """
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     node_id = to_global_id('FinancePaymentBatchCategoryNode', finance_payment_batch.id)
    # 
    #     # Now query single finance_payment_batch and check
    #     executed = execute_test_client_api_query(
    #         self.finance_payment_batch_query, self.admin_user, variables={"id": node_id}
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['financePaymentBatchCategory']['name'], finance_payment_batch.name)
    #     self.assertEqual(data['financePaymentBatchCategory']['archived'], finance_payment_batch.archived)
    #     self.assertEqual(data['financePaymentBatchCategory']['description'], finance_payment_batch.description)
    #     self.assertEqual(data['financePaymentBatchCategory']['batchCategoryType'],
    #                      finance_payment_batch.batch_category_type)
    # 
    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one glacount """
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     node_id = to_global_id('FinancePaymentBatchCategoryNode', finance_payment_batch.id)
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
    #     node_id = to_global_id('FinancePaymentBatchCategoryNode', finance_payment_batch.id)
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
    #     permission = Permission.objects.get(codename='view_financefinance_payment_batch')
    #     user.user_permissions.add(permission)
    #     user.save()
    #     # Payment method Cash from fixtures
    #     node_id = to_global_id('FinancePaymentBatchCategoryNode', finance_payment_batch.id)
    # 
    #     # Now query single location and check
    #     executed = execute_test_client_api_query(self.finance_payment_batch_query, user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['financePaymentBatchCategory']['name'], finance_payment_batch.name)
    # 
    # def test_create_finance_payment_batch(self):
    #     """ Create a finance_payment_batch """
    #     query = self.finance_payment_batch_create_mutation
    #     variables = self.variables_create
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createFinancePaymentBatchCategory']['financePaymentBatchCategory']['name'],
    #                      variables['input']['name'])
    #     self.assertEqual(data['createFinancePaymentBatchCategory']['financePaymentBatchCategory']['archived'],
    #                      False)
    #     self.assertEqual(data['createFinancePaymentBatchCategory']['financePaymentBatchCategory']['description'],
    #                      variables['input']['description'])
    #     self.assertEqual(data['createFinancePaymentBatchCategory']['financePaymentBatchCategory']['batchCategoryType'],
    #                      variables['input']['batchCategoryType'])
    # 
    # def test_create_finance_payment_batch_anon_user(self):
    #     """ Don't allow creating financefinance_payment_batches for non-logged in users """
    #     query = self.finance_payment_batch_create_mutation
    #     variables = self.variables_create
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
    # def test_create_finance_payment_batch_permission_granted(self):
    #     """ Allow creating financefinance_payment_batches for users with permissions """
    #     query = self.finance_payment_batch_create_mutation
    #     variables = self.variables_create
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
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
    #     self.assertEqual(data['createFinancePaymentBatchCategory']['financePaymentBatchCategory']['name'],
    #                      variables['input']['name'])
    # 
    # def test_create_finance_payment_batch_permission_denied(self):
    #     """ Check create finance_payment_batch permission denied error message """
    #     query = self.finance_payment_batch_create_mutation
    #     variables = self.variables_create
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
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
    # def test_update_finance_payment_batch(self):
    #     """ Update a finance_payment_batch """
    #     query = self.finance_payment_batch_update_mutation
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', finance_payment_batch.pk)
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateFinancePaymentBatchCategory']['financePaymentBatchCategory']['name'],
    #                      variables['input']['name'])
    #     self.assertEqual(data['updateFinancePaymentBatchCategory']['financePaymentBatchCategory']['archived'],
    #                      False)
    #     self.assertEqual(data['updateFinancePaymentBatchCategory']['financePaymentBatchCategory']['description'],
    #                      variables['input']['description'])
    # 
    # def test_update_finance_payment_batch_anon_user(self):
    #     """ Don't allow updating financefinance_payment_batches for non-logged in users """
    #     query = self.finance_payment_batch_update_mutation
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', finance_payment_batch.pk)
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # def test_update_finance_payment_batch_permission_granted(self):
    #     """ Allow updating financefinance_payment_batches for users with permissions """
    #     query = self.finance_payment_batch_update_mutation
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', finance_payment_batch.pk)
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
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
    #     self.assertEqual(data['updateFinancePaymentBatchCategory']['financePaymentBatchCategory']['name'],
    #                      variables['input']['name'])
    # 
    # def test_update_finance_payment_batch_permission_denied(self):
    #     """ Check update finance_payment_batch permission denied error message """
    #     query = self.finance_payment_batch_update_mutation
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', finance_payment_batch.pk)
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
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
    # def test_archive_finance_payment_batch(self):
    #     """ Archive a finance_payment_batch """
    #     query = self.finance_payment_batch_archive_mutation
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', finance_payment_batch.pk)
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveFinancePaymentBatchCategory']['financePaymentBatchCategory']['archived'],
    #                      variables['input']['archived'])
    # 
    # def test_archive_finance_payment_batch_anon_user(self):
    #     """ Archive finance_payment_batch denied for anon user """
    #     query = self.finance_payment_batch_archive_mutation
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', finance_payment_batch.pk)
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # def test_archive_finance_payment_batch_permission_granted(self):
    #     """ Allow archiving financefinance_payment_batches for users with permissions """
    #     query = self.finance_payment_batch_archive_mutation
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', finance_payment_batch.pk)
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
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
    #     self.assertEqual(data['archiveFinancePaymentBatchCategory']['financePaymentBatchCategory']['archived'],
    #                      variables['input']['archived'])
    # 
    # def test_archive_finance_payment_batch_permission_denied(self):
    #     """ Check archive finance_payment_batch permission denied error message """
    #     query = self.finance_payment_batch_archive_mutation
    #     finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', finance_payment_batch.pk)
    # 
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
    # 
