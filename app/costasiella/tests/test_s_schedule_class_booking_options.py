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
    This test uses the TransacrionTestCase; it's slower then the regular test case as the DB gets 
    reset every test. However there's some data from previous tests that causes these tests to fail.
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

        # Create class pass
        self.account_classpass = f.AccountClasspassFactory.create()
        self.account = self.account_classpass.account

        # Create subscription
        self.account_subscription = f.AccountSubscriptionFactory.create(account=self.account)

        # Create organization class pass group
        self.schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupAllowFactory.create()
        self.schedule_item = self.schedule_item_organization_classpass_group.schedule_item
        
        # Add class pass to group
        self.organization_classpass_group = self.schedule_item_organization_classpass_group.organization_classpass_group
        self.organization_classpass_group.organization_classpasses.add(self.account_classpass.organization_classpass)

        # Create organization subscriptions group
        self.schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupAllowFactory.create(
            initial_schedule_item=self.schedule_item
        )
        
        # Add subscription to group
        self.organization_subscription_group = \
            self.schedule_item_organization_subscription_group.organization_subscription_group
        self.organization_subscription_group.organization_subscriptions.add(self.account_subscription.organization_subscription)

        # Set drop-in and trial cards (prices)
        self.schedule_item_price = f.ScheduleItemPriceFactory.create(initial_schedule_item=self.schedule_item)

        self.scheduleclassbookingoptions_query = '''
  query ScheduleClassBookingOptions($account: ID!, $scheduleItem:ID!, $date:Date!, $listType:String!) {
    scheduleClassBookingOptions(account: $account, scheduleItem: $scheduleItem, date:$date, listType:$listType) {
      date
      account {
        id
        fullName
      }
      scheduleItem {
        frequencyType
        frequencyInterval
        organizationLocationRoom {
          id
          name
          organizationLocation {
            id
            name
          }
        }
        organizationClasstype {
          id
          name
        }
        organizationLevel {
          id
          name
        }
        dateStart
        dateEnd
        timeStart
        timeEnd
      }
      scheduleItemPrices {
        organizationClasspassDropin {
          id
          name
          priceDisplay
        }
        organizationClasspassTrial {
          id
          name
          priceDisplay
        }
      }
      classpasses {
        bookingType 
        allowed
        accountClasspass {
          id
          dateStart
          dateEnd
          classesRemainingDisplay
          organizationClasspass {
            id
            name
          }
        }
      }
      subscriptions {
        bookingType
        allowed
        accountSubscription {
          id
          dateStart
          dateEnd
          organizationSubscription {
            id
            name
          }
        }
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query_booking_options_list_type_ATTEND(self):
        """ Query should accept list type ATTEND """
        query = self.scheduleclassbookingoptions_query

        variables = {
          'account': to_global_id('AccountNode', self.account.pk),
          'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item.pk),
          'date': str(self.monday),
          'listType': 'ATTEND'
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClassBookingOptions']['date'], variables['date'])
        self.assertEqual(data['scheduleClassBookingOptions']['classpasses'][0]['allowed'], True)
        self.assertEqual(data['scheduleClassBookingOptions']['classpasses'][0]['accountClasspass']['id'], 
            to_global_id('AccountClasspassNode', self.account_classpass.id))


    def test_query_booking_options_list_type_INVALID(self):
        """ Query should not accept list type INVALID """
        query = self.scheduleclassbookingoptions_query

        variables = {
          'account': to_global_id('AccountNode', self.account.pk),
          'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item.pk),
          'date': str(self.monday),
          'listType': 'INVALID'
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Invalid list type, possible options [ATTEND, ENROLL, SHOP_BOOK]')


    def test_query_booking_options_invalid_date(self):
        """ Query should not accept dates when a class isn't happening """
        query = self.scheduleclassbookingoptions_query

        tuesday = self.monday + datetime.timedelta(days=1)

        variables = {
          'account': to_global_id('AccountNode', self.account.pk),
          'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item.pk),
          'date': str(self.tuesday),
          'listType': 'ATTEND'
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], "This class doesn't take place on date: " + str(tuesday))


    #TODO: Test types SHOP_BOOk and ENROLL are accepted (when the time comes)


    def test_query_classpass_allowed(self):
        """ Query list of scheduleclasses """
        query = self.scheduleclassbookingoptions_query

        variables = {
          'account': to_global_id('AccountNode', self.account.pk),
          'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item.pk),
          'date': str(self.monday),
          'listType': 'ATTEND'
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClassBookingOptions']['date'], variables['date'])
        self.assertEqual(data['scheduleClassBookingOptions']['classpasses'][0]['allowed'], True)
        self.assertEqual(data['scheduleClassBookingOptions']['classpasses'][0]['accountClasspass']['id'], 
            to_global_id('AccountClasspassNode', self.account_classpass.id))
        

    def test_query_classpass_not_allowed(self):
        """ Query list of scheduleclasses """
        query = self.scheduleclassbookingoptions_query

        self.schedule_item_organization_classpass_group.attend = False
        self.schedule_item_organization_classpass_group.save()

        variables = {
          'account': to_global_id('AccountNode', self.account.pk),
          'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item.pk),
          'date': str(self.monday),
          'listType': 'ATTEND'
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClassBookingOptions']['date'], variables['date'])
        self.assertEqual(data['scheduleClassBookingOptions']['classpasses'][0]['allowed'], False)
        self.assertEqual(data['scheduleClassBookingOptions']['classpasses'][0]['accountClasspass']['id'], 
            to_global_id('AccountClasspassNode', self.account_classpass.id))
        
    
    def test_query_subscription_allowed(self):
        """ Query list of scheduleclasses """
        query = self.scheduleclassbookingoptions_query

        variables = {
          'account': to_global_id('AccountNode', self.account.pk),
          'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item.pk),
          'date': str(self.monday),
          'listType': 'ATTEND'
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClassBookingOptions']['date'], variables['date'])
        self.assertEqual(data['scheduleClassBookingOptions']['subscriptions'][0]['allowed'], True)
        self.assertEqual(data['scheduleClassBookingOptions']['subscriptions'][0]['accountSubscription']['id'], 
            to_global_id('AccountSubscriptionNode', self.account_subscription.id))
        

    def test_query_subscription_not_allowed(self):
        """ Query list of scheduleclasses """
        query = self.scheduleclassbookingoptions_query

        self.schedule_item_organization_subscription_group.attend = False
        self.schedule_item_organization_subscription_group.save()

        variables = {
          'account': to_global_id('AccountNode', self.account.pk),
          'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item.pk),
          'date': str(self.monday),
          'listType': 'ATTEND'
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClassBookingOptions']['date'], variables['date'])
        self.assertEqual(data['scheduleClassBookingOptions']['subscriptions'][0]['allowed'], False)
        self.assertEqual(data['scheduleClassBookingOptions']['subscriptions'][0]['accountSubscription']['id'], 
            to_global_id('AccountSubscriptionNode', self.account_subscription.id))

    
    # Test listing of dropin and trial cards
    def test_query_schedule_item_price_dropin_and_trial(self):
        """ Query list of schedule classes and check listing of drop-in and trial cards """
        query = self.scheduleclassbookingoptions_query

        variables = {
          'account': to_global_id('AccountNode', self.account.pk),
          'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item.pk),
          'date': str(self.monday),
          'listType': 'ATTEND'
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClassBookingOptions']['date'], variables['date'])
        self.assertEqual(
            data['scheduleClassBookingOptions']['scheduleItemPrices']['organizationClasspassDropin']['id'], 
            to_global_id('OrganizationClasspassNode', self.schedule_item_price.organization_classpass_dropin.id)
        )
        self.assertEqual(
            data['scheduleClassBookingOptions']['scheduleItemPrices']['organizationClasspassTrial']['id'], 
            to_global_id('OrganizationClasspassNode', self.schedule_item_price.organization_classpass_trial.id)
        )
