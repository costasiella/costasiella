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

        self.permission_view = 'view_insightfinancetaxratesummary'

        finance_invoice_item = f.FinanceInvoiceItemFactory.create()
        finance_invoice = finance_invoice_item.finance_invoice
        finance_invoice.date_sent = datetime.date(2020, 1 , 1)
        finance_invoice.status = 'SENT'
        finance_invoice.update_amounts()
        finance_invoice.save()
        self.finance_invoice = finance_invoice
        self.finance_taxrate = finance_invoice_item.finance_tax_rate

        self.variables_query = {
            "dateStart": "2020-01-01",
            "dateEnd": "2020-12-31"
        }

        self.variables_query_no_data = {
            "dateStart": "2022-01-01",
            "dateEnd": "2022-12-31"
        }

        self.query_tax_summary = '''
  query InsightFinanceTaxSummary($dateStart: Date!, $dateEnd: Date!) {
    insightFinanceTaxRateSummary(dateStart:$dateStart, dateEnd: $dateEnd) {
      dateStart
      dateEnd
      data {
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
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query_tax_summary(self):
        """ Query tax rate summary for a given period """
        query = self.query_tax_summary

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightFinanceTaxRateSummary']['dateStart'], self.variables_query['dateStart'])
        self.assertEqual(data['insightFinanceTaxRateSummary']['dateEnd'], self.variables_query['dateEnd'])
        self.assertEqual(data['insightFinanceTaxRateSummary']['data'][0]['financeTaxRate']['name'],
                         self.finance_taxrate.name)
        self.assertEqual(data['insightFinanceTaxRateSummary']['data'][0]['subtotal'],
                         format(self.finance_invoice.subtotal, ".2f"))
        self.assertEqual(data['insightFinanceTaxRateSummary']['data'][0]['tax'],
                         format(self.finance_invoice.tax, ".2f"))


    def test_query_revenue_total_no_data(self):
        """ Query tax rate summary for a given period - no data """
        query = self.query_tax_summary

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_no_data)
        data = executed.get('data')

        self.assertEqual(data['insightFinanceTaxRateSummary']['dateStart'], self.variables_query_no_data['dateStart'])
        self.assertEqual(data['insightFinanceTaxRateSummary']['dateEnd'], self.variables_query_no_data['dateEnd'])
        self.assertEqual(len(data['insightFinanceTaxRateSummary']['data']), 0)


    def test_query_total_permission_denied(self):
        """ Query tax rate summary - check permission denied """
        query = self.query_tax_summary

        # Create regular user
        user = self.finance_invoice.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_total_permission_granted(self):
        """ Query tax rate summary - check permission granted """
        query = self.query_tax_summary

        # Create regular user
        user = self.finance_invoice.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightFinanceTaxRateSummary']['dateStart'], self.variables_query['dateStart'])


    def test_query_total_anon_user(self):
        """ Query tax rate summary - anon user """
        query = self.query_tax_summary

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
    