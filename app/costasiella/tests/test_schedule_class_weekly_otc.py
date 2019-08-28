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



class GQLScheduleClassWeeklyOTC(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleclassweeklyotc'
        self.permission_add = 'add_scheduleclassweeklyotc'
        self.permission_change = 'change_scheduleclassweeklyotc'
        self.permission_delete = 'delete_scheduleclassweeklyotc'


        self.variables_update_classpass = {
            "input": {
                "bookingStatus": "ATTENDING"
            }
        }

        self.variables_delete = {
            "input": {}
        }

        self.weeklyotcs_query = '''
  query ScheduleClassWeeklyOTCs($scheduleItem: ID!, $date: Date!) {
    scheduleClassWeeklyOtcs(first:1, scheduleItem: $scheduleItem, date:$date) {
      edges {
        node {
          id 
          date
          account {
            id
            fullName
          }
          role
          account2 {
            id
            fullName
          }
          role2
          organizationLocationRoom {
            id
            name
          }
          organizationClasstype {
            id
            name
          }
          organizationLevel {
            id
            name
          }
          timeStart
          timeEnd
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


        self.schedule_item_weeklyotc_update_mutation = '''
  mutation UpdateScheduleItemWeeklyOTC($input: UpdateScheduleItemWeeklyOTCInput!) {
    updateScheduleItemWeeklyOTC(input:$input) {
      scheduleItemWeeklyOTC {
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
        weeklyotcType
        bookingStatus
        scheduleItem {
          id
        }
      }
    }
  }
'''

        self.schedule_item_weeklyotc_delete_mutation = '''
  mutation DeleteScheduleItemWeeklyOTC($input: DeleteScheduleItemWeeklyOTCInput!) {
    deleteScheduleItemWeeklyOTC(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of schedule item weeklyotcs """
        query = self.weeklyotcs_query
        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_weeklyotc.schedule_item.id),
            'date': '2030-12-30'
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['scheduleItemWeeklyOtcs']['edges'][0]['node']['id'], 
            to_global_id("ScheduleItemWeeklyOTCNode", schedule_item_weeklyotc.id)
        )
        self.assertEqual(
            data['scheduleItemWeeklyOtcs']['edges'][0]['node']['account']['id'], 
            to_global_id("AccountNode", schedule_item_weeklyotc.account.id)
        )
        self.assertEqual(data['scheduleItemWeeklyOtcs']['edges'][0]['node']['date'], variables['date'])
        self.assertEqual(data['scheduleItemWeeklyOtcs']['edges'][0]['node']['weeklyotcType'], "CLASSPASS")
        self.assertEqual(data['scheduleItemWeeklyOtcs']['edges'][0]['node']['bookingStatus'], "ATTENDING")


    def test_query_permision_denied(self):
        """ Query list of schedule item weeklyotcs - check permission denied """
        query = self.weeklyotcs_query
        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_weeklyotc.schedule_item.id),
            'date': '2030-12-30'
        }

        # Regular user
        user = schedule_item_weeklyotc.account
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permision_granted(self):
        """ Query list of schedule item weeklyotcs with view permission """
        query = self.weeklyotcs_query
        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_weeklyotc.schedule_item.id),
            'date': '2030-12-30'
        }

        # Create regular user
        user = schedule_item_weeklyotc.account
        permission = Permission.objects.get(codename='view_scheduleitemweeklyotc')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all weeklyotcs
        self.assertEqual(
            data['scheduleItemWeeklyOtcs']['edges'][0]['node']['id'], 
            to_global_id("ScheduleItemWeeklyOTCNode", schedule_item_weeklyotc.id)
        )


    def test_query_anon_user(self):
        """ Query list of schedule item weeklyotcs - anon user """
        query = self.weeklyotcs_query
        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_weeklyotc.schedule_item.id),
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
    #     permission = Permission.objects.get(codename='view_scheduleitemweeklyotc')
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


    def test_update_schedule_item_weeklyotc(self):
        """ Update a class weeklyotc status """
        query = self.schedule_item_weeklyotc_update_mutation

        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        variables = self.variables_update_classpass
        variables['input']['id'] = to_global_id('ScheduleItemWeeklyOTCNode', schedule_item_weeklyotc.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateScheduleItemWeeklyOTC']['scheduleItemWeeklyOTC']['id'], 
          variables['input']['id']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOTC']['scheduleItemWeeklyOTC']['bookingStatus'], 
          variables['input']['bookingStatus']
        )


    def test_update_schedule_item_weeklyotc_classpass_one_less_class_remaining(self):
        """ Update a class weeklyotc status to attending and check that 1 class is taken from the pass """
        query = self.schedule_item_weeklyotc_update_mutation

        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        account_classpass = schedule_item_weeklyotc.account_classpass
        classes_remaining_before_checkin = account_classpass.classes_remaining
        account_classpass.update_classes_remaining()
        classes_remaining_after_checkin = account_classpass.classes_remaining

        self.assertEqual(classes_remaining_before_checkin - 1, classes_remaining_after_checkin)


    def test_update_schedule_item_weeklyotc_classpass_return_class_on_cancel(self):
        """ Update a class weeklyotc status to attending and check that 1 class is taken from the pass """
        query = self.schedule_item_weeklyotc_update_mutation

        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        account_classpass = schedule_item_weeklyotc.account_classpass
        account_classpass.update_classes_remaining()
        classes_remaining = account_classpass.classes_remaining

        variables = self.variables_update_classpass
        variables['input']['id'] = to_global_id('ScheduleItemWeeklyOTCNode', schedule_item_weeklyotc.id)
        variables['input']['bookingStatus'] = "CANCELLED"

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateScheduleItemWeeklyOTC']['scheduleItemWeeklyOTC']['bookingStatus'], 
          variables['input']['bookingStatus']
        )
        self.assertEqual(classes_remaining + 1,
          models.AccountClasspass.objects.get(pk=schedule_item_weeklyotc.account_classpass.pk).classes_remaining
        )


    def test_update_schedule_item_weeklyotc_anon_user(self):
        """ Don't allow updating weeklyotcs for non-logged in users """
        query = self.schedule_item_weeklyotc_update_mutation

        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        variables = self.variables_update_classpass
        variables['input']['id'] = to_global_id('ScheduleItemWeeklyOTCNode', schedule_item_weeklyotc.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_schedule_item_weeklyotc_permission_granted(self):
        """ Allow updating weeklyotcs for users with permissions """
        query = self.schedule_item_weeklyotc_update_mutation

        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        variables = self.variables_update_classpass
        variables['input']['id'] = to_global_id('ScheduleItemWeeklyOTCNode', schedule_item_weeklyotc.id)

        user = schedule_item_weeklyotc.account
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
          data['updateScheduleItemWeeklyOTC']['scheduleItemWeeklyOTC']['bookingStatus'], 
          variables['input']['bookingStatus']
        )


    def test_update_schedule_item_weeklyotc_permission_denied(self):
        """ Update a class weeklyotc status permission denied """
        query = self.schedule_item_weeklyotc_update_mutation

        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        variables = self.variables_update_classpass
        variables['input']['id'] = to_global_id('ScheduleItemWeeklyOTCNode', schedule_item_weeklyotc.id)

        user = schedule_item_weeklyotc.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_delete_schedule_item_weeklyotc(self):
        """ Delete schedule item weeklyotc """
        query = self.schedule_item_weeklyotc_delete_mutation

        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemWeeklyOTCNode', schedule_item_weeklyotc.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleItemWeeklyOTC']['ok'], True)


    def test_delete_schedule_item_weeklyotc_return_class_to_pass(self):
        """ Delete schedule item weeklyotc and check the number of classes remaining 
        the pass += 1
        """
        query = self.schedule_item_weeklyotc_delete_mutation

        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        account_classpass = schedule_item_weeklyotc.account_classpass
        account_classpass.update_classes_remaining()
        classes_remaining = account_classpass.classes_remaining
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemWeeklyOTCNode', schedule_item_weeklyotc.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleItemWeeklyOTC']['ok'], True)

        self.assertEqual(classes_remaining + 1,
          models.AccountClasspass.objects.get(pk=schedule_item_weeklyotc.account_classpass.pk).classes_remaining
        )


    def test_delete_schedule_item_weeklyotc_anon_user(self):
        """ Delete schedule item weeklyotc denied for anon user """
        query = self.schedule_item_weeklyotc_delete_mutation

        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemWeeklyOTCNode', schedule_item_weeklyotc.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_delete_schedule_item_weeklyotc_permission_granted(self):
        """ Allow deleting schedule item weeklyotcs for users with permissions """
        query = self.schedule_item_weeklyotc_delete_mutation

        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemWeeklyOTCNode', schedule_item_weeklyotc.id)

        # Give permissions
        user = schedule_item_weeklyotc.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleItemWeeklyOTC']['ok'], True)


    def test_delete_schedule_item_weeklyotc_permission_denied(self):
        """ Check delete schedule item weeklyotc permission denied error message """
        query = self.schedule_item_weeklyotc_delete_mutation

        schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemWeeklyOTCNode', schedule_item_weeklyotc.id)
        
        user = schedule_item_weeklyotc.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

