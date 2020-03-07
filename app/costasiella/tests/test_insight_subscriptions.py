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


class GQLInsightSubscriptions(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_active = 'view_insightsubscriptionsactive'
        self.permission_view_sold = 'view_insightsubscriptionssold'

        # self.organization_membership = f.OrganizationMembershipFactory.create()

        self.variables_query = {
            'year': 2019
        }   

        self.query_subscriptions_active = '''
  query InsightAccountSubscriptionsActive($year: Int!) {
    insightAccountSubscriptionsActive(year: $year) {
      description
      data
      year
    }
  }
'''


        self.query_subscriptions_sold = '''
  query InsightAccountSubscriptionsSold($year: Int!) {
    insightAccountSubscriptionsSold(year: $year) {
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
        """ Query list of subscriptions """
        query = self.query_subscriptions_active
        subscription = f.AccountSubscriptionFactory.create()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightAccountSubscriptionsActive']['description'], 'account_subscriptions_active')
        self.assertEqual(data['insightAccountSubscriptionsActive']['year'], self.variables_query['year'])
        self.assertEqual(data['insightAccountSubscriptionsActive']['data'][0], 1)
        self.assertEqual(data['insightAccountSubscriptionsActive']['data'][1], 1)
        self.assertEqual(data['insightAccountSubscriptionsActive']['data'][2], 1)
        self.assertEqual(data['insightAccountSubscriptionsActive']['data'][3], 1)
        self.assertEqual(data['insightAccountSubscriptionsActive']['data'][4], 1)
        self.assertEqual(data['insightAccountSubscriptionsActive']['data'][5], 1)
        self.assertEqual(data['insightAccountSubscriptionsActive']['data'][6], 1)
        self.assertEqual(data['insightAccountSubscriptionsActive']['data'][7], 1)
        self.assertEqual(data['insightAccountSubscriptionsActive']['data'][8], 1)
        self.assertEqual(data['insightAccountSubscriptionsActive']['data'][9], 1)
        self.assertEqual(data['insightAccountSubscriptionsActive']['data'][10], 1)
        self.assertEqual(data['insightAccountSubscriptionsActive']['data'][11], 1)


    def test_query_active_permision_denied(self):
        """ Query list of subscriptions - check permission denied """
        query = self.query_subscriptions_active
        subscription = f.AccountSubscriptionFactory.create()

        # Create regular user
        user = subscription.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')
        

    def test_query_active_permision_granted(self):
        """ Query list of subscriptions with view permission """
        query = self.query_subscriptions_active
        subscription = f.AccountSubscriptionFactory.create()      

        # Create regular user
        user = subscription.account
        permission = Permission.objects.get(codename='view_insightsubscriptionsactive')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightAccountSubscriptionsActive']['year'], self.variables_query['year'])


    def test_query_active_anon_user(self):
        """ Query list of subscriptions - anon user """
        query = self.query_subscriptions_active
        subscription = f.AccountSubscriptionFactory.create()  

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_sold(self):
        """ Query list of subscriptions """
        query = self.query_subscriptions_sold
        subscription = f.AccountSubscriptionFactory.create()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        print(executed)

        self.assertEqual(data['insightAccountSubscriptionsSold']['description'], 'account_subscriptions_sold')
        self.assertEqual(data['insightAccountSubscriptionsSold']['year'], self.variables_query['year'])
        self.assertEqual(data['insightAccountSubscriptionsSold']['data'][0], 1)
        self.assertEqual(data['insightAccountSubscriptionsSold']['data'][1], 0)
        self.assertEqual(data['insightAccountSubscriptionsSold']['data'][2], 0)
        self.assertEqual(data['insightAccountSubscriptionsSold']['data'][3], 0)
        self.assertEqual(data['insightAccountSubscriptionsSold']['data'][4], 0)
        self.assertEqual(data['insightAccountSubscriptionsSold']['data'][5], 0)
        self.assertEqual(data['insightAccountSubscriptionsSold']['data'][6], 0)
        self.assertEqual(data['insightAccountSubscriptionsSold']['data'][7], 0)
        self.assertEqual(data['insightAccountSubscriptionsSold']['data'][8], 0)
        self.assertEqual(data['insightAccountSubscriptionsSold']['data'][9], 0)
        self.assertEqual(data['insightAccountSubscriptionsSold']['data'][10], 0)
        self.assertEqual(data['insightAccountSubscriptionsSold']['data'][11], 0)


    def test_query_permision_denied(self):
        """ Query list of subscriptions - check permission denied """
        query = self.query_subscriptions_sold
        subscription = f.AccountSubscriptionFactory.create()

        # Create regular user
        user = subscription.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')
        

    def test_query_permision_granted(self):
        """ Query list of subscriptions with view permission """
        query = self.query_subscriptions_sold
        subscription = f.AccountSubscriptionFactory.create()      

        # Create regular user
        user = subscription.account
        permission = Permission.objects.get(codename='view_insightsubscriptionssold')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightAccountSubscriptionsSold']['year'], self.variables_query['year'])


    def test_query_anon_user(self):
        """ Query list of subscriptions - anon user """
        query = self.query_subscriptions_sold
        subscription = f.AccountSubscriptionFactory.create()  

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

