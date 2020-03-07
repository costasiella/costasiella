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

        self.query_classpasses_active = '''
  query InsightAccountClasspassesActive($year: Int!) {
    insightAccountClasspassesActive(year: $year) {
      description
      data
      year
    }
  }
'''


        self.query_classpasses_sold = '''
  query InsightAccountClasspassesSold($year: Int!) {
    insightAccountClasspassesSold(year: $year) {
      description
      data
      year
    }
  }
'''


    def tearDown(self):
        # This is run after every test
        pass


    def test_query_active(self):
        """ Query list of classpasses """
        query = self.query_classpasses_active
        classpass = f.AccountClasspassFactory.create()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightAccountClasspassesActive']['description'], 'account_classpasses_active')
        self.assertEqual(data['insightAccountClasspassesActive']['year'], self.variables_query['year'])
        self.assertEqual(data['insightAccountClasspassesActive']['data'][0], 1)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][1], 1)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][2], 1)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][3], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][4], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][5], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][6], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][7], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][8], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][9], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][10], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][11], 0)


    def test_query_active_permision_denied(self):
        """ Query list of classpasses - check permission denied """
        query = self.query_classpasses_active
        classpass = f.AccountClasspassFactory.create()

        # Create regular user
        user = classpass.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')
        

    def test_query_active_permision_granted(self):
        """ Query list of classpasses with view permission """
        query = self.query_classpasses_active
        classpass = f.AccountClasspassFactory.create()      

        # Create regular user
        user = classpass.account
        permission = Permission.objects.get(codename='view_insightclasspassesactive')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightAccountClasspassesActive']['year'], self.variables_query['year'])


    def test_query_active_anon_user(self):
        """ Query list of classpasses - anon user """
        query = self.query_classpasses_active
        classpass = f.AccountClasspassFactory.create()  

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')



    def test_query_sold(self):
        """ Query list of classpasses """
        query = self.query_classpasses_sold
        classpass = f.AccountClasspassFactory.create()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        print(executed)

        self.assertEqual(data['insightAccountClasspassesSold']['description'], 'account_classpasses_sold')
        self.assertEqual(data['insightAccountClasspassesSold']['year'], self.variables_query['year'])
        self.assertEqual(data['insightAccountClasspassesSold']['data'][0], 1)
        self.assertEqual(data['insightAccountClasspassesSold']['data'][1], 0)
        self.assertEqual(data['insightAccountClasspassesSold']['data'][2], 0)
        self.assertEqual(data['insightAccountClasspassesSold']['data'][3], 0)
        self.assertEqual(data['insightAccountClasspassesSold']['data'][4], 0)
        self.assertEqual(data['insightAccountClasspassesSold']['data'][5], 0)
        self.assertEqual(data['insightAccountClasspassesSold']['data'][6], 0)
        self.assertEqual(data['insightAccountClasspassesSold']['data'][7], 0)
        self.assertEqual(data['insightAccountClasspassesSold']['data'][8], 0)
        self.assertEqual(data['insightAccountClasspassesSold']['data'][9], 0)
        self.assertEqual(data['insightAccountClasspassesSold']['data'][10], 0)
        self.assertEqual(data['insightAccountClasspassesSold']['data'][11], 0)


    def test_query_permision_denied(self):
        """ Query list of classpasses - check permission denied """
        query = self.query_classpasses_sold
        classpass = f.AccountClasspassFactory.create()

        # Create regular user
        user = classpass.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')
        

    def test_query_permision_granted(self):
        """ Query list of classpasses with view permission """
        query = self.query_classpasses_sold
        classpass = f.AccountClasspassFactory.create()      

        # Create regular user
        user = classpass.account
        permission = Permission.objects.get(codename='view_insightclasspassessold')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightAccountClasspassesSold']['year'], self.variables_query['year'])


    def test_query_anon_user(self):
        """ Query list of classpasses - anon user """
        query = self.query_classpasses_sold
        classpass = f.AccountClasspassFactory.create()  

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

