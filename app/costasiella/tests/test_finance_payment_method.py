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


class GQLFinancePaymentMethod(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['finance_payment_methods.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financepaymentmethod'
        self.permission_add = 'add_financepaymentmethod'
        self.permission_change = 'change_financepaymentmethod'
        self.permission_delete = 'delete_financepaymentmethod'

        self.variables_create = {
            "input": {
                "name": "New paymentmethod",
                "code" : "123"
            }
        }

        self.variables_update = {
            "input": {
                "name": "Updated paymentmethod",
                "code" : "987"
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.paymentmethods_query = '''
  query FinancePaymentMethods($after: String, $before: String, $archived: Boolean) {
    financePaymentMethods(first: 15, before: $before, after: $after, archived: $archived) {
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
          systemMethod
          name
          code
        }
      }
    }
  }
'''

        self.paymentmethod_query = '''
  query FinancePaymentMethod($id: ID!) {
    financePaymentMethod(id:$id) {
      id
      name
      code
      archived
    }
  }
'''

        self.paymentmethod_create_mutation = ''' 
  mutation CreateFinancePaymentMethod($input:CreateFinancePaymentMethodInput!) {
    createFinancePaymentMethod(input: $input) {
      financePaymentMethod{
        id
        archived
        name
        code
      }
    }
  }
'''

        self.paymentmethod_update_mutation = '''
  mutation UpdateFinancePaymentMethod($input: UpdateFinancePaymentMethodInput!) {
    updateFinancePaymentMethod(input: $input) {
      financePaymentMethod {
        id
        name
        code
      }
    }
  }
'''

        self.paymentmethod_archive_mutation = '''
  mutation ArchiveFinancePaymentMethod($input: ArchiveFinancePaymentMethodInput!) {
    archiveFinancePaymentMethod(input: $input) {
      financePaymentMethod {
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
        """ Query list of paymentmethods """
        query = self.paymentmethods_query
        # The payment method "Cash" from the fixtures will be listed first
        paymentmethod = models.FinancePaymentMethod.objects.get(pk=101)
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['financePaymentMethods']['edges'][0]['node']['name'], paymentmethod.name)
        self.assertEqual(data['financePaymentMethods']['edges'][0]['node']['archived'], paymentmethod.archived)
        self.assertEqual(data['financePaymentMethods']['edges'][0]['node']['systemMethod'], paymentmethod.system_method)
        self.assertEqual(data['financePaymentMethods']['edges'][0]['node']['code'], paymentmethod.code)


    def test_query_permission_denied(self):
        """ Query list of paymentmethods - check permission denied """
        query = self.paymentmethods_query
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permission_granted(self):
        """ Query list of paymentmethods with view permission """
        query = self.paymentmethods_query
        # The payment method "Cash" from the fixtures will be listed first
        paymentmethod = models.FinancePaymentMethod.objects.get(pk=101)
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financepaymentmethod')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all paymentmethods
        self.assertEqual(data['financePaymentMethods']['edges'][0]['node']['name'], paymentmethod.name)
        self.assertEqual(data['financePaymentMethods']['edges'][0]['node']['archived'], paymentmethod.archived)
        self.assertEqual(data['financePaymentMethods']['edges'][0]['node']['code'], paymentmethod.code)


    def test_query_anon_user(self):
        """ Query list of paymentmethods - anon user """
        query = self.paymentmethods_query
        paymentmethod = f.FinancePaymentMethodFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one paymentmethod as admin """   
        # The payment method "Cash" from the fixtures
        paymentmethod = models.FinancePaymentMethod.objects.get(pk=101)
        node_id = to_global_id('FinancePaymentMethodNode', 101)

        # Now query single paymentmethod and check
        executed = execute_test_client_api_query(self.paymentmethod_query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financePaymentMethod']['name'], paymentmethod.name)
        self.assertEqual(data['financePaymentMethod']['archived'], paymentmethod.archived)
        self.assertEqual(data['financePaymentMethod']['code'], paymentmethod.code)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one glacount """   
        paymentmethod = models.FinancePaymentMethod.objects.get(pk=101)
        node_id = to_global_id('FinancePaymentMethodNode', 101)

        # Now query single paymentmethod and check
        executed = execute_test_client_api_query(self.paymentmethod_query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        node_id = to_global_id('FinancePaymentMethodNode', 101)

        # Now query single paymentmethod and check
        executed = execute_test_client_api_query(self.paymentmethod_query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financepaymentmethod')
        user.user_permissions.add(permission)
        user.save()
        # Payment method Cash from fixtures
        paymentmethod = models.FinancePaymentMethod.objects.get(pk=101)
        node_id = to_global_id('FinancePaymentMethodNode', 101)

        # Now query single location and check   
        executed = execute_test_client_api_query(self.paymentmethod_query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financePaymentMethod']['name'], paymentmethod.name)


    def test_create_paymentmethod(self):
        """ Create a paymentmethod """
        query = self.paymentmethod_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createFinancePaymentMethod']['financePaymentMethod']['name'], variables['input']['name'])
        self.assertEqual(data['createFinancePaymentMethod']['financePaymentMethod']['archived'], False)
        self.assertEqual(data['createFinancePaymentMethod']['financePaymentMethod']['code'], variables['input']['code'])


    def test_create_paymentmethod_anon_user(self):
        """ Don't allow creating paymentmethods for non-logged in users """
        query = self.paymentmethod_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_location_permission_granted(self):
        """ Allow creating paymentmethods for users with permissions """
        query = self.paymentmethod_create_mutation
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
        self.assertEqual(data['createFinancePaymentMethod']['financePaymentMethod']['name'], variables['input']['name'])
        self.assertEqual(data['createFinancePaymentMethod']['financePaymentMethod']['archived'], False)
        self.assertEqual(data['createFinancePaymentMethod']['financePaymentMethod']['code'], variables['input']['code'])


    def test_create_paymentmethod_permission_denied(self):
        """ Check create paymentmethod permission denied error message """
        query = self.paymentmethod_create_mutation
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


    def test_update_paymentmethod(self):
        """ Update a paymentmethod """
        query = self.paymentmethod_update_mutation
        paymentmethod = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinancePaymentMethodNode', paymentmethod.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinancePaymentMethod']['financePaymentMethod']['name'], variables['input']['name'])
        self.assertEqual(data['updateFinancePaymentMethod']['financePaymentMethod']['code'], variables['input']['code'])


    def test_update_paymentmethod_anon_user(self):
        """ Don't allow updating paymentmethods for non-logged in users """
        query = self.paymentmethod_update_mutation
        paymentmethod = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinancePaymentMethodNode', paymentmethod.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_paymentmethod_permission_granted(self):
        """ Allow updating paymentmethods for users with permissions """
        query = self.paymentmethod_update_mutation
        paymentmethod = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinancePaymentMethodNode', paymentmethod.pk)

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
        self.assertEqual(data['updateFinancePaymentMethod']['financePaymentMethod']['name'], variables['input']['name'])
        self.assertEqual(data['updateFinancePaymentMethod']['financePaymentMethod']['code'], variables['input']['code'])


    def test_update_paymentmethod_permission_denied(self):
        """ Check update paymentmethod permission denied error message """
        query = self.paymentmethod_update_mutation
        paymentmethod = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinancePaymentMethodNode', paymentmethod.pk)

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


    def test_archive_paymentmethod(self):
        """ Archive a paymentmethod """
        query = self.paymentmethod_archive_mutation
        paymentmethod = f.FinancePaymentMethodFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinancePaymentMethodNode', paymentmethod.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveFinancePaymentMethod']['financePaymentMethod']['archived'], variables['input']['archived'])


    def test_unable_to_archive_system_paymentmethod(self):
        """ Test that we can't archive a sytem payment method """
        query = self.paymentmethod_archive_mutation
        # This is the "Cash" system payment method from the fixtures
        paymentmethod = models.FinancePaymentMethod.objects.get(pk=101)
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinancePaymentMethodNode', paymentmethod.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Unable to archive, this is a system method!')


    def test_archive_paymentmethod_anon_user(self):
        """ Archive paymentmethod denied for anon user """
        query = self.paymentmethod_archive_mutation
        paymentmethod = f.FinancePaymentMethodFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinancePaymentMethodNode', paymentmethod.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_paymentmethod_permission_granted(self):
        """ Allow archiving paymentmethods for users with permissions """
        query = self.paymentmethod_archive_mutation
        paymentmethod = f.FinancePaymentMethodFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinancePaymentMethodNode', paymentmethod.pk)

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
        self.assertEqual(data['archiveFinancePaymentMethod']['financePaymentMethod']['archived'], variables['input']['archived'])


    def test_archive_paymentmethod_permission_denied(self):
        """ Check archive paymentmethod permission denied error message """
        query = self.paymentmethod_archive_mutation
        paymentmethod = f.FinancePaymentMethodFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinancePaymentMethodNode', paymentmethod.pk)
        
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

