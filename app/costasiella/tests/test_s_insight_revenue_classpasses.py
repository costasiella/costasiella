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


class GQLInsightRevenueClasspasses(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_insightrevenue'

        finance_invoice_item = f.FinanceInvoiceItemFactory.create()
        finance_invoice_item.account_classpass = f.AccountClasspassFactory.create(
            account=finance_invoice_item.finance_invoice.account
        )
        finance_invoice_item.save()
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
  query InsightRevenueTotalClasspasses($year: Int!) {
    insightRevenueTotalClasspasses(year: $year) {
      description
      data
      year
    }
  }
'''

        self.query_revenue_subtotal = '''
  query InsightRevenueSubTotalClasspasses($year: Int!) {
    insightRevenueSubtotalClasspasses(year: $year) {
      description
      data
      year
    }
  }
'''
        self.query_revenue_tax = '''
  query InsightRevenueTaxClasspasses($year: Int!) {
    insightRevenueTaxClasspasses(year: $year) {
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
        """ Query total revenue for classpasses for a year """
        query = self.query_revenue_total

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightRevenueTotalClasspasses']['description'], 'revenue_total_classpasses')
        self.assertEqual(data['insightRevenueTotalClasspasses']['year'], self.variables_query['year'])
        self.assertEqual(data['insightRevenueTotalClasspasses']['data'][0], format(self.finance_invoice.total, ".2f"))
        self.assertEqual(data['insightRevenueTotalClasspasses']['data'][1], '0')
        self.assertEqual(data['insightRevenueTotalClasspasses']['data'][2], '0')
        self.assertEqual(data['insightRevenueTotalClasspasses']['data'][3], '0')
        self.assertEqual(data['insightRevenueTotalClasspasses']['data'][4], '0')
        self.assertEqual(data['insightRevenueTotalClasspasses']['data'][5], '0')
        self.assertEqual(data['insightRevenueTotalClasspasses']['data'][6], '0')
        self.assertEqual(data['insightRevenueTotalClasspasses']['data'][7], '0')
        self.assertEqual(data['insightRevenueTotalClasspasses']['data'][8], '0')
        self.assertEqual(data['insightRevenueTotalClasspasses']['data'][9], '0')
        self.assertEqual(data['insightRevenueTotalClasspasses']['data'][10], '0')
        self.assertEqual(data['insightRevenueTotalClasspasses']['data'][11], '0')

    def test_query_total_permission_denied(self):
        """ Query total revenue for classpassesfor a year - check permission denied """
        query = self.query_revenue_total

        # Create regular user
        user = self.finance_invoice.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_total_permission_granted(self):
        """ Query total revenue for classpasses for a year - check permission granted """
        query = self.query_revenue_total

        # Create regular user
        user = self.finance_invoice.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightRevenueTotalClasspasses']['year'], self.variables_query['year'])

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

        self.assertEqual(data['insightRevenueSubtotalClasspasses']['description'], 'revenue_subtotal_classpasses')
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['year'], self.variables_query['year'])
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['data'][0], format(self.finance_invoice.subtotal, ".2f"))
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['data'][1], '0')
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['data'][2], '0')
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['data'][3], '0')
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['data'][4], '0')
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['data'][5], '0')
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['data'][6], '0')
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['data'][7], '0')
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['data'][8], '0')
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['data'][9], '0')
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['data'][10], '0')
        self.assertEqual(data['insightRevenueSubtotalClasspasses']['data'][11], '0')

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

        self.assertEqual(data['insightRevenueSubtotalClasspasses']['year'], self.variables_query['year'])

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

        self.assertEqual(data['insightRevenueTaxClasspasses']['description'], 'revenue_tax_classpasses')
        self.assertEqual(data['insightRevenueTaxClasspasses']['year'], self.variables_query['year'])
        self.assertEqual(data['insightRevenueTaxClasspasses']['data'][0], format(self.finance_invoice.tax, ".2f"))
        self.assertEqual(data['insightRevenueTaxClasspasses']['data'][1], '0')
        self.assertEqual(data['insightRevenueTaxClasspasses']['data'][2], '0')
        self.assertEqual(data['insightRevenueTaxClasspasses']['data'][3], '0')
        self.assertEqual(data['insightRevenueTaxClasspasses']['data'][4], '0')
        self.assertEqual(data['insightRevenueTaxClasspasses']['data'][5], '0')
        self.assertEqual(data['insightRevenueTaxClasspasses']['data'][6], '0')
        self.assertEqual(data['insightRevenueTaxClasspasses']['data'][7], '0')
        self.assertEqual(data['insightRevenueTaxClasspasses']['data'][8], '0')
        self.assertEqual(data['insightRevenueTaxClasspasses']['data'][9], '0')
        self.assertEqual(data['insightRevenueTaxClasspasses']['data'][10], '0')
        self.assertEqual(data['insightRevenueTaxClasspasses']['data'][11], '0')

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

        self.assertEqual(data['insightRevenueTaxClasspasses']['year'], self.variables_query['year'])

    def test_query_tax_anon_user(self):
        """ Query revenue tax for a year - anon user """
        query = self.query_revenue_tax

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
