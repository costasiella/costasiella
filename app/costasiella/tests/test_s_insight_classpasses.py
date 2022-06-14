# from graphql.error.located_error import GraphQLLocatedError
import graphql

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
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


class GQLInsightClasspasses(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_active = 'view_insightclasspassesactive'
        self.permission_view_sold = 'view_insightclasspassessold'

        # self.organization_membership = f.OrganizationMembershipFactory.create()

        self.variables_query = {
            'year': 2019
        }   

        self.query_classpasses = '''
    query InsightAccountClasspasses($year: Int!) {
      insightAccountClasspasses(year: $year) {
        year
        months {
          month
          sold
          active
        }
      }
    }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of classpasses """
        query = self.query_classpasses
        classpass = f.AccountClasspassFactory.create()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightAccountClasspasses']['year'], self.variables_query['year'])
        # January
        self.assertEqual(data['insightAccountClasspasses']['months'][0]['month'], 1)
        self.assertEqual(data['insightAccountClasspasses']['months'][0]['active'], 1)
        self.assertEqual(data['insightAccountClasspasses']['months'][0]['sold'], 1)
        # February
        self.assertEqual(data['insightAccountClasspasses']['months'][1]['month'], 2)
        self.assertEqual(data['insightAccountClasspasses']['months'][1]['active'], 1)
        self.assertEqual(data['insightAccountClasspasses']['months'][1]['sold'], 0)
        # March
        self.assertEqual(data['insightAccountClasspasses']['months'][2]['month'], 3)
        self.assertEqual(data['insightAccountClasspasses']['months'][2]['active'], 1)
        self.assertEqual(data['insightAccountClasspasses']['months'][2]['sold'], 0)
        # April
        self.assertEqual(data['insightAccountClasspasses']['months'][3]['month'], 4)
        self.assertEqual(data['insightAccountClasspasses']['months'][3]['active'], 0)
        self.assertEqual(data['insightAccountClasspasses']['months'][3]['sold'], 0)
        # May
        self.assertEqual(data['insightAccountClasspasses']['months'][4]['month'], 5)
        self.assertEqual(data['insightAccountClasspasses']['months'][4]['active'], 0)
        self.assertEqual(data['insightAccountClasspasses']['months'][4]['sold'], 0)
        # June
        self.assertEqual(data['insightAccountClasspasses']['months'][5]['month'], 6)
        self.assertEqual(data['insightAccountClasspasses']['months'][5]['active'], 0)
        self.assertEqual(data['insightAccountClasspasses']['months'][5]['sold'], 0)
        # July
        self.assertEqual(data['insightAccountClasspasses']['months'][6]['month'], 7)
        self.assertEqual(data['insightAccountClasspasses']['months'][6]['active'], 0)
        self.assertEqual(data['insightAccountClasspasses']['months'][6]['sold'], 0)
        # August
        self.assertEqual(data['insightAccountClasspasses']['months'][7]['month'], 8)
        self.assertEqual(data['insightAccountClasspasses']['months'][7]['active'], 0)
        self.assertEqual(data['insightAccountClasspasses']['months'][7]['sold'], 0)
        # September
        self.assertEqual(data['insightAccountClasspasses']['months'][8]['month'], 9)
        self.assertEqual(data['insightAccountClasspasses']['months'][8]['active'], 0)
        self.assertEqual(data['insightAccountClasspasses']['months'][8]['sold'], 0)
        # October
        self.assertEqual(data['insightAccountClasspasses']['months'][9]['month'], 10)
        self.assertEqual(data['insightAccountClasspasses']['months'][9]['active'], 0)
        self.assertEqual(data['insightAccountClasspasses']['months'][9]['sold'], 0)
        # November
        self.assertEqual(data['insightAccountClasspasses']['months'][10]['month'], 11)
        self.assertEqual(data['insightAccountClasspasses']['months'][10]['active'], 0)
        self.assertEqual(data['insightAccountClasspasses']['months'][10]['sold'], 0)
        # December
        self.assertEqual(data['insightAccountClasspasses']['months'][11]['month'], 12)
        self.assertEqual(data['insightAccountClasspasses']['months'][11]['active'], 0)
        self.assertEqual(data['insightAccountClasspasses']['months'][11]['sold'], 0)

    def test_query_permission_denied(self):
        """ Query list of classpasses - check permission denied """
        query = self.query_classpasses
        classpass = f.AccountClasspassFactory.create()

        # Create regular user
        user = classpass.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of classpasses with view permission """
        query = self.query_classpasses
        classpass = f.AccountClasspassFactory.create()

        # Create regular user
        user = classpass.account
        permission = Permission.objects.get(codename='view_insightclasspasses')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightAccountClasspasses']['year'], self.variables_query['year'])

    def test_query_anon_user(self):
        """ Query list of classpasses - anon user """
        query = self.query_classpasses
        classpass = f.AccountClasspassFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
