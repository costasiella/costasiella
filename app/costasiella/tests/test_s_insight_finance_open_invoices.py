# from graphql.error.located_error import GraphQLLocatedError
import datetime
import os
from django.contrib.auth.models import Permission
from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query

from graphql_relay import to_global_id


class GQLInsightRevenue(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_insightfinanceinvoicesopenondate'

        finance_invoice_item = f.FinanceInvoiceItemFactory.create()
        finance_invoice = finance_invoice_item.finance_invoice
        finance_invoice.date_sent = datetime.date(2020, 1, 1)
        finance_invoice.status = 'SENT'
        finance_invoice.update_amounts()
        finance_invoice.save()
        self.finance_invoice = finance_invoice
        # self.finance_taxrate = finance_invoice_item.finance_tax_rate

        self.variables_query = {
            "date": "2020-01-01",
        }

        self.variables_query_no_data = {
            "date": "2019-12-31",
        }

        self.query_open_invoices = '''
  query InsightFinanceOpenInvoices($date: Date!) {
    insightFinanceOpenInvoices(date:$date) {
      date
      totalOpenOnDate
      financeInvoices {
        id
        invoiceNumber
        status
        dateSent
        total
        paid
        balance
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query_open_invoices_and_total_balance(self):
        """ Query open invoices for a given date """
        query = self.query_open_invoices

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightFinanceOpenInvoices']['date'], self.variables_query['date'])
        self.assertEqual(data['insightFinanceOpenInvoices']['totalOpenOnDate'],
                         format(self.finance_invoice.balance, ".2f"))
        self.assertEqual(data['insightFinanceOpenInvoices']['financeInvoices'][0]['id'],
                         to_global_id('FinanceInvoiceNode', self.finance_invoice.id))
        self.assertEqual(data['insightFinanceOpenInvoices']['financeInvoices'][0]['total'],
                         format(self.finance_invoice.total, ".2f"))
        self.assertEqual(data['insightFinanceOpenInvoices']['financeInvoices'][0]['paid'],
                         str(self.finance_invoice.paid))
        self.assertEqual(data['insightFinanceOpenInvoices']['financeInvoices'][0]['balance'],
                         format(self.finance_invoice.balance, ".2f"))


    def test_query_revenue_total_no_data(self):
        """ Query open invoices for a given date - no data """
        query = self.query_open_invoices

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_no_data)
        data = executed.get('data')

        self.assertEqual(data['insightFinanceOpenInvoices']['date'], self.variables_query_no_data['date'])
        self.assertEqual(len(data['insightFinanceOpenInvoices']['financeInvoices']), 0)


    def test_query_total_permission_denied(self):
        """ Query open invoices - check permission denied """
        query = self.query_open_invoices

        # Create regular user
        user = self.finance_invoice.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_total_permission_granted(self):
        """ Query open invoices - check permission granted """
        query = self.query_open_invoices

        # Create regular user
        user = self.finance_invoice.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightFinanceOpenInvoices']['date'], self.variables_query['date'])


    def test_query_total_anon_user(self):
        """ Query open invoices - anon user """
        query = self.query_open_invoices

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
