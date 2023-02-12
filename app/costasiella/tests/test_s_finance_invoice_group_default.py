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



class GQLFinanceInvoiceGroupDefaultDefault(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['finance_invoice_group.json', 'finance_invoice_group_defaults.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_group = 'view_financeinvoicegroup'
        self.permission_view = 'view_financeinvoicegroupdefault'
        self.permission_add = 'add_financeinvoicegroupdefault'
        self.permission_change = 'change_financeinvoicegroupdefault'
        self.permission_delete = 'delete_financeinvoicegroupdefault'

        self.variables_update = {
            "input": {}
        }

        self.invoicegroupdefaults_query = '''
query FinanceInvoiceGroupDefaults {
  financeInvoiceGroupDefaults(first: 100) {
    edges {
      node {
        id
        itemType
        financeInvoiceGroup {
          id
          name
        }
      }
    }
  }
}
'''

#         self.invoicegroupdefault_query = '''
#   query FinanceInvoiceGroupDefault($id: ID!) {
#     financeInvoiceGroupDefault(id:$id) {
#       id
#       archived
#       displayPublic
#       name
#       nextId
#       dueAfterDays
#       prefix
#       prefixYear
#       autoResetPrefixYear
#       terms
#       footer
#       code
#     }
#   }
# '''


        self.invoicegroupdefault_update_mutation = '''
  mutation UpdateFinanceInvoiceGroupDefault($input: UpdateFinanceInvoiceGroupDefaultInput!) {
    updateFinanceInvoiceGroupDefault(input: $input) {
      financeInvoiceGroupDefault {
        id
        itemType
        financeInvoiceGroup {
          id
          name
        }
      }
    }
  }
'''


    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of invoicegroupdefaults """
        query = self.invoicegroupdefaults_query
        
        first_default = models.FinanceInvoiceGroupDefault.objects.all().first()
        default_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')
        self.assertEqual(data['financeInvoiceGroupDefaults']['edges'][0]['node']['id'], 
            to_global_id('FinanceInvoiceGroupDefaultNode', first_default.id))
        self.assertEqual(data['financeInvoiceGroupDefaults']['edges'][0]['node']['itemType'], 
            first_default.item_type)
        self.assertEqual(data['financeInvoiceGroupDefaults']['edges'][0]['node']['financeInvoiceGroup']['id'], 
            to_global_id('FinanceInvoiceGroupNode', default_invoice_group.id)
        )
        

    def test_query_permission_denied(self):
        """ Query list of invoicegroupdefaults - check permission denied """
        query = self.invoicegroupdefaults_query

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user)

        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permission_granted(self):
        """ Query list of invoicegroupdefaults with view permission """
        query = self.invoicegroupdefaults_query

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financeinvoicegroupdefault')
        user.user_permissions.add(permission)
        # View group
        permission = Permission.objects.get(codename=self.permission_view_group)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user)
        data = executed.get('data')

        first_default = models.FinanceInvoiceGroupDefault.objects.all().first()
        self.assertEqual(data['financeInvoiceGroupDefaults']['edges'][0]['node']['id'], 
            to_global_id('FinanceInvoiceGroupDefaultNode', first_default.id))


    def test_query_anon_user(self):
        """ Query list of invoicegroupdefaults - anon user """
        query = self.invoicegroupdefaults_query

        executed = execute_test_client_api_query(query, self.anon_user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


# Comment out tests for now, as this endpoint isn't used anywhere

    # def test_query_one(self):
    #     """ Query one invoicegroupdefault as admin """   
    #     invoicegroupdefault = f.FinanceInvoiceGroupDefaultFactory.create()

    #     # First query invoicegroupdefaults to get node id easily
    #     node_id = to_global_id('FinanceInvoiceGroupDefaultNode', invoicegroupdefault.id)

    #     # Now query single invoicegroupdefault and check
    #     executed = execute_test_client_api_query(self.invoicegroupdefault_query, self.admin_user, variables={"id": node_id})
    #     data = executed.get('data')

    #     self.assertEqual(data['financeInvoiceGroupDefault']['name'], invoicegroupdefault.name)


    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one glacount """   
    #     invoicegroupdefault = f.FinanceInvoiceGroupDefaultFactory.create()

    #     # First query invoicegroupdefaults to get node id easily
    #     node_id = to_global_id('FinanceInvoiceGroupDefaultNode', invoicegroupdefault.id)

    #     # Now query single invoicegroupdefault and check
    #     executed = execute_test_client_api_query(self.invoicegroupdefault_query, self.anon_user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     invoicegroupdefault = f.FinanceInvoiceGroupDefaultFactory.create()

    #     # First query invoicegroupdefaults to get node id easily
    #     node_id = to_global_id('FinanceInvoiceGroupDefaultNode', invoicegroupdefault.id)

    #     # Now query single invoicegroupdefault and check
    #     executed = execute_test_client_api_query(self.invoicegroupdefault_query, user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_financeinvoicegroupdefault')
    #     user.user_permissions.add(permission)
    #     user.save()
    #     invoicegroupdefault = f.FinanceInvoiceGroupDefaultFactory.create()

    #     # First query invoicegroupdefaults to get node id easily
    #     node_id = to_global_id('FinanceInvoiceGroupDefaultNode', invoicegroupdefault.id)

    #     # Now query single location and check   
    #     executed = execute_test_client_api_query(self.invoicegroupdefault_query, user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['financeInvoiceGroupDefault']['name'], invoicegroupdefault.name)


    def test_update_invoicegroupdefault(self):
        """ Update a invoicegroupdefault """
        query = self.invoicegroupdefault_update_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_update

        first_invoice_group_default = models.FinanceInvoiceGroupDefault.objects.all().first()
        variables['input']['id'] = to_global_id('FinanceInvoiceGroupDefaultNode', first_invoice_group_default.pk)
        variables['input']['financeInvoiceGroup'] = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['updateFinanceInvoiceGroupDefault']['financeInvoiceGroupDefault']['id'], variables['input']['id'])
        self.assertEqual(data['updateFinanceInvoiceGroupDefault']['financeInvoiceGroupDefault']['financeInvoiceGroup']['id'], 
            variables['input']['financeInvoiceGroup']
        )
        

    def test_update_invoicegroupdefault_anon_user(self):
        """ Don't allow updating invoicegroupdefaults for non-logged in users """
        query = self.invoicegroupdefault_update_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_update
        first_invoice_group_default = models.FinanceInvoiceGroupDefault.objects.all().first()
        variables['input']['id'] = to_global_id('FinanceInvoiceGroupDefaultNode', first_invoice_group_default.pk)
        variables['input']['financeInvoiceGroup'] = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_invoicegroupdefault_permission_granted(self):
        """ Allow updating invoicegroupdefaults for users with permissions """
        query = self.invoicegroupdefault_update_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_update
        first_invoice_group_default = models.FinanceInvoiceGroupDefault.objects.all().first()
        variables['input']['id'] = to_global_id('FinanceInvoiceGroupDefaultNode', first_invoice_group_default.pk)
        variables['input']['financeInvoiceGroup'] = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        # View group
        permission = Permission.objects.get(codename=self.permission_view_group)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinanceInvoiceGroupDefault']['financeInvoiceGroupDefault']['financeInvoiceGroup']['id'], 
            variables['input']['financeInvoiceGroup']
        )


    def test_update_invoicegroupdefault_permission_denied(self):
        """ Check update invoicegroupdefault permission denied error message """
        query = self.invoicegroupdefault_update_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_update
        first_invoice_group_default = models.FinanceInvoiceGroupDefault.objects.all().first()
        variables['input']['id'] = to_global_id('FinanceInvoiceGroupDefaultNode', first_invoice_group_default.pk)
        variables['input']['financeInvoiceGroup'] = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

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

