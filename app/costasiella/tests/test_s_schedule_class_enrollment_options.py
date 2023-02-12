# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser, Permission

from . import factories as f
from .tools import next_weekday
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema
from ..modules.gql_tools import get_rid



class GQLScheduleClassBookingOptions(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    """
    """

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleitem'
        self.permission_add = 'add_scheduleitem'
        self.permission_change = 'change_scheduleitem'
        self.permission_delete = 'delete_scheduleitem'

        self.monday = datetime.date(2019, 1, 7)
        self.tuesday = self.monday + datetime.timedelta(days=1)

        # Create subscription
        self.account_subscription = f.AccountSubscriptionFactory.create()
        self.account = self.account_subscription.account

        # Create organization subscriptions group
        self.schedule_item_organization_subscription_group = \
            f.ScheduleItemOrganizationSubscriptionGroupAllowFactory.create()
        self.schedule_item = self.schedule_item_organization_subscription_group.schedule_item
        
        # Add subscription to group
        self.organization_subscription_group = \
            self.schedule_item_organization_subscription_group.organization_subscription_group
        self.organization_subscription_group.organization_subscriptions.add(self.account_subscription.organization_subscription)

        self.scheduleclassenrollmentoptions_query = '''
  query ScheduleItemEnrollmentOptions($account: ID!, $scheduleItem: ID!) {
    scheduleClassEnrollmentOptions(account: $account, scheduleItem: $scheduleItem) {
      subscriptions {
        allowed
        blocked
        paused
        accountSubscription {
          id
          dateStart
          dateEnd
          organizationSubscription {
            name
          }
        }
      }
    }
    account(id:$account) {
      id
      firstName
      lastName
      fullName
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query_enrollment_options_list_subscription_allowed(self):
        """ Check if account subscription is listed and allowed for this class """
        query = self.scheduleclassenrollmentoptions_query

        variables = {
          'account': to_global_id('AccountNode', self.account.pk),
          'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item.pk),
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClassEnrollmentOptions']['subscriptions'][0]['allowed'], True)
        self.assertEqual(data['scheduleClassEnrollmentOptions']['subscriptions'][0]['accountSubscription']['id'],
            to_global_id('AccountSubscriptionNode', self.account_subscription.id))

    def test_query_enrollment_options_list_subscription_not_allowed(self):
        """ Check if account subscription is listed and not allowed for this class """
        query = self.scheduleclassenrollmentoptions_query
        self.schedule_item_organization_subscription_group.enroll = False
        self.schedule_item_organization_subscription_group.save()

        variables = {
          'account': to_global_id('AccountNode', self.account.pk),
          'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item.pk),
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClassEnrollmentOptions']['subscriptions'][0]['allowed'], False)
        self.assertEqual(data['scheduleClassEnrollmentOptions']['subscriptions'][0]['accountSubscription']['id'],
            to_global_id('AccountSubscriptionNode', self.account_subscription.id))

