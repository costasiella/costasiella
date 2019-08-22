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

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleitem'
        self.permission_add = 'add_scheduleitem'
        self.permission_change = 'change_scheduleitem'
        self.permission_delete = 'delete_scheduleitem'

        self.next_monday = next_weekday(datetime.date.today(), 1)

        # Create class pass
        self.account_classpass = f.AccountClasspassFactory.create()
        self.account = self.account_classpass.account

        # Create organization class pass group
        self.schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupAllowFactory.create()
        self.schedule_item = self.schedule_item_organization_classpass_group.schedule_item
        
        # Add class pass to group
        self.organization_classpass_group = self.schedule_item_organization_classpass_group.organization_classpass_group
        self.organization_classpass_group.organization_classpasses.add(self.account_classpass.organization_classpass)

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
          'date': str(self.next_monday),
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
          'date': str(self.next_monday),
          'listType': 'INVALID'
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Invalid list type, possible options [ATTEND, ENROLL, SHOP_BOOK]')


    def test_query_booking_options_invalid_date(self):
        """ Query should not accept dates when a class isn't happening """
        query = self.scheduleclassbookingoptions_query

        next_tuesday = self.next_monday + datetime.timedelta(days=1)

        variables = {
          'account': to_global_id('AccountNode', self.account.pk),
          'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item.pk),
          'date': str(self.next_tuesday),
          'listType': 'INVALID'
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], "This class doesn't take place on date: " + str(next_tuesday))


    #TODO: Test types SHOP_BOOk and ENROLL are accepted (when the time comes)


    def test_query_classpass_allowed(self):
        """ Query list of scheduleclasses """
        query = self.scheduleclassbookingoptions_query

        variables = {
          'account': to_global_id('AccountNode', self.account.pk),
          'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item.pk),
          'date': str(self.next_monday),
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
          'date': str(self.next_monday),
          'listType': 'ATTEND'
        }
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleClassBookingOptions']['date'], variables['date'])
        self.assertEqual(data['scheduleClassBookingOptions']['classpasses'][0]['allowed'], False)
        self.assertEqual(data['scheduleClassBookingOptions']['classpasses'][0]['accountClasspass']['id'], 
            to_global_id('AccountClasspassNode', self.account_classpass.id))
        
