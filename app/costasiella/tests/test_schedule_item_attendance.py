# from graphql.error.located_error import GraphQLLocatedError
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

#         self.subscription_query = '''
#   query AccountSubscription($id: ID!, $accountId: ID!, $after: String, $before: String, $archived: Boolean!) {
#     accountSubscription(id:$id) {
#       id
#       account {
#           id
#       }
#       organizationSubscription {
#         id
#         name
#       }
#       financePaymentMethod {
#         id
#         name
#       }
#       dateStart
#       dateEnd
#       note
#       registrationFeePaid
#       createdAt
#     }
#     organizationSubscriptions(first: 100, before: $before, after: $after, archived: $archived) {
#       pageInfo {
#         startCursor
#         endCursor
#         hasNextPage
#         hasPreviousPage
#       }
#       edges {
#         node {
#           id
#           archived
#           name
#         }
#       }
#     }
#     financePaymentMethods(first: 100, before: $before, after: $after, archived: $archived) {
#       pageInfo {
#         startCursor
#         endCursor
#         hasNextPage
#         hasPreviousPage
#       }
#       edges {
#         node {
#           id
#           archived
#           name
#           code
#         }
#       }
#     }
#     account(id:$accountId) {
#       id
#       firstName
#       lastName
#       email
#       phone
#       mobile
#       isActive
#     }
#   }
# '''

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


    def test_query_permision_denied(self):
        """ Query list of schedule item attendances - check permission denied """
        query = self.attendances_query
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_attendance.schedule_item.id),
            'date': '2030-12-30'
        }

        # Regular user
        user = schedule_item_attendance.account
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permision_granted(self):
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


    # def test_query_one(self):
    #     """ Query one account subscription as admin """   
    #     subscription = f.AccountSubscriptionFactory.create()
        
    #     variables = {
    #         "id": to_global_id("AccountSubscriptionNode", subscription.id),
    #         "accountId": to_global_id("AccountNode", subscription.account.id),
    #         "archived": False,
    #     }

    #     # Now query single subscription and check
    #     executed = execute_test_client_api_query(self.subscription_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['accountSubscription']['account']['id'], 
    #         to_global_id('AccountNode', subscription.account.id)
    #     )
    #     self.assertEqual(
    #         data['accountSubscription']['organizationSubscription']['id'], 
    #         to_global_id('OrganizationSubscriptionNode', subscription.organization_subscription.id)
    #     )
    #     self.assertEqual(
    #         data['accountSubscription']['financePaymentMethod']['id'], 
    #         to_global_id('FinancePaymentMethodNode', subscription.finance_payment_method.id)
    #     )
    #     self.assertEqual(data['accountSubscription']['dateStart'], str(subscription.date_start))
    #     self.assertEqual(data['accountSubscription']['dateEnd'], subscription.date_end)
    #     self.assertEqual(data['accountSubscription']['note'], subscription.note)
    #     self.assertEqual(data['accountSubscription']['registrationFeePaid'], subscription.registration_fee_paid)


    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one account subscription """   
    #     subscription = f.AccountSubscriptionFactory.create()

    #     variables = {
    #         "id": to_global_id("AccountSubscriptionNode", subscription.id),
    #         "accountId": to_global_id("AccountNode", subscription.account.id),
    #         "archived": False,
    #     }

    #     # Now query single subscription and check
    #     executed = execute_test_client_api_query(self.subscription_query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     subscription = f.AccountSubscriptionFactory.create()
    #     user = subscription.account

    #     variables = {
    #         "id": to_global_id("AccountSubscriptionNode", subscription.id),
    #         "accountId": to_global_id("AccountNode", subscription.account.id),
    #         "archived": False,
    #     }

    #     # Now query single subscription and check
    #     executed = execute_test_client_api_query(self.subscription_query, user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     subscription = f.AccountSubscriptionFactory.create()
    #     user = subscription.account
    #     permission = Permission.objects.get(codename='view_scheduleitemattendance')
    #     user.user_permissions.add(permission)
    #     user.save()
        

    #     variables = {
    #         "id": to_global_id("AccountSubscriptionNode", subscription.id),
    #         "accountId": to_global_id("AccountNode", subscription.account.id),
    #         "archived": False,
    #     }

    #     # Now query single subscription and check   
    #     executed = execute_test_client_api_query(self.subscription_query, user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['accountSubscription']['organizationSubscription']['id'], 
    #         to_global_id('OrganizationSubscriptionNode', subscription.organization_subscription.id)
    #     )


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



    def test_create_schedule_class_subscription_attendance(self):
        """ Check in to a class using a subscription """
        query = self.schedule_item_attendance_create_mutation

        # Create class pass
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
        self.assertEqual(data['createScheduleItemAttendance']['scheduleItemAttendance']['date'], variables['input']['date'])
        self.assertEqual(data['createScheduleItemAttendance']['scheduleItemAttendance']['attendanceType'], variables['input']['attendanceType'])
        self.assertEqual(data['createScheduleItemAttendance']['scheduleItemAttendance']['bookingStatus'], variables['input']['bookingStatus'])


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
        """ Check create subscription permission denied error message """
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

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


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
          models.AccountClasspass.objects.get(pk=schedule_item_attendance.account_classpass.pk).classes_remaining
        )


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


    def test_update_schedule_item_attendance_permission_denied(self):
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

