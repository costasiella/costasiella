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



class GQLFinanceInvoicePayment(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['finance_invoice_group.json', 'finance_payment_methods.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financeinvoicepayment'
        self.permission_add = 'add_financeinvoicepayment'
        self.permission_change = 'change_financeinvoicepayment'
        self.permission_delete = 'delete_financeinvoicepayment'

        self.finance_payment_method = models.FinancePaymentMethod.objects.get(id=102)

        self.variables_create = {
            "input": {
              "date": datetime.date(2019, 1, 1),
              "amount": "12",
              "note": "test create note",
              # Fixed value for wire transfer (from fixtures)
              "financePaymentMethod": to_global_id("FinancePaymentMethodNode", 102) 
            }
        }

        self.variables_update = {
            "input": {
              "date": datetime.date(2019, 1, 1),
              "amount": "12",
              "note": "test update note",
              # Fixed value for wire transfer (from fixtures)
              "financePaymentMethod": to_global_id("FinancePaymentMethodNode", 103) 
            }
        }

        self.invoice_payments_query = '''
  query FinanceInvoicesPayments($financeInvoice: ID!) {
    financeInvoicePayments(first: 100, financeInvoice: $financeInvoice) {
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
          date
          amount
          note
          financePaymentMethod {
            id
            name
          }
        }
      }
    }
  }
'''

        self.invoice_payment_query = '''
  query FinanceInvoicePayment($id: ID!) {
    financeInvoicePayment(id:$id) {
      id
      financeInvoice {
        id
      }
      date
      amount
      note
      financePaymentMethod {
        id
        name
      }
    }
  }
'''

        self.invoice_payment_create_mutation = ''' 
  mutation CreateFinanceInvoicePayment($input:CreateFinanceInvoicePaymentInput!) {
    createFinanceInvoicePayment(input:$input) {
      financeInvoicePayment {
        id
        financeInvoice {
          id
        }
        date
        amount
        note
        financePaymentMethod {
          id
          name
        }
      } 
    }
  }
'''

        self.invoice_payment_update_mutation = '''
  mutation UpdateFinanceInvoicePayment($input:UpdateFinanceInvoicePaymentInput!) {
    updateFinanceInvoicePayment(input:$input) {
      financeInvoicePayment {
        id
        financeInvoice {
          id
        }
        date
        amount
        note
        financePaymentMethod {
          id
          name
        }
      }
    }
  }
'''

        self.invoice_payment_delete_mutation = '''
  mutation DeleteFinanceInvoicePayment($input: DeleteFinanceInvoicePaymentInput!) {
    deleteFinanceInvoicePayment(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account invoice payments """
        query = self.invoice_payments_query
        invoice_payment = f.FinanceInvoicePaymentFactory.create()

        variables = {
          "financeInvoice": to_global_id('FinanceInvoiceNode', invoice_payment.finance_invoice.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['financeInvoicePayments']['edges'][0]['node']['id'],
          to_global_id('FinanceInvoicePaymentNode', invoice_payment.id)
        )
        self.assertEqual(
          data['financeInvoicePayments']['edges'][0]['node']['financeInvoice']['id'],
          to_global_id('FinanceInvoiceNode', invoice_payment.finance_invoice.id)
        )
        self.assertEqual(data['financeInvoicePayments']['edges'][0]['node']['date'], str(invoice_payment.date))
        self.assertEqual(data['financeInvoicePayments']['edges'][0]['node']['amount'],
                         format(invoice_payment.amount, ".2f"))
        self.assertEqual(data['financeInvoicePayments']['edges'][0]['node']['note'], invoice_payment.note)
        self.assertEqual(
          data['financeInvoicePayments']['edges'][0]['node']['financePaymentMethod']['id'], 
          to_global_id('FinancePaymentMethodNode', invoice_payment.finance_payment_method.id)
        )

    def test_query_permission_denied(self):
        """ Query list of account invoice payments - check permission denied """
        query = self.invoice_payments_query
        invoice_payment = f.FinanceInvoicePaymentFactory.create()

        variables = {
          "financeInvoice": to_global_id('FinanceInvoicePaymentNode', invoice_payment.finance_invoice.pk)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=invoice_payment.finance_invoice.account.id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of account invoice payments with view permission """
        query = self.invoice_payments_query
        invoice_payment = f.FinanceInvoicePaymentFactory.create()

        variables = {
          "financeInvoice": to_global_id('FinanceInvoicePaymentNode', invoice_payment.finance_invoice.pk)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=invoice_payment.finance_invoice.account.id)
        permission = Permission.objects.get(codename='view_financeinvoicepayment')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List selected invoice payments
        self.assertEqual(
          data['financeInvoicePayments']['edges'][0]['node']['id'],
          to_global_id('FinanceInvoicePaymentNode', invoice_payment.id)
        )

    def test_query_anon_user(self):
        """ Query list of account invoice payments - anon user """
        query = self.invoice_payments_query
        invoice_payment = f.FinanceInvoicePaymentFactory.create()

        variables = {
          "financeInvoice": to_global_id('FinanceInvoicePaymentNode', invoice_payment.finance_invoice.pk)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account invoice payment as admin """   
        invoice_payment = f.FinanceInvoicePaymentFactory.create()
        
        variables = {
            "id": to_global_id("FinanceInvoicePaymentNode", invoice_payment.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.invoice_payment_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['financeInvoicePayment']['id'],
            to_global_id('FinanceInvoicePaymentNode', invoice_payment.id)
        )
        self.assertEqual(
            data['financeInvoicePayment']['financeInvoice']['id'],
            to_global_id('FinanceInvoiceNode', invoice_payment.finance_invoice.id)
        )
        self.assertEqual(data['financeInvoicePayment']['date'], str(invoice_payment.date))
        self.assertEqual(data['financeInvoicePayment']['amount'], format(invoice_payment.amount, ".2f"))
        self.assertEqual(data['financeInvoicePayment']['note'], invoice_payment.note)
        self.assertEqual(
            data['financeInvoicePayment']['financePaymentMethod']['id'],
            to_global_id('FinancePaymentMethodNode', invoice_payment.finance_payment_method.id)
        )

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account invoice """   
        invoice_payment = f.FinanceInvoicePaymentFactory.create()
        
        variables = {
            "id": to_global_id("FinanceInvoicePaymentNode", invoice_payment.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.invoice_payment_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        invoice_payment = f.FinanceInvoicePaymentFactory.create()
        user = invoice_payment.finance_invoice.account

        variables = {
            "id": to_global_id("FinanceInvoicePaymentNode", invoice_payment.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.invoice_payment_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        invoice_payment = f.FinanceInvoicePaymentFactory.create()
        user = invoice_payment.finance_invoice.account
        permission = Permission.objects.get(codename='view_financeinvoicepayment')
        user.user_permissions.add(permission)
        user.save()
        
        variables = {
            "id": to_global_id("FinanceInvoicePaymentNode", invoice_payment.id),
        }

        # Now query single invoice and check   
        executed = execute_test_client_api_query(self.invoice_payment_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['financeInvoicePayment']['id'],
            to_global_id('FinanceInvoicePaymentNode', invoice_payment.id)
        )

    def test_create_invoice_payment(self):
        """ Create an invoice payment """
        query = self.invoice_payment_create_mutation

        invoice_item = f.FinanceInvoiceItemFactory.create()
        invoice = invoice_item.finance_invoice
        invoice.total = self.variables_create['input']['amount']
        invoice.save()

        variables = self.variables_create
        variables['input']['financeInvoice'] = to_global_id('FinanceInvoiceNode', invoice.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        # Get payment
        rid = get_rid(data['createFinanceInvoicePayment']['financeInvoicePayment']['id'])
        invoice_payment = models.FinanceInvoicePayment.objects.get(pk=rid.id)

        self.assertEqual(
            data['createFinanceInvoicePayment']['financeInvoicePayment']['financeInvoice']['id'], 
            variables['input']['financeInvoice']
        )
        self.assertEqual(
            data['createFinanceInvoicePayment']['financeInvoicePayment']['date'], 
            str(variables['input']['date'])
        )
        self.assertEqual(
            data['createFinanceInvoicePayment']['financeInvoicePayment']['amount'], 
            variables['input']['amount']
        )
        self.assertEqual(
            data['createFinanceInvoicePayment']['financeInvoicePayment']['financePaymentMethod']['id'], 
            variables['input']['financePaymentMethod']
        )

        # Check whether the status has changed to paid
        invoice = models.FinanceInvoice.objects.get(id=invoice.id)
        self.assertEqual(invoice.status, "PAID")

    def test_create_invoice_payment_anon_user(self):
        """ Don't allow creating invoice payments for non-logged in users """
        query = self.invoice_payment_create_mutation

        invoice_item = f.FinanceInvoiceItemFactory.create()
        invoice = invoice_item.finance_invoice
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

    def test_create_invoice_payment_permission_granted(self):
        """ Allow creating invoice payments for users with permissions """
        query = self.invoice_payment_create_mutation

        invoice_item = f.FinanceInvoiceItemFactory.create()
        invoice = invoice_item.finance_invoice
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
            data['createFinanceInvoicePayment']['financeInvoicePayment']['financeInvoice']['id'], 
            variables['input']['financeInvoice']
        )

    def test_create_invoice_payment_permission_denied(self):
        """ Check create invoice payment permission denied error message """
        query = self.invoice_payment_create_mutation

        invoice_item = f.FinanceInvoiceItemFactory.create()
        invoice = invoice_item.finance_invoice
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

    def test_update_invoice_payment(self):
        """ Update an invoice payment """
        query = self.invoice_payment_update_mutation

        invoice_payment = f.FinanceInvoicePaymentFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoicePaymentNode', invoice_payment.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['updateFinanceInvoicePayment']['financeInvoicePayment']['date'], str(variables['input']['date']))
        self.assertEqual(data['updateFinanceInvoicePayment']['financeInvoicePayment']['amount'], variables['input']['amount'])
        self.assertEqual(data['updateFinanceInvoicePayment']['financeInvoicePayment']['note'], variables['input']['note'])
        self.assertEqual(
          data['updateFinanceInvoicePayment']['financeInvoicePayment']['financePaymentMethod']['id'], 
          variables['input']['financePaymentMethod']
        )

    def test_update_invoice_payment_anon_user(self):
        """ Don't allow updating invoice payments for non-logged in users """
        query = self.invoice_payment_update_mutation

        invoice_payment = f.FinanceInvoicePaymentFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoicePaymentNode', invoice_payment.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_invoice_payment_permission_granted(self):
        """ Allow updating invoice payments for users with permissions """
        query = self.invoice_payment_update_mutation

        invoice_payment = f.FinanceInvoicePaymentFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoicePaymentNode', invoice_payment.id)

        user = invoice_payment.finance_invoice.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinanceInvoicePayment']['financeInvoicePayment']['note'], variables['input']['note'])

    def test_update_invoice_payment_permission_denied(self):
        """ Check update invoice payment permission denied error message """
        query = self.invoice_payment_update_mutation

        invoice_payment = f.FinanceInvoicePaymentFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoicePaymentNode', invoice_payment.id)

        user = invoice_payment.finance_invoice.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_invoice_payment(self):
        """ Delete an account invoice payment """
        query = self.invoice_payment_delete_mutation
        invoice_payment = f.FinanceInvoicePaymentFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoicePaymentNode', invoice_payment.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceInvoicePayment']['ok'], True)

    def test_delete_invoice_payment_anon_user(self):
        """ Delete invoice denied for anon user """
        query = self.invoice_payment_delete_mutation
        invoice_payment = f.FinanceInvoicePaymentFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoicePaymentNode', invoice_payment.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_invoice_payment_permission_granted(self):
        """ Allow deleting invoices for users with permissions """
        query = self.invoice_payment_delete_mutation
        invoice_payment = f.FinanceInvoicePaymentFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoicePaymentNode', invoice_payment.id)

        # Give permissions
        user = invoice_payment.finance_invoice.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceInvoicePayment']['ok'], True)

    def test_delete_invoice_payment_permission_denied(self):
        """ Check delete invoice permission denied error message """
        query = self.invoice_payment_delete_mutation
        invoice_payment = f.FinanceInvoicePaymentFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoicePaymentNode', invoice_payment.id)
        
        user = invoice_payment.finance_invoice.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
