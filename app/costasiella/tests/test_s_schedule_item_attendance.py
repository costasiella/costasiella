# from graphql.error.located_error import GraphQLLocatedError
import datetime
import graphql
import base64

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser, Permission

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema


class GQLScheduleItemAttendance(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = [
        'app_settings.json',
        'finance_invoice_group.json',
        'finance_invoice_group_defaults.json',
        'organization.json',
        'system_mail_template.json'
    ]

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleitemattendance'
        self.permission_add = 'add_scheduleitemattendance'
        self.permission_change = 'change_scheduleitemattendance'
        self.permission_delete = 'delete_scheduleitemattendance'

        self.variables_create_classpass = {
            "input": {
                "attendanceType": "CLASSPASS",
                "bookingStatus": "ATTENDING",
                "date": "2019-01-07",
            }
        }

        self.variables_create_subscription = {
            "input": {
                "attendanceType": "SUBSCRIPTION",
                "bookingStatus": "ATTENDING",
                "date": "2019-01-07",
            }
        }

        self.variables_create_classpass_buy_and_book = {
            "input": {
                "attendanceType": "CLASSPASS_BUY_AND_BOOK",
                "bookingStatus": "ATTENDING",
                "date": "2019-01-07",
            }
        }

        self.variables_update_classpass = {
            "input": {
                "bookingStatus": "ATTENDING"
            }
        }

        self.variables_delete = {
            "input": {}
        }

        self.attendances_query = '''
  query ScheduleItemAttendances($after: String, $before: String, $scheduleItem: ID!, $date: Date!) {
    scheduleItemAttendances(first: 100, before: $before, after: $after, scheduleItem: $scheduleItem, date: $date) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          account {
            id
            fullName
          }
          date     
          attendanceType
          bookingStatus
        }
      }
    }
  }
'''

        self.schedule_item_attendance_query = '''
  query ScheduleItemAttendance($id:ID!) {
    scheduleItemAttendance(id: $id) {
      id
      cancellationPossible
      attendanceType
      date
      bookingStatus
      scheduleItem {
        id
      }
    }
  }
'''

        self.schedule_item_attendance_create_mutation = ''' 
  mutation CreateScheduleItemAttendance($input: CreateScheduleItemAttendanceInput!) {
    createScheduleItemAttendance(input:$input) {
      scheduleItemAttendance {
        id
        account {
          id
          fullName
        }
        accountClasspass {
          id
        }
        accountSubscription {
          id
        }
        date     
        attendanceType
        bookingStatus
        scheduleItem {
          id
        }
      }
    }
  }
'''

        self.schedule_item_attendance_update_mutation = '''
  mutation UpdateScheduleItemAttendance($input: UpdateScheduleItemAttendanceInput!) {
    updateScheduleItemAttendance(input:$input) {
      scheduleItemAttendance {
        id
        account {
          id
          fullName
        }
        accountClasspass {
          id
        }
        accountSubscription {
          id
        }
        date     
        attendanceType
        bookingStatus
        scheduleItem {
          id
        }
      }
    }
  }
'''

        self.schedule_item_attendance_delete_mutation = '''
  mutation DeleteScheduleItemAttendance($input: DeleteScheduleItemAttendanceInput!) {
    deleteScheduleItemAttendance(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of schedule item attendances """
        query = self.attendances_query
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_attendance.schedule_item.id),
            'date': '2030-12-30'
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['scheduleItemAttendances']['edges'][0]['node']['id'], 
            to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id)
        )
        self.assertEqual(
            data['scheduleItemAttendances']['edges'][0]['node']['account']['id'], 
            to_global_id("AccountNode", schedule_item_attendance.account.id)
        )
        self.assertEqual(data['scheduleItemAttendances']['edges'][0]['node']['date'], variables['date'])
        self.assertEqual(data['scheduleItemAttendances']['edges'][0]['node']['attendanceType'], "CLASSPASS")
        self.assertEqual(data['scheduleItemAttendances']['edges'][0]['node']['bookingStatus'], "ATTENDING")

    def test_query_permission_denied(self):
        """ Query list of schedule item attendances - check permission denied
        A user can query the orders linked to their account, so an error will never be thrown
        But a user shouldn't be able to view orders from other accounts without additional permission
        """
        query = self.attendances_query
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_attendance.schedule_item.id),
            'date': '2030-12-30'
        }

        # Regular user
        user = schedule_item_attendance.account
        other_user = f.InstructorFactory.create()
        executed = execute_test_client_api_query(query, other_user, variables=variables)
        data = executed.get('data')

        for item in data['scheduleItemAttendances']['edges']:
            node = item['node']
            self.assertNotEqual(node['account']['id'], to_global_id("AccountNode", user.id))

        # self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of schedule item attendances with view permission """
        query = self.attendances_query
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_attendance.schedule_item.id),
            'date': '2030-12-30'
        }

        # Create regular user
        user = schedule_item_attendance.account
        permission = Permission.objects.get(codename='view_scheduleitemattendance')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all attendances
        self.assertEqual(
            data['scheduleItemAttendances']['edges'][0]['node']['id'], 
            to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id)
        )

    def test_query_anon_user(self):
        """ Query list of schedule item attendances - anon user """
        query = self.attendances_query
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_attendance.schedule_item.id),
            'date': '2030-12-30'
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one schedule item attendance """
        query = self.schedule_item_attendance_query
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        schedule_item_attendance.booking_status = "BOOKED"
        schedule_item_attendance.save()

        variables = {
            "id": to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleItemAttendance']['id'],
                         to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id))
        self.assertEqual(data['scheduleItemAttendance']['scheduleItem']['id'],
                         to_global_id("ScheduleItemNode", schedule_item_attendance.schedule_item.id))
        self.assertEqual(data['scheduleItemAttendance']['attendanceType'], schedule_item_attendance.attendance_type)
        self.assertEqual(data['scheduleItemAttendance']['bookingStatus'], schedule_item_attendance.booking_status)
        self.assertEqual(data['scheduleItemAttendance']['date'], str(schedule_item_attendance.date))
        self.assertEqual(data['scheduleItemAttendance']['cancellationPossible'], True)

    def test_query_one_cancellation_no_longer_possible_date(self):
        """ Query one schedule item attendance - cancellation not possible for past class """
        query = self.schedule_item_attendance_query
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        schedule_item_attendance.date = datetime.date.today() - datetime.timedelta(days=1)
        schedule_item_attendance.save()

        variables = {
            "id": to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleItemAttendance']['id'],
                         to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id))
        self.assertEqual(data['scheduleItemAttendance']['cancellationPossible'], False)

    def test_query_one_cancellation_no_longer_possible_status(self):
        """ Query one schedule item attendance - cancellation not possible for status ATTENDING """
        query = self.schedule_item_attendance_query
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        schedule_item_attendance.booking_status = "ATTENDING"
        schedule_item_attendance.save()

        variables = {
            "id": to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleItemAttendance']['id'],
                         to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id))
        self.assertEqual(data['scheduleItemAttendance']['cancellationPossible'], False)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one schedule item attendance """
        query = self.schedule_item_attendance_query
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()

        variables = {
            "id": to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied_other_user(self):
        """ Permission denied message when user lacks authorization to query one schedule item attendance """
        # Create regular user
        query = self.schedule_item_attendance_query
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        user = f.Instructor2Factory.create()

        variables = {
            "id": to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted_own_account(self):
        """ Permission denied message when user lacks authorization to query one schedule item attendance """
        # Create regular user
        query = self.schedule_item_attendance_query
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        user = schedule_item_attendance.account

        variables = {
            "id": to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['scheduleItemAttendance']['id'],
                         to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id))

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        query = self.schedule_item_attendance_query
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        user = schedule_item_attendance.account
        permission = Permission.objects.get(codename='view_scheduleitemattendance')
        user.user_permissions.add(permission)
        user.save()

        variables = {
            "id": to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['scheduleItemAttendance']['id'],
                         to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id))

    def test_create_schedule_class_classpass_attendance(self):
        """ Check in to a class using a class pass """
        query = self.schedule_item_attendance_create_mutation

        # Create class pass
        account_classpass = f.AccountClasspassFactory.create()
        account = account_classpass.account

        # Create organization class pass group
        schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupAllowFactory.create()
        schedule_item = schedule_item_organization_classpass_group.schedule_item
        
        # Add class pass to group
        organization_classpass_group = schedule_item_organization_classpass_group.organization_classpass_group
        organization_classpass_group.organization_classpasses.add(account_classpass.organization_classpass)

        variables = self.variables_create_classpass
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['accountClasspass'] = to_global_id('AccountClasspassNode', account_classpass.id)
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['account']['id'], 
            variables['input']['account']
        )
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['accountClasspass']['id'], 
            variables['input']['accountClasspass']
        )
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['scheduleItem']['id'], 
            variables['input']['scheduleItem']
        )
        self.assertEqual(data['createScheduleItemAttendance']['scheduleItemAttendance']['date'], variables['input']['date'])
        self.assertEqual(data['createScheduleItemAttendance']['scheduleItemAttendance']['attendanceType'], variables['input']['attendanceType'])
        self.assertEqual(data['createScheduleItemAttendance']['scheduleItemAttendance']['bookingStatus'], variables['input']['bookingStatus'])


    def test_create_schedule_class_classpass_attendance_no_classes_remaining_fail(self):
        """ Check if checking in to a class with an empty card fails """
        query = self.schedule_item_attendance_create_mutation

        # Create class pass
        account_classpass = f.AccountClasspassFactory.create()
        account_classpass.classes_remaining = 0
        account_classpass.save()
        account = account_classpass.account

        # Create organization class pass group
        schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupAllowFactory.create()
        schedule_item = schedule_item_organization_classpass_group.schedule_item
        
        # Add class pass to group
        organization_classpass_group = schedule_item_organization_classpass_group.organization_classpass_group
        organization_classpass_group.organization_classpasses.add(account_classpass.organization_classpass)

        variables = self.variables_create_classpass
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['accountClasspass'] = to_global_id('AccountClasspassNode', account_classpass.id)
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'No classes left on this pass.')


    def test_create_schedule_class_classpass_attendance_pass_date_invalid_fail(self):
        """ Check if checking in to a class with an empty card fails """
        query = self.schedule_item_attendance_create_mutation

        # Create class pass
        account_classpass = f.AccountClasspassFactory.create()
        account = account_classpass.account

        # Create organization class pass group
        schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupAllowFactory.create()
        schedule_item = schedule_item_organization_classpass_group.schedule_item
        
        # Add class pass to group
        organization_classpass_group = schedule_item_organization_classpass_group.organization_classpass_group
        organization_classpass_group.organization_classpasses.add(account_classpass.organization_classpass)

        variables = self.variables_create_classpass
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['accountClasspass'] = to_global_id('AccountClasspassNode', account_classpass.id)
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_item.id)
        variables['input']['date'] = '2030-12-30'

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'This pass is not valid on this date.')


    def test_create_schedule_class_classpass_buy_and_book_dropin_attendance(self):
        """ Check in to a class using the organization class pass
            set for drop-in classes """
        query = self.schedule_item_attendance_create_mutation

        # Create schedule_item with prices
        schedule_item_price = f.ScheduleItemPriceFactory.create()

        # Create account
        account = f.RegularUserFactory.create()

        variables = self.variables_create_classpass_buy_and_book
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationClasspass'] = to_global_id(
            'OrganizationClasspassNode', 
            schedule_item_price.organization_classpass_dropin.id
        )
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_item_price.schedule_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['account']['id'],
            variables['input']['account']
        )
        self.assertEqual(
            len(data['createScheduleItemAttendance']['scheduleItemAttendance']['accountClasspass']),
            True
        )
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['scheduleItem']['id'],
            variables['input']['scheduleItem']
        )
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['attendanceType'], 
            "CLASSPASS",
        )
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['date'], 
            variables['input']['date']
        )
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['bookingStatus'], 
            variables['input']['bookingStatus']
        )

    def test_create_schedule_class_classpass_buy_and_book_trial_attendance(self):
        """ Check in to a class using the organization class pass
            set for trial classes """
        query = self.schedule_item_attendance_create_mutation

        # Create schedule_item with prices
        schedule_item_price = f.ScheduleItemPriceFactory.create()

        # Create account
        account = f.RegularUserFactory.create()

        variables = self.variables_create_classpass_buy_and_book
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationClasspass'] = to_global_id(
            'OrganizationClasspassNode', 
            schedule_item_price.organization_classpass_trial.id
        )
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_item_price.schedule_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['account']['id'],
            variables['input']['account']
        )
        self.assertEqual(
            len(data['createScheduleItemAttendance']['scheduleItemAttendance']['accountClasspass']),
            True
        )
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['scheduleItem']['id'],
            variables['input']['scheduleItem']
        )
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['attendanceType'], 
            "CLASSPASS",
        )
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['date'], 
            variables['input']['date']
        )
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['bookingStatus'], 
            variables['input']['bookingStatus']
        )

    def test_create_schedule_class_subscription_attendance(self):
        """ Check in to a class using a subscription """
        query = self.schedule_item_attendance_create_mutation

        # Create subscription
        account_subscription = f.AccountSubscriptionFactory.create()
        account = account_subscription.account

        # Create organization subscription group
        schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupAllowFactory.create()
        schedule_item = schedule_item_organization_subscription_group.schedule_item

        # Add subscription to group
        organization_subscription_group = schedule_item_organization_subscription_group.organization_subscription_group
        organization_subscription_group.organization_subscriptions.add(account_subscription.organization_subscription)

        variables = self.variables_create_subscription
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['accountSubscription'] = to_global_id('AccountSubscriptionNode', account_subscription.id)
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_item.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['account']['id'],
            variables['input']['account']
        )
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['accountSubscription']['id'],
            variables['input']['accountSubscription']
        )
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['scheduleItem']['id'],
            variables['input']['scheduleItem']
        )
        self.assertEqual(data['createScheduleItemAttendance']['scheduleItemAttendance']['date'],
                         variables['input']['date'])
        self.assertEqual(data['createScheduleItemAttendance']['scheduleItemAttendance']['attendanceType'],
                         variables['input']['attendanceType'])
        self.assertEqual(data['createScheduleItemAttendance']['scheduleItemAttendance']['bookingStatus'],
                         variables['input']['bookingStatus'])

    def test_create_schedule_class_subscription_attendance_take_one_credit(self):
        """ Is a credit taken when checkin in to a class using a subscription? """
        query = self.schedule_item_attendance_create_mutation

        # Create subscription
        account_subscription = f.AccountSubscriptionFactory.create()
        account = account_subscription.account

        # Create organization subscription group
        schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupAllowFactory.create()
        schedule_item = schedule_item_organization_subscription_group.schedule_item

        # Add subscription to group
        organization_subscription_group = schedule_item_organization_subscription_group.organization_subscription_group
        organization_subscription_group.organization_subscriptions.add(account_subscription.organization_subscription)

        variables = self.variables_create_subscription
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['accountSubscription'] = to_global_id('AccountSubscriptionNode', account_subscription.id)
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_item.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        # Check successful query; correct data returned.
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['accountSubscription']['id'],
            variables['input']['accountSubscription']
        )

        # Check that one credit is subtracted with a subscription check-in
        qs = models.AccountSubscriptionCredit.objects.filter(
            account_subscription=account_subscription
        )
        self.assertEqual(qs.exists(), True)

    def test_create_schedule_class_subscription_attendance_blocked(self):
        """ Shouldn't be able to check-in with a blocked subscription """
        query = self.schedule_item_attendance_create_mutation

        # Create subscription block
        account_subscription_block = f.AccountSubscriptionBlockFactory.create()
        account_subscription = account_subscription_block.account_subscription
        account = account_subscription.account

        # Create organization subscription group
        schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupAllowFactory.create()
        schedule_item = schedule_item_organization_subscription_group.schedule_item

        # Add subscription to group
        organization_subscription_group = schedule_item_organization_subscription_group.organization_subscription_group
        organization_subscription_group.organization_subscriptions.add(account_subscription.organization_subscription)

        variables = self.variables_create_subscription
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['accountSubscription'] = to_global_id('AccountSubscriptionNode', account_subscription.id)
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_item.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        errors = executed['errors']
        self.assertEqual("This subscription is blocked" in errors[0]['message'], True)

    def test_create_schedule_class_subscription_attendance_paused(self):
        """ Shouldn't be able to check-in with a paused subscription """
        query = self.schedule_item_attendance_create_mutation

        # Create subscription pause
        account_subscription_block = f.AccountSubscriptionPauseFactory.create()
        account_subscription = account_subscription_block.account_subscription
        account = account_subscription.account

        # Create organization subscription group
        schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupAllowFactory.create()
        schedule_item = schedule_item_organization_subscription_group.schedule_item

        # Add subscription to group
        organization_subscription_group = schedule_item_organization_subscription_group.organization_subscription_group
        organization_subscription_group.organization_subscriptions.add(account_subscription.organization_subscription)

        variables = self.variables_create_subscription
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['accountSubscription'] = to_global_id('AccountSubscriptionNode', account_subscription.id)
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_item.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        errors = executed['errors']
        self.assertEqual("This subscription is paused" in errors[0]['message'], True)

    def test_create_schedule_item_attendance_anon_user(self):
        """ Don't allow creating account attendances for non-logged in users """
        query = self.schedule_item_attendance_create_mutation

        # Create class pass
        account_classpass = f.AccountClasspassFactory.create()
        account = account_classpass.account

        # Create organization class pass group
        schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupAllowFactory.create()
        schedule_item = schedule_item_organization_classpass_group.schedule_item
        
        # Add class pass to group
        organization_classpass_group = schedule_item_organization_classpass_group.organization_classpass_group
        organization_classpass_group.organization_classpasses.add(account_classpass.organization_classpass)

        variables = self.variables_create_classpass
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['accountClasspass'] = to_global_id('AccountClasspassNode', account_classpass.id)
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_schedule_item_attendance_permission_granted(self):
        """ Allow creating attendances for users with permissions """
        query = self.schedule_item_attendance_create_mutation

        # Create class pass
        account_classpass = f.AccountClasspassFactory.create()
        account = account_classpass.account

        # Create organization class pass group
        schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupAllowFactory.create()
        schedule_item = schedule_item_organization_classpass_group.schedule_item
        
        # Add class pass to group
        organization_classpass_group = schedule_item_organization_classpass_group.organization_classpass_group
        organization_classpass_group.organization_classpasses.add(account_classpass.organization_classpass)

        variables = self.variables_create_classpass
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['accountClasspass'] = to_global_id('AccountClasspassNode', account_classpass.id)
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_item.id)

        # Create regular user
        user = account
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['account']['id'], 
            variables['input']['account']
        )

    def test_create_schedule_item_attendance_permission_denied(self):
        """
        Verify that the user who created the attendance record is the user who executed the query, not the account
        specified, if any.
        """
        query = self.schedule_item_attendance_create_mutation

        # Create class pass
        account_classpass = f.AccountClasspassFactory.create()
        account = account_classpass.account
        other_user = f.InstructorFactory.create()

        # Create organization class pass group
        schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupAllowFactory.create()
        schedule_item = schedule_item_organization_classpass_group.schedule_item
        
        # Add class pass to group
        organization_classpass_group = schedule_item_organization_classpass_group.organization_classpass_group
        organization_classpass_group.organization_classpasses.add(account_classpass.organization_classpass)

        variables = self.variables_create_classpass
        variables['input']['account'] = to_global_id('AccountNode', other_user.id)
        variables['input']['accountClasspass'] = to_global_id('AccountClasspassNode', account_classpass.id)
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_item.id)

        # Create regular user
        user = account
        executed = execute_test_client_api_query(
            query, 
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')

        self.assertEqual(
            data['createScheduleItemAttendance']['scheduleItemAttendance']['account']['id'],
            to_global_id('AccountNode', account.id)
        )


    def test_update_schedule_item_attendance(self):
        """ Update a class attendance status """
        query = self.schedule_item_attendance_update_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = self.variables_update_classpass
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateScheduleItemAttendance']['scheduleItemAttendance']['id'], 
          variables['input']['id']
        )
        self.assertEqual(
          data['updateScheduleItemAttendance']['scheduleItemAttendance']['bookingStatus'], 
          variables['input']['bookingStatus']
        )


    def test_update_schedule_item_attendance_classpass_one_less_class_remaining(self):
        """ Update a class attendance status to attending and check that 1 class is taken from the pass """
        query = self.schedule_item_attendance_update_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        account_classpass = schedule_item_attendance.account_classpass
        classes_remaining_before_checkin = account_classpass.classes_remaining
        account_classpass.update_classes_remaining()
        classes_remaining_after_checkin = account_classpass.classes_remaining

        self.assertEqual(classes_remaining_before_checkin - 1, classes_remaining_after_checkin)

    def test_update_schedule_item_attendance_classpass_return_class_on_cancel(self):
        """ Update a class attendance status to attending and check that 1 class is taken from the pass """
        query = self.schedule_item_attendance_update_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        account_classpass = schedule_item_attendance.account_classpass
        account_classpass.update_classes_remaining()
        classes_remaining = account_classpass.classes_remaining

        variables = self.variables_update_classpass
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)
        variables['input']['bookingStatus'] = "CANCELLED"

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateScheduleItemAttendance']['scheduleItemAttendance']['bookingStatus'], 
          variables['input']['bookingStatus']
        )
        self.assertEqual(classes_remaining + 1,
          models.AccountClasspass.objects.get(pk=schedule_item_attendance.account_classpass.pk).classes_remaining)

    def test_update_schedule_item_attendance_subscription_return_credit_on_cancel(self):
        """ Update a class attendance status to cancelled and check that 1 credit is returned """
        query = self.schedule_item_attendance_update_mutation

        account_subscription_credit = f.AccountSubscriptionCreditAttendanceFactory.create()
        schedule_item_attendance = account_subscription_credit.schedule_item_attendance
        account_subscription = schedule_item_attendance.account_subscription
        credits_total_before = account_subscription.get_credits_total(schedule_item_attendance.date)

        variables = self.variables_update_classpass
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)
        variables['input']['bookingStatus'] = "CANCELLED"

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        credits_total_after = account_subscription.get_credits_total(schedule_item_attendance.date)

        self.assertEqual(
          data['updateScheduleItemAttendance']['scheduleItemAttendance']['bookingStatus'],
          variables['input']['bookingStatus']
        )
        self.assertEqual(credits_total_before + 1, credits_total_after)

    def test_update_schedule_item_attendance_anon_user(self):
        """ Don't allow updating attendances for non-logged in users """
        query = self.schedule_item_attendance_update_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = self.variables_update_classpass
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_schedule_item_attendance_permission_granted(self):
        """ Allow updating attendances for users with permissions """
        query = self.schedule_item_attendance_update_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = self.variables_update_classpass
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)

        user = schedule_item_attendance.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
          data['updateScheduleItemAttendance']['scheduleItemAttendance']['bookingStatus'], 
          variables['input']['bookingStatus']
        )

    def test_update_schedule_item_attendance_granted_own_account(self):
        """ Update a class attendance status permission denied """
        query = self.schedule_item_attendance_update_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = self.variables_update_classpass
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)

        user = schedule_item_attendance.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
          data['updateScheduleItemAttendance']['scheduleItemAttendance']['bookingStatus'],
          variables['input']['bookingStatus']
        )

    def test_update_schedule_item_attendance_permission_denied_other_account(self):
        """ Update a class attendance status permission denied """
        query = self.schedule_item_attendance_update_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = self.variables_update_classpass
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)

        user = f.Instructor2Factory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_schedule_item_attendance(self):
        """ Delete schedule item attendance """
        query = self.schedule_item_attendance_delete_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleItemAttendance']['ok'], True)

    def test_delete_schedule_item_attendance_return_class_to_pass(self):
        """ Delete schedule item attendance and check the number of classes remaining 
        the pass += 1
        """
        query = self.schedule_item_attendance_delete_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        account_classpass = schedule_item_attendance.account_classpass
        account_classpass.update_classes_remaining()
        classes_remaining = account_classpass.classes_remaining
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleItemAttendance']['ok'], True)

        self.assertEqual(classes_remaining + 1,
          models.AccountClasspass.objects.get(pk=schedule_item_attendance.account_classpass.pk).classes_remaining
        )

    def test_delete_schedule_item_attendance_return_credit_to_subscription(self):
        """ Delete schedule item attendance and check that the number of credits goes +1
        """
        query = self.schedule_item_attendance_delete_mutation

        account_subscription_credit = f.AccountSubscriptionCreditAttendanceFactory.create()
        schedule_item_attendance = account_subscription_credit.schedule_item_attendance
        account_subscription = schedule_item_attendance.account_subscription
        credits_total_before = account_subscription.get_credits_total(schedule_item_attendance.date)

        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        credits_total_after = account_subscription.get_credits_total(schedule_item_attendance.date)

        self.assertEqual(data['deleteScheduleItemAttendance']['ok'], True)
        self.assertEqual(credits_total_before + 1, credits_total_after)

    def test_delete_schedule_item_attendance_anon_user(self):
        """ Delete schedule item attendance denied for anon user """
        query = self.schedule_item_attendance_delete_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_schedule_item_attendance_permission_granted(self):
        """ Allow deleting schedule item attendances for users with permissions """
        query = self.schedule_item_attendance_delete_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)

        # Give permissions
        user = schedule_item_attendance.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleItemAttendance']['ok'], True)

    def test_delete_schedule_item_attendance_permission_denied(self):
        """ Check delete schedule item attendance permission denied error message """
        query = self.schedule_item_attendance_delete_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemAttendanceNode', schedule_item_attendance.id)
        
        user = schedule_item_attendance.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

