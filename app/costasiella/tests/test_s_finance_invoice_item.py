# from graphql.error.located_error import GraphQLLocatedError
import graphql
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser, Permission

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema
from ..modules.gql_tools import get_rid


class GQLFinanceInvoiceItem(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['finance_invoice_group.json', 'finance_payment_methods.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financeinvoiceitem'
        self.permission_add = 'add_financeinvoiceitem'
        self.permission_change = 'change_financeinvoiceitem'
        self.permission_delete = 'delete_financeinvoiceitem'

        self.finance_tax_rate = f.FinanceTaxRateFactory.create()
        self.finance_glaccount = f.FinanceGLAccountFactory.create()
        self.finance_costcenter = f.FinanceCostCenterFactory.create()

        self.variables_create = {
            "input": {}
        }

        self.variables_update = {
            "input": {
              "productName": "Updated product",
              "description": "Updated description",
              "quantity": "10",
              "price": "12.51",
              "financeTaxRate": to_global_id("FinanceTaxRateNode", self.finance_tax_rate.pk),
              "financeGlaccount": to_global_id("FinanceGLAccountNode", self.finance_glaccount.pk),
              "financeCostcenter": to_global_id("FinanceCostCenterNode", self.finance_costcenter.pk)
            }
        }

        self.invoice_items_query = '''
  query FinanceInvoicesItems($financeInvoice: ID!) {
    financeInvoiceItems(first: 100, financeInvoice: $financeInvoice) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          financeInvoice {
            id
          }
          lineNumber
          productName
          description
          quantity
          price
          financeTaxRate {
            id
            name
            percentage
            rateType
          }
          subtotal
          subtotalDisplay
          tax
          taxDisplay
          total
          totalDisplay
          financeGlaccount {
            id
            name
          }
          financeCostcenter {
            id
            name
          }
        }
      }
    }
  }
'''

        self.invoice_item_query = '''
  query FinanceInvoiceItem($id: ID!) {
    financeInvoiceItem(id:$id) {
      id
      financeInvoice {
        id
      }
      lineNumber
      productName
      description
      quantity
      price
      financeTaxRate {
        id
        name
        percentage
        rateType
      }
      subtotal
      subtotalDisplay
      tax
      taxDisplay
      total
      totalDisplay
      financeGlaccount {
        id
        name
      }
      financeCostcenter {
        id
        name
      }
    }
  }
'''

        self.invoice_item_create_mutation = ''' 
  mutation CreateFinanceInvoiceItem($input: CreateFinanceInvoiceItemInput!) {
    createFinanceInvoiceItem(input: $input) {
      financeInvoiceItem {
        id
        financeInvoice {
          id
        }
        lineNumber
        productName
        description
        quantity
        price
        financeTaxRate {
          id
          name
        }
      }
    }
  }
'''

        self.invoice_item_update_mutation = '''
  mutation UpdateFinanceInvoiceItem($input: UpdateFinanceInvoiceItemInput!) {
    updateFinanceInvoiceItem(input: $input) {
      financeInvoiceItem {
        id
        financeInvoice {
          id
        }
        lineNumber
        productName
        description
        quantity
        price
        financeTaxRate {
          id
          name
        }
        financeGlaccount {
          id
          name
        }
        financeCostcenter {
          id
          name
        }
      }
    }
  }
'''

        self.invoice_item_delete_mutation = '''
  mutation DeleteFinanceInvoiceItem($input: DeleteFinanceInvoiceItemInput!) {
    deleteFinanceInvoiceItem(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account invoice items """
        query = self.invoice_items_query
        invoice_item = f.FinanceInvoiceItemFactory.create()

        variables = {
          "financeInvoice": to_global_id('FinanceInvoiceItemNode', invoice_item.finance_invoice.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['financeInvoiceItems']['edges'][0]['node']['id'],
          to_global_id('FinanceInvoiceItemNode', invoice_item.id)
        )
        self.assertEqual(
          data['financeInvoiceItems']['edges'][0]['node']['financeInvoice']['id'],
          to_global_id('FinanceInvoiceNode', invoice_item.finance_invoice.id)
        )
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['lineNumber'], invoice_item.line_number)
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['productName'], invoice_item.product_name)
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['description'], invoice_item.description)
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['quantity'],
                         format(invoice_item.quantity, ".2f"))
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['price'],
                         format(invoice_item.price, ".2f"))
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['financeTaxRate']['id'], 
                         to_global_id('FinanceTaxRateNode', invoice_item.finance_tax_rate.id))
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['subtotal'],
                         format(invoice_item.subtotal, ".2f"))
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['tax'], format(invoice_item.tax, ".2f"))
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['total'], format(invoice_item.total, ".2f"))
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['financeGlaccount']['id'], 
                         to_global_id('FinanceGLAccountNode', invoice_item.finance_glaccount.id))
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['financeCostcenter']['id'], 
                         to_global_id('FinanceCostCenterNode', invoice_item.finance_costcenter.id))

    def test_query_permission_denied(self):
        """ Query list of account invoice items - check permission denied """
        query = self.invoice_items_query
        invoice_item = f.FinanceInvoiceItemFactory.create()

        variables = {
          "financeInvoice": to_global_id('FinanceInvoiceItemNode', invoice_item.finance_invoice.pk)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=invoice_item.finance_invoice.account.id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of account invoice items with view permission """
        query = self.invoice_items_query
        invoice_item = f.FinanceInvoiceItemFactory.create()

        variables = {
          "financeInvoice": to_global_id('FinanceInvoiceItemNode', invoice_item.finance_invoice.pk)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=invoice_item.finance_invoice.account.id)
        permission = Permission.objects.get(codename='view_financeinvoiceitem')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List selected invoice items
        self.assertEqual(
          data['financeInvoiceItems']['edges'][0]['node']['id'],
          to_global_id('FinanceInvoiceItemNode', invoice_item.id)
        )

    def test_query_anon_user(self):
        """ Query list of account invoice items - anon user """
        query = self.invoice_items_query
        invoice_item = f.FinanceInvoiceItemFactory.create()

        variables = {
          "financeInvoice": to_global_id('FinanceInvoiceItemNode', invoice_item.finance_invoice.pk)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account invoice item as admin """   
        invoice_item = f.FinanceInvoiceItemFactory.create()
        
        variables = {
            "id": to_global_id("FinanceInvoiceItemNode", invoice_item.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.invoice_item_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['financeInvoiceItem']['id'],
            to_global_id('FinanceInvoiceItemNode', invoice_item.id)
        )

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account invoice """   
        invoice_item = f.FinanceInvoiceItemFactory.create()
        
        variables = {
            "id": to_global_id("FinanceInvoiceItemNode", invoice_item.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.invoice_item_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        invoice_item = f.FinanceInvoiceItemFactory.create()
        user = invoice_item.finance_invoice.account

        variables = {
            "id": to_global_id("FinanceInvoiceItemNode", invoice_item.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.invoice_item_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        invoice_item = f.FinanceInvoiceItemFactory.create()
        user = invoice_item.finance_invoice.account
        permission = Permission.objects.get(codename='view_financeinvoiceitem')
        user.user_permissions.add(permission)
        user.save()
        
        variables = {
            "id": to_global_id("FinanceInvoiceItemNode", invoice_item.id),
        }

        # Now query single invoice and check   
        executed = execute_test_client_api_query(self.invoice_item_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['financeInvoiceItem']['id'],
            to_global_id('FinanceInvoiceItemNode', invoice_item.id)
        )

    def test_create_invoice_item(self):
        """ Create an account invoice """
        query = self.invoice_item_create_mutation

        invoice = f.FinanceInvoiceFactory.create()
        variables = self.variables_create
        variables['input']['financeInvoice'] = to_global_id('FinanceInvoiceNode', invoice.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        # Get invoice
        rid = get_rid(data['createFinanceInvoiceItem']['financeInvoiceItem']['financeInvoice']['id'])
        invoice = models.FinanceInvoice.objects.get(pk=rid.id)

        self.assertEqual(
            data['createFinanceInvoiceItem']['financeInvoiceItem']['financeInvoice']['id'], 
            variables['input']['financeInvoice']
        )

    def test_create_invoice_item_increate_line_number(self):
        """ Create an account invoice """
        query = self.invoice_item_create_mutation

        invoice = f.FinanceInvoiceFactory.create()
        variables = self.variables_create
        variables['input']['financeInvoice'] = to_global_id('FinanceInvoiceNode', invoice.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        # Get invoice
        rid = get_rid(data['createFinanceInvoiceItem']['financeInvoiceItem']['financeInvoice']['id'])
        invoice = models.FinanceInvoice.objects.get(pk=rid.id)

        self.assertEqual(
            data['createFinanceInvoiceItem']['financeInvoiceItem']['financeInvoice']['id'], 
            variables['input']['financeInvoice']
        )
        self.assertEqual(data['createFinanceInvoiceItem']['financeInvoiceItem']['lineNumber'], 0)

        # Execute again and check if the line number for the 2nd item = 1
        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['createFinanceInvoiceItem']['financeInvoiceItem']['lineNumber'], 1)

    def test_create_invoice_item_anon_user(self):
        """ Don't allow creating account invoices for non-logged in users """
        query = self.invoice_item_create_mutation

        invoice = f.FinanceInvoiceFactory.create()
        variables = self.variables_create
        variables['input']['financeInvoice'] = to_global_id('FinanceInvoiceNode', invoice.id)
        
        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_invoice_item_permission_granted(self):
        """ Allow creating invoices for users with permissions """
        query = self.invoice_item_create_mutation

        invoice = f.FinanceInvoiceFactory.create()
        variables = self.variables_create
        variables['input']['financeInvoice'] = to_global_id('FinanceInvoiceNode', invoice.id)

        # Create regular user
        user = get_user_model().objects.get(pk=invoice.account.id)
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
            data['createFinanceInvoiceItem']['financeInvoiceItem']['financeInvoice']['id'], 
            variables['input']['financeInvoice']
        )

    def test_create_invoice_item_permission_denied(self):
        """ Check create invoice permission denied error message """
        query = self.invoice_item_create_mutation

        invoice = f.FinanceInvoiceFactory.create()
        variables = self.variables_create
        variables['input']['financeInvoice'] = to_global_id('FinanceInvoiceNode', invoice.id)

        # Create regular user
        user = get_user_model().objects.get(pk=invoice.account.id)

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_invoice_item(self):
        """ Update a invoice item """
        query = self.invoice_item_update_mutation

        invoice_item = f.FinanceInvoiceItemFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['updateFinanceInvoiceItem']['financeInvoiceItem']['productName'],
                         variables['input']['productName'])
        self.assertEqual(data['updateFinanceInvoiceItem']['financeInvoiceItem']['description'],
                         variables['input']['description'])
        self.assertEqual(data['updateFinanceInvoiceItem']['financeInvoiceItem']['quantity'],
                         variables['input']['quantity'])
        self.assertEqual(data['updateFinanceInvoiceItem']['financeInvoiceItem']['price'],
                         variables['input']['price'])
        self.assertEqual(
          data['updateFinanceInvoiceItem']['financeInvoiceItem']['financeTaxRate']['id'], 
          variables['input']['financeTaxRate']
        )
        self.assertEqual(
          data['updateFinanceInvoiceItem']['financeInvoiceItem']['financeGlaccount']['id'], 
          variables['input']['financeGlaccount']
        )
        self.assertEqual(
          data['updateFinanceInvoiceItem']['financeInvoiceItem']['financeCostcenter']['id'], 
          variables['input']['financeCostcenter']
        )

    def test_update_invoice_item_line_number(self):
        """ Update a invoice item line number"""
        query = self.invoice_item_update_mutation
        query_create = self.invoice_item_create_mutation

        invoice = f.FinanceInvoiceFactory.create()
        invoice_item = f.FinanceInvoiceItemFactory.create(
          finance_invoice=invoice
        )

        query_create = self.invoice_item_create_mutation
        variables_create = self.variables_create
        variables_create['input']['financeInvoice'] = to_global_id('FinanceInvoiceNode', invoice.id)

        # Add 2 more items
        # Execute again and check if the line number for the 2nd item = 1
        executed = execute_test_client_api_query(
            query_create, 
            self.admin_user, 
            variables=variables_create
        )

        data = executed.get('data')
        id_2 = data['createFinanceInvoiceItem']['financeInvoiceItem']['id']
        rid_2 = get_rid(id_2)
        line_nr_2 = data['createFinanceInvoiceItem']['financeInvoiceItem']['lineNumber']

        self.assertEqual(data['createFinanceInvoiceItem']['financeInvoiceItem']['lineNumber'], 1)

        # Execute again and check if the line number for the 3rd item = 2
        executed = execute_test_client_api_query(
            query_create, 
            self.admin_user, 
            variables=variables_create
        )

        data = executed.get('data')
        id_3 = data['createFinanceInvoiceItem']['financeInvoiceItem']['id']
        rid_3 = get_rid(id_3)
        line_nr_3 = data['createFinanceInvoiceItem']['financeInvoiceItem']['lineNumber']

        self.assertEqual(data['createFinanceInvoiceItem']['financeInvoiceItem']['lineNumber'], 2)

        variables = {
          "input": {
            "lineNumber": 0
          }
        }
        variables['input']['id'] = id_3

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateFinanceInvoiceItem']['financeInvoiceItem']['lineNumber'], 
          variables['input']['lineNumber']
        )

        item_1 = models.FinanceInvoiceItem.objects.get(id=invoice_item.id)
        item_2 = models.FinanceInvoiceItem.objects.get(id=rid_2.id)
        item_3 = models.FinanceInvoiceItem.objects.get(id=rid_3.id)
        self.assertEqual(item_1.line_number, 1)
        self.assertEqual(item_2.line_number, 2)
        self.assertEqual(item_3.line_number, 0)

    def test_update_invoice_item_anon_user(self):
        """ Don't allow updating invoices for non-logged in users """
        query = self.invoice_item_update_mutation

        invoice_item = f.FinanceInvoiceItemFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_invoice_item_permission_granted(self):
        """ Allow updating invoices for users with permissions """
        query = self.invoice_item_update_mutation

        invoice_item = f.FinanceInvoiceItemFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

        user = invoice_item.finance_invoice.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinanceInvoiceItem']['financeInvoiceItem']['productName'], variables['input']['productName'])

    def test_update_invoice_item_permission_denied(self):
        """ Check update invoice permission denied error message """
        query = self.invoice_item_update_mutation

        invoice_item = f.FinanceInvoiceItemFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

        user = invoice_item.finance_invoice.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_invoice_item(self):
        """ Delete an account invoice item """
        query = self.invoice_item_delete_mutation
        invoice_item = f.FinanceInvoiceItemFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceInvoiceItem']['ok'], True)

    def test_delete_invoice_item_check_line_number(self):
        """ Delete an account invoice item """
        query = self.invoice_item_delete_mutation
        invoice = f.FinanceInvoiceFactory.create()
        invoice_item = f.FinanceInvoiceItemFactory.create(
          finance_invoice=invoice
        )

        query_create = self.invoice_item_create_mutation
        variables_create = self.variables_create
        variables_create['input']['financeInvoice'] = to_global_id('FinanceInvoiceNode', invoice.id)

        # Add 2 more items
        # Execute again and check if the line number for the 2nd item = 1
        executed = execute_test_client_api_query(
            query_create, 
            self.admin_user, 
            variables=variables_create
        )

        data = executed.get('data')
        id_2 = data['createFinanceInvoiceItem']['financeInvoiceItem']['id']
        rid_2 = get_rid(id_2)
        line_nr_2 = data['createFinanceInvoiceItem']['financeInvoiceItem']['lineNumber']

        self.assertEqual(data['createFinanceInvoiceItem']['financeInvoiceItem']['lineNumber'], 1)

        # Execute again and check if the line number for the 3rd item = 2
        executed = execute_test_client_api_query(
            query_create, 
            self.admin_user, 
            variables=variables_create
        )
        data = executed.get('data')
        id_3 = data['createFinanceInvoiceItem']['financeInvoiceItem']['id']
        rid_3 = get_rid(id_3)
        line_nr_3 = data['createFinanceInvoiceItem']['financeInvoiceItem']['lineNumber']

        self.assertEqual(data['createFinanceInvoiceItem']['financeInvoiceItem']['lineNumber'], 2)
        
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceInvoiceItem']['ok'], True)

        # Check re-numbering items 2 and 3
        item_2 = models.FinanceInvoiceItem.objects.get(pk=rid_2.id)
        item_3 = models.FinanceInvoiceItem.objects.get(pk=rid_3.id)

        self.assertEqual(item_2.line_number, line_nr_2 - 1)
        self.assertEqual(item_3.line_number, line_nr_3 - 1)

    def test_delete_invoice_item_anon_user(self):
        """ Delete invoice denied for anon user """
        query = self.invoice_item_delete_mutation
        invoice_item = f.FinanceInvoiceItemFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_invoice_item_permission_granted(self):
        """ Allow deleting invoices for users with permissions """
        query = self.invoice_item_delete_mutation
        invoice_item = f.FinanceInvoiceItemFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

        # Give permissions
        user = invoice_item.finance_invoice.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceInvoiceItem']['ok'], True)

    def test_delete_invoice_item_permission_denied(self):
        """ Check delete invoice permission denied error message """
        query = self.invoice_item_delete_mutation
        invoice_item = f.FinanceInvoiceItemFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)
        
        user = invoice_item.finance_invoice.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
