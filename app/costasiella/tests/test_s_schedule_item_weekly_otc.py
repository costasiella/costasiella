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



class GQLScheduleItemWeeklyOTC(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleitemweeklyotc'
        self.permission_add = 'add_scheduleitemweeklyotc'
        self.permission_change = 'change_scheduleitemweeklyotc'
        self.permission_delete = 'delete_scheduleitemweeklyotc'

        self.class_otc = f.SchedulePublicWeeklyClassOTCFactory.create()

        self.variables_list_all = {
            'scheduleItem': to_global_id('ScheduleItemNode', self.class_otc.schedule_item.id),
            'date': '2030-12-30'
        }


        self.variables_update = {
            "input": {
                "scheduleItem": to_global_id('ScheduleItemNode', self.class_otc.schedule_item.id),
                "date": "2030-12-30",
                "description": "hello world",
                "account": to_global_id('AccountNode', self.class_otc.account.id),
                "role": "ASSISTANT",
                "account2": to_global_id('AccountNode', self.class_otc.account_2.id),
                "role2": "ASSISTANT",
                "organizationLocationRoom": to_global_id('OrganizationLocationRoomNode', self.class_otc.organization_location_room.id),
                "organizationClasstype": to_global_id('OrganizationClasstypeNode', self.class_otc.organization_classtype.id),
                "organizationLevel": to_global_id('OrganizationLevelNode', self.class_otc.organization_level.id),
                "timeStart": "04:30:00",
                "timeEnd": "07:00:00",
                "infoMailEnabled": True
            }
        }

        self.variables_delete = {
            "input": {
                "scheduleItem": to_global_id('ScheduleItemNode', self.class_otc.schedule_item.id),
                "date": "2030-12-30",
            }
        }

        self.weeklyotcs_query = '''
  query ScheduleItemWeeklyOTCs($scheduleItem: ID!, $date: Date!) {
    scheduleItemWeeklyOtcs(first:1, scheduleItem: $scheduleItem, date:$date) {
      edges {
        node {
          id 
          date
          status
          description
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
          organizationShift {
            id
            name
          }
          timeStart
          timeEnd
          infoMailEnabled
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


        self.update_mutation = '''
  mutation UpdateScheduleItemWeeklyOTC($input: UpdateScheduleItemWeeklyOTCInput!) {
    updateScheduleItemWeeklyOtc(input:$input) {
      scheduleItemWeeklyOtc {
        id
        scheduleItem {
          id
        }
        date
        description
        account {
          id
        }
        role
        account2 {
          id
        }
        role2
        organizationLocationRoom {
          id
        }
        organizationClasstype {
          id
        }
        organizationLevel {
          id
        }
        timeStart
        timeEnd
        infoMailEnabled
      }
    }
  }
'''

        self.delete_mutation = '''
  mutation DeleteScheduleItemWeeklyOTC($input: DeleteScheduleItemWeeklyOTCInput!) {
    deleteScheduleItemWeeklyOtc(input: $input) {
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
        # schedule_item_weeklyotc = f.ScheduleItemWeeklyOTCClasspassFactory.create()

        variables = self.variables_list_all
        self.class_otc.organization_shift = f.OrganizationShiftFactory.create()
        self.class_otc.save()

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['scheduleItemWeeklyOtcs']['edges'][0]['node']['id'], 
            to_global_id("ScheduleItemWeeklyOTCNode", self.class_otc.id)
        )
        self.assertEqual(data['scheduleItemWeeklyOtcs']['edges'][0]['node']['date'], variables['date'])
        self.assertEqual(data['scheduleItemWeeklyOtcs']['edges'][0]['node']["status"], self.class_otc.status)
        self.assertEqual(data['scheduleItemWeeklyOtcs']['edges'][0]['node']['description'], self.class_otc.description)
        self.assertEqual(
            data['scheduleItemWeeklyOtcs']['edges'][0]['node']['account']['id'], 
            to_global_id("AccountNode", self.class_otc.account.id)
        )
        self.assertEqual(data['scheduleItemWeeklyOtcs']['edges'][0]['node']['role'], self.class_otc.role)
        self.assertEqual(
            data['scheduleItemWeeklyOtcs']['edges'][0]['node']['account2']['id'], 
            to_global_id("AccountNode", self.class_otc.account_2.id)
        )
        self.assertEqual(data['scheduleItemWeeklyOtcs']['edges'][0]['node']['role2'], self.class_otc.role_2)
        self.assertEqual(
            data['scheduleItemWeeklyOtcs']['edges'][0]['node']['organizationLocationRoom']['id'], 
            to_global_id("OrganizationLocationRoomNode", self.class_otc.organization_location_room.id)
        )
        self.assertEqual(
            data['scheduleItemWeeklyOtcs']['edges'][0]['node']['organizationClasstype']['id'], 
            to_global_id("OrganizationClasstypeNode", self.class_otc.organization_classtype.id)
        )
        self.assertEqual(
            data['scheduleItemWeeklyOtcs']['edges'][0]['node']['organizationLevel']['id'], 
            to_global_id("OrganizationLevelNode", self.class_otc.organization_level.id)
        )
        self.assertEqual(
            data['scheduleItemWeeklyOtcs']['edges'][0]['node']['organizationShift']['id'],
            to_global_id("OrganizationShiftNode", self.class_otc.organization_shift.id)
        )
        self.assertEqual(data['scheduleItemWeeklyOtcs']['edges'][0]['node']['timeStart'], str(self.class_otc.time_start))
        self.assertEqual(data['scheduleItemWeeklyOtcs']['edges'][0]['node']['timeEnd'], str(self.class_otc.time_end))        
        self.assertEqual(data['scheduleItemWeeklyOtcs']['edges'][0]['node']['infoMailEnabled'],
                         self.class_otc.info_mail_enabled)


    def test_query_permission_denied(self):
        """ Query list of schedule item weeklyotcs - check permission denied """
        query = self.weeklyotcs_query

        # Regular user
        user = self.class_otc.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_list_all)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permission_granted(self):
        """ Query list of schedule item weeklyotcs with view permission """
        query = self.weeklyotcs_query

        # Create regular user
        user = self.class_otc.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_list_all)
        data = executed.get('data')

        # List all weeklyotcs
        self.assertEqual(
            data['scheduleItemWeeklyOtcs']['edges'][0]['node']['id'], 
            to_global_id("ScheduleItemWeeklyOTCNode", self.class_otc.id)
        )


    def test_query_anon_user(self):
        """ Query list of schedule item weeklyotcs - anon user """
        query = self.weeklyotcs_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_list_all)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_schedule_class_weeklyotc(self):
        """ Update a class weeklyotc status """
        query = self.update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['scheduleItem']['id'], 
          variables['input']['scheduleItem']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['date'], 
          variables['input']['date']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['description'], 
          variables['input']['description']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['account']['id'], 
          variables['input']['account']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['role'], 
          variables['input']['role']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['account2']['id'], 
          variables['input']['account2']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['role2'], 
          variables['input']['role2']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['organizationLocationRoom']['id'], 
          variables['input']['organizationLocationRoom']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['organizationClasstype']['id'], 
          variables['input']['organizationClasstype']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['organizationLevel']['id'], 
          variables['input']['organizationLevel']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['timeStart'], 
          variables['input']['timeStart']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['timeEnd'], 
          variables['input']['timeEnd']
        )
        self.assertEqual(
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['infoMailEnabled'],
          variables['input']['infoMailEnabled']
        )


    def test_update_schedule_class_weeklyotc_anon_user(self):
        """ Don't allow updating weeklyotcs for non-logged in users """
        query = self.update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_schedule_class_weeklyotc_permission_granted(self):
        """ Allow updating weeklyotcs for users with permissions """
        query = self.update_mutation
        variables = self.variables_update

        user = self.class_otc.account
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
          data['updateScheduleItemWeeklyOtc']['scheduleItemWeeklyOtc']['scheduleItem']['id'], 
          variables['input']['scheduleItem']
        )


    def test_update_schedule_class_weeklyotc_permission_denied(self):
        """ Update a class weeklyotc status permission denied """
        query = self.update_mutation
        variables = self.variables_update

        user = self.class_otc.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_delete_schedule_class_weeklyotc(self):
        """ Delete schedule class weeklyotc """
        query = self.delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleItemWeeklyOtc']['ok'], True)


    def test_delete_schedule_class_weeklyotc_anon_user(self):
        """ Delete schedule class weeklyotc denied for anon user """
        query = self.delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_delete_schedule_class_weeklyotc_permission_granted(self):
        """ Allow deleting schedule class weeklyotcs for users with permissions """
        query = self.delete_mutation
        variables = self.variables_delete
        
        # Give permissions
        user = self.class_otc.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleItemWeeklyOtc']['ok'], True)


    def test_delete_schedule_class_weeklyotc_permission_denied(self):
        """ Check delete schedule class weeklyotc permission denied error message """
        query = self.delete_mutation
        variables = self.variables_delete
        
        user = self.class_otc.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

