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


class GQLInsightRevenueOther(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_insightrevenue'

        finance_invoice_item = f.FinanceInvoiceItemFactory.create()
        finance_invoice = finance_invoice_item.finance_invoice
        finance_invoice.date_sent = datetime.date(2020, 1, 1)
        finance_invoice.status = 'SENT'
        finance_invoice.update_amounts()
        finance_invoice.save()
        self.finance_invoice = finance_invoice

        self.variables_query = {
            'year': 2020
        }   

        self.query_revenue_total = '''
  query InsightRevenueTotalOther($year: Int!) {
    insightRevenueTotalOther(year: $year) {
      description
      data
      year
    }
  }
'''

        self.query_revenue_subtotal = '''
  query InsightRevenueSubTotalOther($year: Int!) {
    insightRevenueSubtotalOther(year: $year) {
      description
      data
      year
    }
  }
'''
        self.query_revenue_tax = '''
  query InsightRevenueTaxOther($year: Int!) {
    insightRevenueTaxOther(year: $year) {
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
        """ Query total revenue for other for a year """
        query = self.query_revenue_total

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightRevenueTotalOther']['description'], 'revenue_total_other')
        self.assertEqual(data['insightRevenueTotalOther']['year'], self.variables_query['year'])
        self.assertEqual(data['insightRevenueTotalOther']['data'][0], format(self.finance_invoice.total, ".2f"))
        self.assertEqual(data['insightRevenueTotalOther']['data'][1], '0')
        self.assertEqual(data['insightRevenueTotalOther']['data'][2], '0')
        self.assertEqual(data['insightRevenueTotalOther']['data'][3], '0')
        self.assertEqual(data['insightRevenueTotalOther']['data'][4], '0')
        self.assertEqual(data['insightRevenueTotalOther']['data'][5], '0')
        self.assertEqual(data['insightRevenueTotalOther']['data'][6], '0')
        self.assertEqual(data['insightRevenueTotalOther']['data'][7], '0')
        self.assertEqual(data['insightRevenueTotalOther']['data'][8], '0')
        self.assertEqual(data['insightRevenueTotalOther']['data'][9], '0')
        self.assertEqual(data['insightRevenueTotalOther']['data'][10], '0')
        self.assertEqual(data['insightRevenueTotalOther']['data'][11], '0')

    def test_query_total_permission_denied(self):
        """ Query total revenue for otherfor a year - check permission denied """
        query = self.query_revenue_total

        # Create regular user
        user = self.finance_invoice.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_total_permission_granted(self):
        """ Query total revenue for other for a year - check permission granted """
        query = self.query_revenue_total

        # Create regular user
        user = self.finance_invoice.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightRevenueTotalOther']['year'], self.variables_query['year'])

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

        self.assertEqual(data['insightRevenueSubtotalOther']['description'], 'revenue_subtotal_other')
        self.assertEqual(data['insightRevenueSubtotalOther']['year'], self.variables_query['year'])
        self.assertEqual(data['insightRevenueSubtotalOther']['data'][0], format(self.finance_invoice.subtotal, ".2f"))
        self.assertEqual(data['insightRevenueSubtotalOther']['data'][1], '0')
        self.assertEqual(data['insightRevenueSubtotalOther']['data'][2], '0')
        self.assertEqual(data['insightRevenueSubtotalOther']['data'][3], '0')
        self.assertEqual(data['insightRevenueSubtotalOther']['data'][4], '0')
        self.assertEqual(data['insightRevenueSubtotalOther']['data'][5], '0')
        self.assertEqual(data['insightRevenueSubtotalOther']['data'][6], '0')
        self.assertEqual(data['insightRevenueSubtotalOther']['data'][7], '0')
        self.assertEqual(data['insightRevenueSubtotalOther']['data'][8], '0')
        self.assertEqual(data['insightRevenueSubtotalOther']['data'][9], '0')
        self.assertEqual(data['insightRevenueSubtotalOther']['data'][10], '0')
        self.assertEqual(data['insightRevenueSubtotalOther']['data'][11], '0')

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

        self.assertEqual(data['insightRevenueSubtotalOther']['year'], self.variables_query['year'])

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

        self.assertEqual(data['insightRevenueTaxOther']['description'], 'revenue_tax_other')
        self.assertEqual(data['insightRevenueTaxOther']['year'], self.variables_query['year'])
        self.assertEqual(data['insightRevenueTaxOther']['data'][0], format(self.finance_invoice.tax, ".2f"))
        self.assertEqual(data['insightRevenueTaxOther']['data'][1], '0')
        self.assertEqual(data['insightRevenueTaxOther']['data'][2], '0')
        self.assertEqual(data['insightRevenueTaxOther']['data'][3], '0')
        self.assertEqual(data['insightRevenueTaxOther']['data'][4], '0')
        self.assertEqual(data['insightRevenueTaxOther']['data'][5], '0')
        self.assertEqual(data['insightRevenueTaxOther']['data'][6], '0')
        self.assertEqual(data['insightRevenueTaxOther']['data'][7], '0')
        self.assertEqual(data['insightRevenueTaxOther']['data'][8], '0')
        self.assertEqual(data['insightRevenueTaxOther']['data'][9], '0')
        self.assertEqual(data['insightRevenueTaxOther']['data'][10], '0')
        self.assertEqual(data['insightRevenueTaxOther']['data'][11], '0')

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

        self.assertEqual(data['insightRevenueTaxOther']['year'], self.variables_query['year'])

    def test_query_tax_anon_user(self):
        """ Query revenue tax for a year - anon user """
        query = self.query_revenue_tax

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
