# from graphql.error.located_error import GraphQLLocatedError
import datetime
import graphql

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils import timezone
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema
from ..modules.finance_tools import display_float_as_amount
from ..modules.validity_tools import display_validity_unit

from graphql_relay import to_global_id


class GQLInsightRevenue(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_insightrevenue'

        finance_invoice_item = f.FinanceInvoiceItemFactory.create()
        finance_invoice = finance_invoice_item.finance_invoice
        finance_invoice.date_sent = datetime.date(2020, 1 , 1)
        finance_invoice.status = 'SENT'
        finance_invoice.update_amounts()
        finance_invoice.save()
        self.finance_invoice = finance_invoice


        self.variables_query = {
            'year': 2020
        }   

        self.query_revenue_total = '''
  query InsightRevenueTotal($year: Int!) {
    insightRevenueTotal(year: $year) {
      description
      data
      year
    }
  }
'''

        self.query_revenue_subtotal = '''
  query InsightRevenueSubTotal($year: Int!) {
    insightRevenueSubtotal(year: $year) {
      description
      data
      year
    }
  }
'''
        self.query_revenue_tax = '''
  query InsightRevenueTax($year: Int!) {
    insightRevenueTax(year: $year) {
      description
      data
      year
    }
  }
'''


    def tearDown(self):
        # This is run after every test
        pass


    def test_query_revenue_total(self):
        """ Query total revenue for a year """
        query = self.query_revenue_total

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightRevenueTotal']['description'], 'revenue_total')
        self.assertEqual(data['insightRevenueTotal']['year'], self.variables_query['year'])
        self.assertEqual(data['insightRevenueTotal']['data'][0], format(self.finance_invoice.total, ".2f"))
        self.assertEqual(data['insightRevenueTotal']['data'][1], '0')
        self.assertEqual(data['insightRevenueTotal']['data'][2], '0')
        self.assertEqual(data['insightRevenueTotal']['data'][3], '0')
        self.assertEqual(data['insightRevenueTotal']['data'][4], '0')
        self.assertEqual(data['insightRevenueTotal']['data'][5], '0')
        self.assertEqual(data['insightRevenueTotal']['data'][6], '0')
        self.assertEqual(data['insightRevenueTotal']['data'][7], '0')
        self.assertEqual(data['insightRevenueTotal']['data'][8], '0')
        self.assertEqual(data['insightRevenueTotal']['data'][9], '0')
        self.assertEqual(data['insightRevenueTotal']['data'][10], '0')
        self.assertEqual(data['insightRevenueTotal']['data'][11], '0')


    def test_query_total_permission_denied(self):
        """ Query total revenue for a year - check permission denied """
        query = self.query_revenue_total

        # Create regular user
        user = self.finance_invoice.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_total_permission_granted(self):
        """ Query total revenue for a year - check permission granted """
        query = self.query_revenue_total

        # Create regular user
        user = self.finance_invoice.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightRevenueTotal']['year'], self.variables_query['year'])


    def test_query_total_anon_user(self):
        """ Query total revenue for a year - anon user """
        query = self.query_revenue_total

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_revenue_subtotal(self):
        """ Query subtotal revenue for a year """
        query = self.query_revenue_subtotal

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightRevenueSubtotal']['description'], 'revenue_subtotal')
        self.assertEqual(data['insightRevenueSubtotal']['year'], self.variables_query['year'])
        self.assertEqual(data['insightRevenueSubtotal']['data'][0], format(self.finance_invoice.subtotal, ".2f"))
        self.assertEqual(data['insightRevenueSubtotal']['data'][1], '0')
        self.assertEqual(data['insightRevenueSubtotal']['data'][2], '0')
        self.assertEqual(data['insightRevenueSubtotal']['data'][3], '0')
        self.assertEqual(data['insightRevenueSubtotal']['data'][4], '0')
        self.assertEqual(data['insightRevenueSubtotal']['data'][5], '0')
        self.assertEqual(data['insightRevenueSubtotal']['data'][6], '0')
        self.assertEqual(data['insightRevenueSubtotal']['data'][7], '0')
        self.assertEqual(data['insightRevenueSubtotal']['data'][8], '0')
        self.assertEqual(data['insightRevenueSubtotal']['data'][9], '0')
        self.assertEqual(data['insightRevenueSubtotal']['data'][10], '0')
        self.assertEqual(data['insightRevenueSubtotal']['data'][11], '0')


    def test_query_subtotal_permission_denied(self):
        """ Query subtotal revenue for a year - check permission denied """
        query = self.query_revenue_subtotal

        # Create regular user
        user = self.finance_invoice.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_subtotal_permission_granted(self):
        """ Query subtotal revenue for a year - greant view permission """
        query = self.query_revenue_subtotal

        # Create regular user
        user = self.finance_invoice.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightRevenueSubtotal']['year'], self.variables_query['year'])


    def test_query_subtotal_anon_user(self):
        """ Query subtotal revenue for a year - anon user """
        query = self.query_revenue_subtotal

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_revenue_tax(self):
        """ Query revenue tax for a year """
        query = self.query_revenue_tax

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightRevenueTax']['description'], 'revenue_tax')
        self.assertEqual(data['insightRevenueTax']['year'], self.variables_query['year'])
        self.assertEqual(data['insightRevenueTax']['data'][0], format(self.finance_invoice.tax, ".2f"))
        self.assertEqual(data['insightRevenueTax']['data'][1], '0')
        self.assertEqual(data['insightRevenueTax']['data'][2], '0')
        self.assertEqual(data['insightRevenueTax']['data'][3], '0')
        self.assertEqual(data['insightRevenueTax']['data'][4], '0')
        self.assertEqual(data['insightRevenueTax']['data'][5], '0')
        self.assertEqual(data['insightRevenueTax']['data'][6], '0')
        self.assertEqual(data['insightRevenueTax']['data'][7], '0')
        self.assertEqual(data['insightRevenueTax']['data'][8], '0')
        self.assertEqual(data['insightRevenueTax']['data'][9], '0')
        self.assertEqual(data['insightRevenueTax']['data'][10], '0')
        self.assertEqual(data['insightRevenueTax']['data'][11], '0')


    def test_query_tax_permission_denied(self):
        """ Query revenue tax for a year - check permission denied """
        query = self.query_revenue_tax

        # Create regular user
        user = self.finance_invoice.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_tax_permission_granted(self):
        """ Query revenue tax for a year - greant view permission """
        query = self.query_revenue_tax

        # Create regular user
        user = self.finance_invoice.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightRevenueTax']['year'], self.variables_query['year'])


    def test_query_tax_anon_user(self):
        """ Query revenue tax for a year - anon user """
        query = self.query_revenue_tax

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
