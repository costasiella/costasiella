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

        # self.account = f.RegularUserFactory.create()

        self.variables_create = {
            "input": {
                # Account will be added in the test create functions
                "financeInvoiceGroup": to_global_id('FinanceInvoiceGroupNode', 100),
                "summary": "create summary"
            }
        }

        self.variables_update = {
            "input": {
              "summary": "create summary",
              "relationCompany": "ACME INC.",
              "relationCompanyRegistration": "ACME 4312",
              "relationCompanyTaxRegistration": "ACME TAX 99",
              "relationContactName": "Contact person",
              "relationAddress": "Street 1",
              "relationPostcode": "1233434 545",
              "relationCity": "Amsterdam",
              "relationCountry": "NL",
              "invoiceNumber": "INVT0001",
              "dateSent": "2019-01-03",
              "dateDue": "2019-02-28",
              "status": "SENT",
              "terms": "Terms go there",
              "footer": "Footer here",
              "note": "Notes here"
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
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['quantity'], invoice_item.quantity)
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['price'], invoice_item.price)
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['financeTaxRate']['id'], 
          to_global_id('FinanceTaxRateNode', invoice_item.finance_tax_rate.id))
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['subtotal'], round(invoice_item.subtotal, 2))
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['tax'], round(invoice_item.tax, 2))
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['total'], round(invoice_item.total, 2))
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['financeGlaccount']['id'], 
          to_global_id('FinanceGLAccountNode', invoice_item.finance_glaccount.id))
        self.assertEqual(data['financeInvoiceItems']['edges'][0]['node']['financeCostcenter']['id'], 
          to_global_id('FinanceCostCenterNode', invoice_item.finance_costcenter.id))


    def test_query_permision_denied(self):
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


    def test_query_permision_granted(self):
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



    # def test_create_invoice(self):
    #     """ Create an account invoice """
    #     query = self.invoice_create_mutation

    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')

    #     # Get invoice
    #     rid = get_rid(data['createFinanceInvoice']['financeInvoice']['id'])
    #     invoice = models.FinanceInvoice.objects.get(pk=rid.id)

    #     self.assertEqual(
    #         data['createFinanceInvoice']['financeInvoice']['account']['id'], 
    #         variables['input']['account']
    #     )
    #     self.assertEqual(
    #         data['createFinanceInvoice']['financeInvoice']['financeInvoiceGroup']['id'], 
    #         variables['input']['financeInvoiceGroup']
    #     )
    #     self.assertEqual(data['createFinanceInvoice']['financeInvoice']['dateSent'], str(timezone.now().date()))
    #     self.assertEqual(data['createFinanceInvoice']['financeInvoice']['dateDue'], 
    #       str(timezone.now().date() + datetime.timedelta(days=invoice.finance_invoice_group.due_after_days))
    #     )
    #     self.assertEqual(data['createFinanceInvoice']['financeInvoice']['summary'], variables['input']['summary'])


    # def test_create_invoice_anon_user(self):
    #     """ Don't allow creating account invoices for non-logged in users """
    #     query = self.invoice_create_mutation
        
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_create_location_permission_granted(self):
    #     """ Allow creating invoices for users with permissions """
    #     query = self.invoice_create_mutation

    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)

    #     # Create regular user
    #     user = account
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['createFinanceInvoice']['financeInvoice']['account']['id'], 
    #         variables['input']['account']
    #     )


    # def test_create_invoice_permission_denied(self):
    #     """ Check create invoice permission denied error message """
    #     query = self.invoice_create_mutation

    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)

    #     # Create regular user
    #     user = account

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_update_invoice(self):
    #     """ Update a invoice """
    #     query = self.invoice_update_mutation

    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )

    #     data = executed.get('data')

    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCompany'], variables['input']['relationCompany'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCompanyRegistration'], variables['input']['relationCompanyRegistration'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationContactName'], variables['input']['relationContactName'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationAddress'], variables['input']['relationAddress'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationPostcode'], variables['input']['relationPostcode'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCity'], variables['input']['relationCity'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCountry'], variables['input']['relationCountry'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['invoiceNumber'], variables['input']['invoiceNumber'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateSent'], variables['input']['dateSent'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateDue'], variables['input']['dateDue'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['status'], variables['input']['status'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['summary'], variables['input']['summary'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['terms'], variables['input']['terms'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['footer'], variables['input']['footer'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['note'], variables['input']['note'])


    # def test_update_invoice_anon_user(self):
    #     """ Don't allow updating invoices for non-logged in users """
    #     query = self.invoice_update_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_invoice_permission_granted(self):
    #     """ Allow updating invoices for users with permissions """
    #     query = self.invoice_update_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

    #     user = invoice_item.finance_invoice.account
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateSent'], variables['input']['dateSent'])


    # def test_update_invoice_permission_denied(self):
    #     """ Check update invoice permission denied error message """
    #     query = self.invoice_update_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

    #     user = invoice_item.finance_invoice.account

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_delete_invoice(self):
    #     """ Delete an account invoice """
    #     query = self.invoice_delete_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['deleteFinanceInvoice']['ok'], True)


    # def test_delete_invoice_anon_user(self):
    #     """ Delete invoice denied for anon user """
    #     query = self.invoice_delete_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_delete_invoice_permission_granted(self):
    #     """ Allow deleting invoices for users with permissions """
    #     query = self.invoice_delete_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)

    #     # Give permissions
    #     user = invoice_item.finance_invoice.account
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['deleteFinanceInvoice']['ok'], True)


    # def test_delete_invoice_permission_denied(self):
    #     """ Check delete invoice permission denied error message """
    #     query = self.invoice_delete_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceItemNode', invoice_item.id)
        
    #     user = invoice_item.finance_invoice.account

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')

