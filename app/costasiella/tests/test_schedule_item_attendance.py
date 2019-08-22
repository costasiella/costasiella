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



class GQLAccountSubscription(TestCase):
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
                "date": "2030-12-05",
            }
        }

        self.variables_update = {
            "input": {
                "dateStart": "2017-01-01",
                "dateEnd": "2020-12-31",
                "note": "Update note",
                "registrationFeePaid": True
            }
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

        self.subscription_update_mutation = '''
  mutation UpdateAccountSubscription($input: UpdateAccountSubscriptionInput!) {
    updateAccountSubscription(input: $input) {
      accountSubscription {
        id
        account {
          id
          firstName
          lastName
          email
        }
        organizationSubscription {
          id
          name
        }
        financePaymentMethod {
          id
          name
        }
        dateStart
        dateEnd
        note
        registrationFeePaid        
      }
    }
  }
'''

        self.subscription_delete_mutation = '''
  mutation DeleteAccountSubscription($input: DeleteAccountSubscriptionInput!) {
    deleteAccountSubscription(input: $input) {
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
            'date': '2030-12-05'
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
            'date': '2030-12-05'
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
            'date': '2030-12-05'
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
            'date': '2030-12-05'
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
        """ Create an account subscription """
        query = self.schedule_item_attendance_create_mutation

        # Create class pass
        self.account_classpass = f.AccountClasspassFactory.create()
        self.account = self.account_classpass.account

        # Create organization class pass group
        self.schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupAllowFactory.create()
        self.schedule_item = self.schedule_item_organization_classpass_group.schedule_item
        
        # Add class pass to group
        self.organization_classpass_group = self.schedule_item_organization_classpass_group.organization_classpass_group
        self.organization_classpass_group.organization_classpasses.add(self.account_classpass.organization_classpass)


        variables = self.variables_create
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
            data['createAccountSubscription']['accountSubscription']['account']['id'], 
            variables['input']['account']
        )
        self.assertEqual(
            data['createAccountSubscription']['accountSubscription']['organizationSubscription']['id'], 
            variables['input']['organizationSubscription']
        )
        self.assertEqual(
            data['createAccountSubscription']['accountSubscription']['financePaymentMethod']['id'], 
            variables['input']['financePaymentMethod']
        )
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['dateEnd'], variables['input']['dateEnd'])
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['note'], variables['input']['note'])
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['registrationFeePaid'], variables['input']['registrationFeePaid'])


    # def test_create_subscription_anon_user(self):
    #     """ Don't allow creating account attendances for non-logged in users """
    #     query = self.subscription_create_mutation
        
    #     account = f.RegularUserFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_create_location_permission_granted(self):
    #     """ Allow creating attendances for users with permissions """
    #     query = self.subscription_create_mutation

    #     account = f.RegularUserFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     # Create regular user
    #     user = account
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['createAccountSubscription']['accountSubscription']['organizationSubscription']['id'], 
    #         variables['input']['organizationSubscription']
    #     )


    # def test_create_subscription_permission_denied(self):
    #     """ Check create subscription permission denied error message """
    #     query = self.subscription_create_mutation
    #     account = f.RegularUserFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     # Create regular user
    #     user = account

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_update_subscription(self):
    #     """ Update a subscription """
    #     query = self.subscription_update_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')

    #     self.assertEqual(
    #       data['updateAccountSubscription']['accountSubscription']['organizationSubscription']['id'], 
    #       variables['input']['organizationSubscription']
    #     )
    #     self.assertEqual(
    #       data['updateAccountSubscription']['accountSubscription']['financePaymentMethod']['id'], 
    #       variables['input']['financePaymentMethod']
    #     )
    #     self.assertEqual(data['updateAccountSubscription']['accountSubscription']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['updateAccountSubscription']['accountSubscription']['dateEnd'], variables['input']['dateEnd'])
    #     self.assertEqual(data['updateAccountSubscription']['accountSubscription']['note'], variables['input']['note'])
    #     self.assertEqual(data['updateAccountSubscription']['accountSubscription']['registrationFeePaid'], variables['input']['registrationFeePaid'])


    # def test_update_subscription_anon_user(self):
    #     """ Don't allow updating attendances for non-logged in users """
    #     query = self.subscription_update_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_subscription_permission_granted(self):
    #     """ Allow updating attendances for users with permissions """
    #     query = self.subscription_update_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     user = subscription.account
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateAccountSubscription']['accountSubscription']['dateStart'], variables['input']['dateStart'])


    # def test_update_subscription_permission_denied(self):
    #     """ Check update subscription permission denied error message """
    #     query = self.subscription_update_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     user = subscription.account

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_delete_subscription(self):
    #     """ Delete an account subscription """
    #     query = self.subscription_delete_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     print(data)
    #     self.assertEqual(data['deleteAccountSubscription']['ok'], True)


    # def test_delete_subscription_anon_user(self):
    #     """ Delete subscription denied for anon user """
    #     query = self.subscription_delete_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_delete_subscription_permission_granted(self):
    #     """ Allow deleting attendances for users with permissions """
    #     query = self.subscription_delete_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)

    #     # Give permissions
    #     user = subscription.account
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['deleteAccountSubscription']['ok'], True)


    # def test_delete_subscription_permission_denied(self):
    #     """ Check delete subscription permission denied error message """
    #     query = self.subscription_delete_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
        
    #     user = subscription.account

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')

