# from graphql.error.located_error import GraphQLLocatedError
from django.contrib.auth.models import Permission
from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query



class GQLInsightSubscriptions(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        # self.organization_membership = f.OrganizationMembershipFactory.create()

        self.variables_query = {
            'year': 2019
        }   

        self.query_subscriptions = '''
  query InsightAccountSubscriptions($year: Int!) {
    insightAccountSubscriptions(year: $year) {
      year
      months {
        month
        sold
        active
        paused
        blocked
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass
    
    def test_query(self):
        """ Query list of subscriptions """
        query = self.query_subscriptions
        account_subscription = f.AccountSubscriptionFactory.create()

        # There should be a pause counted in January & February
        account_subscription_pause = f.AccountSubscriptionPauseFactory.create(
            account_subscription=account_subscription,
            date_end='2019-02-02'
        )

        # There should be a block counted in January & February
        account_subscription_block = f.AccountSubscriptionBlockFactory.create(
            account_subscription=account_subscription,
            date_end='2019-02-02'
        )

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightAccountSubscriptions']['year'], self.variables_query['year'])
        # January
        self.assertEqual(data['insightAccountSubscriptions']['months'][0]['month'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][0]['active'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][0]['sold'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][0]['paused'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][0]['blocked'], 1)
        # February
        self.assertEqual(data['insightAccountSubscriptions']['months'][1]['month'], 2)
        self.assertEqual(data['insightAccountSubscriptions']['months'][1]['active'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][1]['sold'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][1]['paused'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][1]['blocked'], 1)
        # March
        self.assertEqual(data['insightAccountSubscriptions']['months'][2]['month'], 3)
        self.assertEqual(data['insightAccountSubscriptions']['months'][2]['active'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][2]['sold'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][2]['paused'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][2]['blocked'], 0)
        # April
        self.assertEqual(data['insightAccountSubscriptions']['months'][3]['month'], 4)
        self.assertEqual(data['insightAccountSubscriptions']['months'][3]['active'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][3]['sold'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][3]['paused'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][3]['blocked'], 0)
        # May
        self.assertEqual(data['insightAccountSubscriptions']['months'][4]['month'], 5)
        self.assertEqual(data['insightAccountSubscriptions']['months'][4]['active'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][4]['sold'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][4]['paused'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][4]['blocked'], 0)
        # June
        self.assertEqual(data['insightAccountSubscriptions']['months'][5]['month'], 6)
        self.assertEqual(data['insightAccountSubscriptions']['months'][5]['active'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][5]['sold'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][5]['paused'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][5]['blocked'], 0)
        # July
        self.assertEqual(data['insightAccountSubscriptions']['months'][6]['month'], 7)
        self.assertEqual(data['insightAccountSubscriptions']['months'][6]['active'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][6]['sold'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][6]['paused'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][6]['blocked'], 0)
        # August
        self.assertEqual(data['insightAccountSubscriptions']['months'][7]['month'], 8)
        self.assertEqual(data['insightAccountSubscriptions']['months'][7]['active'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][7]['sold'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][7]['paused'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][7]['blocked'], 0)
        # September
        self.assertEqual(data['insightAccountSubscriptions']['months'][8]['month'], 9)
        self.assertEqual(data['insightAccountSubscriptions']['months'][8]['active'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][8]['sold'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][8]['paused'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][8]['blocked'], 0)
        # October
        self.assertEqual(data['insightAccountSubscriptions']['months'][9]['month'], 10)
        self.assertEqual(data['insightAccountSubscriptions']['months'][9]['active'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][9]['sold'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][9]['paused'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][9]['blocked'], 0)
        # November
        self.assertEqual(data['insightAccountSubscriptions']['months'][10]['month'], 11)
        self.assertEqual(data['insightAccountSubscriptions']['months'][10]['active'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][10]['sold'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][10]['paused'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][10]['blocked'], 0)
        # December
        self.assertEqual(data['insightAccountSubscriptions']['months'][11]['month'], 12)
        self.assertEqual(data['insightAccountSubscriptions']['months'][11]['active'], 1)
        self.assertEqual(data['insightAccountSubscriptions']['months'][11]['sold'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][11]['paused'], 0)
        self.assertEqual(data['insightAccountSubscriptions']['months'][11]['blocked'], 0)

    def test_query_permission_denied(self):
        """ Query list of subscriptions - check permission denied """
        query = self.query_subscriptions
        subscription = f.AccountSubscriptionFactory.create()

        # Create regular user
        user = subscription.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of subscriptions with view permission """
        query = self.query_subscriptions
        subscription = f.AccountSubscriptionFactory.create()

        # Create regular user
        user = subscription.account
        permission = Permission.objects.get(codename='view_insightsubscriptions')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightAccountSubscriptions']['year'], self.variables_query['year'])

    def test_query_anon_user(self):
        """ Query list of subscriptions - anon user """
        query = self.query_subscriptions
        subscription = f.AccountSubscriptionFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
