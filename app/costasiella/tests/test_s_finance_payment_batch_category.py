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


class GQLFinancePaymentBatchCategory(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financepaymentbatchcategory'
        self.permission_add = 'add_financepaymentbatchcategory'
        self.permission_change = 'change_financepaymentbatchcategory'
        self.permission_delete = 'delete_financepaymentbatchcategory'

        self.variables_create = {
            "input": {
                "name": "New paymentbatchcategory",
                "description": "hello",
                "batchCategoryType": "COLLECTION"
                
            }
        }

        self.variables_update = {
            "input": {
                "name": "Updated paymentbatchcategory",
                "description": "hello",
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.paymentbatchcategories_query = '''
  query FinancePaymentBatchCategories($after: String, $before: String, $archived: Boolean) {
    financePaymentBatchCategories(first: 15, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          description
          batchCategoryType
          name
        }
      }
    }
  }
'''

        self.paymentbatchcategory_query = '''
  query FinancePaymentBatchCategory($id: ID!) {
    financePaymentBatchCategory(id:$id) {
      id
      name
      description
      archived
      batchCategoryType
    }
  }
'''

        self.paymentbatchcategory_create_mutation = ''' 
  mutation CreateFinancePaymentBatchCategory($input:CreateFinancePaymentBatchCategoryInput!) {
    createFinancePaymentBatchCategory(input: $input) {
      financePaymentBatchCategory {
        id
        name
        description
        batchCategoryType
        archived
      }
    }
  }
'''

        self.paymentbatchcategory_update_mutation = '''
  mutation UpdateFinancePaymentBatchCategory($input: UpdateFinancePaymentBatchCategoryInput!) {
    updateFinancePaymentBatchCategory(input: $input) {
      financePaymentBatchCategory {
        id
        name
        description
        batchCategoryType
        archived
      }
    }
  }
'''

        self.paymentbatchcategory_archive_mutation = '''
  mutation ArchiveFinancePaymentBatchCategory($input: ArchiveFinancePaymentBatchCategoryInput!) {
    archiveFinancePaymentBatchCategory(input: $input) {
      financePaymentBatchCategory {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of paymentbatchcategories """
        payment_batch_category = f.FinancePaymentBatchCategoryCollectionFactory.create()
        query = self.paymentbatchcategories_query

        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)

        data = executed.get('data')
        self.assertEqual(data['financePaymentBatchCategories']['edges'][0]['node']['name'], payment_batch_category.name)
        self.assertEqual(data['financePaymentBatchCategories']['edges'][0]['node']['archived'],
                         payment_batch_category.archived)
        self.assertEqual(data['financePaymentBatchCategories']['edges'][0]['node']['description'],
                         payment_batch_category.description)
        self.assertEqual(data['financePaymentBatchCategories']['edges'][0]['node']['batchCategoryType'],
                         payment_batch_category.batch_category_type)

    def test_query_permission_denied(self):
        """ Query list of paymentbatchcategories - check permission denied """
        payment_batch_category = f.FinancePaymentBatchCategoryCollectionFactory.create()
        query = self.paymentbatchcategories_query
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of paymentbatchcategories with view permission """
        payment_batch_category = f.FinancePaymentBatchCategoryCollectionFactory.create()
        query = self.paymentbatchcategories_query
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financepaymentbatchcategory')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all paymentbatchcategories
        self.assertEqual(data['financePaymentBatchCategories']['edges'][0]['node']['name'], payment_batch_category.name)

    def test_query_anon_user(self):
        """ Query list of paymentbatchcategories - anon user """
        payment_batch_category = f.FinancePaymentBatchCategoryCollectionFactory.create()
        query = self.paymentbatchcategories_query
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one paymentbatchcategory as admin """
        payment_batch_category = f.FinancePaymentBatchCategoryCollectionFactory.create()
        node_id = to_global_id('FinancePaymentBatchCategoryNode', payment_batch_category.id)

        # Now query single paymentbatchcategory and check
        executed = execute_test_client_api_query(
            self.paymentbatchcategory_query, self.admin_user, variables={"id": node_id}
        )
        data = executed.get('data')
        self.assertEqual(data['financePaymentBatchCategory']['name'], payment_batch_category.name)
        self.assertEqual(data['financePaymentBatchCategory']['archived'], payment_batch_category.archived)
        self.assertEqual(data['financePaymentBatchCategory']['description'], payment_batch_category.description)
        self.assertEqual(data['financePaymentBatchCategory']['batchCategoryType'],
                         payment_batch_category.batch_category_type)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one glacount """
        payment_batch_category = f.FinancePaymentBatchCategoryCollectionFactory.create()
        node_id = to_global_id('FinancePaymentBatchCategoryNode', payment_batch_category.id)

        # Now query single paymentbatchcategory and check
        executed = execute_test_client_api_query(
            self.paymentbatchcategory_query, self.anon_user, variables={"id": node_id}
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        payment_batch_category = f.FinancePaymentBatchCategoryCollectionFactory.create()
        user = f.RegularUserFactory.create()
        node_id = to_global_id('FinancePaymentBatchCategoryNode', payment_batch_category.id)

        # Now query single paymentbatchcategory and check
        executed = execute_test_client_api_query(self.paymentbatchcategory_query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        payment_batch_category = f.FinancePaymentBatchCategoryCollectionFactory.create()
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financepaymentbatchcategory')
        user.user_permissions.add(permission)
        user.save()
        # Payment method Cash from fixtures
        node_id = to_global_id('FinancePaymentBatchCategoryNode', payment_batch_category.id)

        # Now query single location and check
        executed = execute_test_client_api_query(self.paymentbatchcategory_query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financePaymentBatchCategory']['name'], payment_batch_category.name)

    def test_create_paymentbatchcategory(self):
        """ Create a paymentbatchcategory """
        query = self.paymentbatchcategory_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createFinancePaymentBatchCategory']['financePaymentBatchCategory']['name'],
                         variables['input']['name'])
        self.assertEqual(data['createFinancePaymentBatchCategory']['financePaymentBatchCategory']['archived'],
                         False)
        self.assertEqual(data['createFinancePaymentBatchCategory']['financePaymentBatchCategory']['description'],
                         variables['input']['description'])
        self.assertEqual(data['createFinancePaymentBatchCategory']['financePaymentBatchCategory']['batchCategoryType'],
                         variables['input']['batchCategoryType'])

    def test_create_paymentbatchcategory_anon_user(self):
        """ Don't allow creating paymentbatchcategories for non-logged in users """
        query = self.paymentbatchcategory_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_paymentbatchcategory_permission_granted(self):
        """ Allow creating paymentbatchcategories for users with permissions """
        query = self.paymentbatchcategory_create_mutation
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
        self.assertEqual(data['createFinancePaymentBatchCategory']['financePaymentBatchCategory']['name'],
                         variables['input']['name'])

    def test_create_paymentbatchcategory_permission_denied(self):
        """ Check create paymentbatchcategory permission denied error message """
        query = self.paymentbatchcategory_create_mutation
        variables = self.variables_create

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

    def test_update_paymentbatchcategory(self):
        """ Update a paymentbatchcategory """
        query = self.paymentbatchcategory_update_mutation
        paymentbatchcategory = f.FinancePaymentBatchCategoryCollectionFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', paymentbatchcategory.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinancePaymentBatchCategory']['financePaymentBatchCategory']['name'],
                         variables['input']['name'])
        self.assertEqual(data['updateFinancePaymentBatchCategory']['financePaymentBatchCategory']['archived'],
                         False)
        self.assertEqual(data['updateFinancePaymentBatchCategory']['financePaymentBatchCategory']['description'],
                         variables['input']['description'])

    def test_update_paymentbatchcategory_anon_user(self):
        """ Don't allow updating paymentbatchcategories for non-logged in users """
        query = self.paymentbatchcategory_update_mutation
        paymentbatchcategory = f.FinancePaymentBatchCategoryCollectionFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', paymentbatchcategory.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_paymentbatchcategory_permission_granted(self):
        """ Allow updating paymentbatchcategories for users with permissions """
        query = self.paymentbatchcategory_update_mutation
        paymentbatchcategory = f.FinancePaymentBatchCategoryCollectionFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', paymentbatchcategory.pk)

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
        self.assertEqual(data['updateFinancePaymentBatchCategory']['financePaymentBatchCategory']['name'],
                         variables['input']['name'])

    def test_update_paymentbatchcategory_permission_denied(self):
        """ Check update paymentbatchcategory permission denied error message """
        query = self.paymentbatchcategory_update_mutation
        paymentbatchcategory = f.FinancePaymentBatchCategoryCollectionFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', paymentbatchcategory.pk)

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

    def test_archive_paymentbatchcategory(self):
        """ Archive a paymentbatchcategory """
        query = self.paymentbatchcategory_archive_mutation
        paymentbatchcategory = f.FinancePaymentBatchCategoryCollectionFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', paymentbatchcategory.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveFinancePaymentBatchCategory']['financePaymentBatchCategory']['archived'],
                         variables['input']['archived'])

    def test_archive_paymentbatchcategory_anon_user(self):
        """ Archive paymentbatchcategory denied for anon user """
        query = self.paymentbatchcategory_archive_mutation
        paymentbatchcategory = f.FinancePaymentBatchCategoryCollectionFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', paymentbatchcategory.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_archive_paymentbatchcategory_permission_granted(self):
        """ Allow archiving paymentbatchcategories for users with permissions """
        query = self.paymentbatchcategory_archive_mutation
        paymentbatchcategory = f.FinancePaymentBatchCategoryCollectionFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', paymentbatchcategory.pk)

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
        self.assertEqual(data['archiveFinancePaymentBatchCategory']['financePaymentBatchCategory']['archived'],
                         variables['input']['archived'])

    def test_archive_paymentbatchcategory_permission_denied(self):
        """ Check archive paymentbatchcategory permission denied error message """
        query = self.paymentbatchcategory_archive_mutation
        paymentbatchcategory = f.FinancePaymentBatchCategoryCollectionFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinancePaymentBatchCategoryNode', paymentbatchcategory.pk)

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

