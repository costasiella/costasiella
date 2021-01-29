# from graphql.error.located_error import GraphQLLocatedError
import graphql
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser, Permission

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema
from ..modules.gql_tools import get_rid


class GQLScheduleItem(TestCase):

    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['app_settings.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleitem'
        self.permission_add = 'add_scheduleitem'
        self.permission_change = 'change_scheduleitem'
        self.permission_delete = 'delete_scheduleitem'

        # self.account = f.RegularUserFactory.create()
        # self.organization_level = f.OrganizationLevelFactory.create()
        self.organization_location_room = f.OrganizationLocationRoomFactory.create()

        self.variables_create = {
            "input": {
                "organizationLocationRoom": to_global_id("OrganizationLocationRoomNode",
                                                         self.organization_location_room.id),
                "name": "Created event",
                "spaces": 20,
                "dateStart": "2021-01-01",
                "timeStart": "09:00:00",
                "timeEnd": "09:00:00",
                "frequencyType": "SPECIFIC",
                "frequencyInterval": 0,
                "scheduleItemType": "EVENT_ACTIVITY",
                "displayPublic": True
            }
        }

        self.variables_update = {
            "input": {
                # "organizationLevel": to_global_id("OrganizationLevelNode", self.organization_level.id),
                "name": "Updated event",
                "tagline": "Tagline for updated event",
                "preview": "Event preview updated",
                "description": "Event description updated",
                "infoMailContent": "hello world updated"
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.events_activities_query = '''
query ScheduleItem($before:String, $after:String, $scheduleEvent:ID!) {
  scheduleItems(first:100, before:$before, after:$after, scheduleEvent:$scheduleEvent) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      node {
        id
        displayPublic
        scheduleEvent {
          id
          name
        }
        organizationLocationRoom {
          id
          name
          organizationLocation {
            id
            name
          }
        }
        name
        spaces
        countAttendance
        dateStart
        timeStart
        timeEnd
        account {
          id
          fullName
        }
        account2 {
          id
          fullName
        }
      }
    }
  }
}
'''

        self.event_activity_query = '''
query ScheduleEventActivity($id:ID!) {
  scheduleItem(id: $id) {
    id
    scheduleEvent {
      id
    }
    displayPublic
    name
    spaces
    dateStart
    timeStart
    timeEnd
    organizationLocationRoom {
      id
      name
      organizationLocation {
        id
        name
      }
    }
    account {
      id
      fullName
    }
    account2 {
      id
      fullName
    }
  }
}
'''

        self.event_activity_create_mutation = ''' 
  mutation CreateScheduleItem($input:CreateScheduleItemInput!) {
    createScheduleItem(input: $input) {
      scheduleItem {
        id
        scheduleEvent {
          id
        }
        displayPublic
        name
        spaces
        dateStart
        timeStart
        timeEnd
        organizationLocationRoom {
          id
          name
          organizationLocation {
            id
            name
          }
        }
        account {
          id
          fullName
        }
        account2 {
          id
          fullName
        }
      }
    }
  }
'''

        self.event_activity_update_mutation = '''
  mutation UpdateScheduleItem($input:UpdateScheduleItemInput!) {
    updateScheduleItem(input: $input) {
      scheduleItem {
        id
        scheduleEvent {
          id
        }
        displayPublic
        name
        spaces
        dateStart
        timeStart
        timeEnd
        organizationLocationRoom {
          id
          name
          organizationLocation {
            id
            name
          }
        }
        account {
          id
          fullName
        }
        account2 {
          id
          fullName
        }
      }
    }
  }
'''

        self.event_activity_delete_mutation = '''
  mutation DeleteScheduleItem($input: DeleteScheduleItemInput!) {
    deleteScheduleItem(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of schedule events activities """
        query = self.events_activities_query
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        variables = {
            'scheduleEvent': to_global_id('ScheduleEventNode', schedule_event_activity.schedule_event.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleItems']['edges'][0]['node']['scheduleEvent']['id'],
                         to_global_id("ScheduleEventNode", schedule_event_activity.schedule_event.id))
        self.assertEqual(data['scheduleItems']['edges'][0]['node']['organizationLocationRoom']['id'],
                         to_global_id("OrganizationLocationRoomNode",
                                      schedule_event_activity.organization_location_room.id))
        self.assertEqual(data['scheduleItems']['edges'][0]['node']['name'], schedule_event_activity.name)
        self.assertEqual(data['scheduleItems']['edges'][0]['node']['spaces'], schedule_event_activity.spaces)
        self.assertEqual(data['scheduleItems']['edges'][0]['node']['dateStart'],
                         str(schedule_event_activity.date_start))
        self.assertEqual(data['scheduleItems']['edges'][0]['node']['timeStart'],
                         str(schedule_event_activity.time_start))
        self.assertEqual(data['scheduleItems']['edges'][0]['node']['account']['id'],
                         to_global_id('AccountNode', schedule_event_activity.account.id))
        self.assertEqual(data['scheduleItems']['edges'][0]['node']['account2']['id'],
                         to_global_id('AccountNode', schedule_event_activity.account_2.id))

    def test_query_permission_denied_dont_show_nonpublic_activities(self):
        """ Query list of event activities - check permission denied
        """
        query = self.events_activities_query
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        schedule_event_activity.display_public = False
        schedule_event_activity.save()
        variables = {
            'scheduleEvent': to_global_id('ScheduleEventNode', schedule_event_activity.schedule_event.id)
        }

        # Create regular user
        user = schedule_event_activity.account
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # No items should be listed
        self.assertEqual(len(data['scheduleItems']['edges']), 0)

    def test_query_permission_granted_show_nonpublic_activities(self):
        """ Query list of schedule event activities with view permission """
        query = self.events_activities_query
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        schedule_event_activity.display_public = False
        schedule_event_activity.save()
        variables = {
            'scheduleEvent': to_global_id('ScheduleEventNode', schedule_event_activity.schedule_event.id)
        }

        # Create regular user
        user = schedule_event_activity.account
        permission = Permission.objects.get(codename='view_scheduleitem')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # We should have some data
        self.assertEqual(data['scheduleItems']['edges'][0]['node']['scheduleEvent']['id'],
                         to_global_id("ScheduleEventNode", schedule_event_activity.schedule_event.id))

    def test_query_anon_user_show_public(self):
        """ Query list of schedule event activities - anon user """
        query = self.events_activities_query
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        variables = {
            'scheduleEvent': to_global_id('ScheduleEventNode', schedule_event_activity.schedule_event.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        data = executed.get('data')

        # We should have some data
        self.assertEqual(data['scheduleItems']['edges'][0]['node']['scheduleEvent']['id'],
                         to_global_id("ScheduleEventNode", schedule_event_activity.schedule_event.id))

    def test_query_anon_user_dont_show_nonpublic(self):
        """ Query list of schedule event activities - anon user """
        query = self.events_activities_query
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        schedule_event_activity.display_public = False
        schedule_event_activity.save()
        variables = {
            'scheduleEvent': to_global_id('ScheduleEventNode', schedule_event_activity.schedule_event.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        data = executed.get('data')

        # No items should be listed
        self.assertEqual(len(data['scheduleItems']['edges']), 0)

    def test_query_one(self):
        """ Query one schedule event activity as admin """
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()

        variables = {
            "id": to_global_id("ScheduleItemNode", schedule_event_activity.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.event_activity_query, self.admin_user, variables=variables)
        data = executed.get('data')

        print(executed)

        self.assertEqual(data['scheduleItem']['scheduleEvent']['id'],
                         to_global_id("ScheduleEventNode", schedule_event_activity.schedule_event.id))
        self.assertEqual(data['scheduleItem']['organizationLocationRoom']['id'],
                         to_global_id("OrganizationLocationRoomNode",
                                      schedule_event_activity.organization_location_room.id))
        self.assertEqual(data['scheduleItem']['name'], schedule_event_activity.name)
        self.assertEqual(data['scheduleItem']['spaces'], schedule_event_activity.spaces)
        self.assertEqual(data['scheduleItem']['dateStart'], str(schedule_event_activity.date_start))
        self.assertEqual(data['scheduleItem']['timeStart'], str(schedule_event_activity.time_start))
        self.assertEqual(data['scheduleItem']['account']['id'],
                         to_global_id("AccountNode", schedule_event_activity.account.id))
        self.assertEqual(data['scheduleItem']['account2']['id'],
                         to_global_id("AccountNode", schedule_event_activity.account_2.id))

    def test_query_one_anon_user_nonpublic_not_allowed(self):
        """ Deny permission for anon users Query one schedule event activity """
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        schedule_event_activity.display_public = False
        schedule_event_activity.save()

        variables = {
            "id": to_global_id("ScheduleItemNode", schedule_event_activity.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.event_activity_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_anon_user_public_allowed(self):
        """ Deny permission for anon users Query one schedule event activity """
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()

        variables = {
            "id": to_global_id("ScheduleItemNode", schedule_event_activity.id),
        }

        executed = execute_test_client_api_query(self.event_activity_query, self.anon_user, variables=variables)
        data = executed['data']
        self.assertEqual(data['scheduleItem']['scheduleEvent']['id'],
                         to_global_id("ScheduleEventNode", schedule_event_activity.schedule_event.id))

    def test_query_one_display_nonpublic_permission_denied(self):
        """ Don't list non-public event activity when user lacks authorization """
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        schedule_event_activity.display_public = False
        schedule_event_activity.save()
        # Create regular user
        user = f.RegularUserFactory()

        variables = {
            "id": to_global_id("ScheduleItemNode", schedule_event_activity.id),
        }

        # Now query single event and check
        executed = execute_test_client_api_query(self.event_activity_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_display_nonpublic_permission_granted(self):
        """ Respond with data when user has permission """
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        schedule_event_activity.display_public = False
        schedule_event_activity.save()
        # Create regular user
        user = f.RegularUserFactory()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        variables = {
            "id": to_global_id("ScheduleItemNode", schedule_event_activity.id),
        }

        # Now query single schedule event and check
        executed = execute_test_client_api_query(self.event_activity_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['scheduleItem']['scheduleEvent']['id'],
                         to_global_id("ScheduleEventNode", schedule_event_activity.schedule_event.id))

    def test_create_schedule_event_activity(self):
        """ Create a schedule event activity """
        query = self.event_activity_create_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_create['input']['scheduleEvent'] = to_global_id('ScheduleEventNode', schedule_event.id)
        self.variables_create['input']['account'] = to_global_id('AccountNode', schedule_event.teacher.id)
        self.variables_create['input']['account2'] = to_global_id('AccountNode', schedule_event.teacher_2.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_create
        )
        data = executed.get('data')

        self.assertEqual(data['createScheduleItem']['scheduleItem']['scheduleEvent']['id'],
                         self.variables_create['input']['scheduleEvent'])
        self.assertEqual(data['createScheduleItem']['scheduleItem']['organizationLocationRoom']['id'],
                         self.variables_create['input']['organizationLocationRoom'])
        self.assertEqual(data['createScheduleItem']['scheduleItem']['account']['id'],
                         self.variables_create['input']['account'])
        self.assertEqual(data['createScheduleItem']['scheduleItem']['account2']['id'],
                         self.variables_create['input']['account2'])
        self.assertEqual(data['createScheduleItem']['scheduleItem']['displayPublic'],
                         self.variables_create['input']['displayPublic'])
        self.assertEqual(data['createScheduleItem']['scheduleItem']['name'],
                         self.variables_create['input']['name'])
        self.assertEqual(data['createScheduleItem']['scheduleItem']['spaces'],
                         self.variables_create['input']['spaces'])
        self.assertEqual(data['createScheduleItem']['scheduleItem']['dateStart'],
                         self.variables_create['input']['dateStart'])
        self.assertEqual(data['createScheduleItem']['scheduleItem']['timeStart'],
                         self.variables_create['input']['timeStart'])

    # def test_create_event_activity_anon_user(self):
    #     """ Don't allow creating schedule events for non-logged in users """
    #     query = self.event_activity_create_mutation
    #     schedule_event = f.ScheduleEventFactory.create()
        # "organizationLocationRoom": to_global_id("OrganizationLocationRoomNode",
        #                                          self.organization_location_room.id),
        # self.variables_create['input']['scheduleEvent'] = to_global_id('ScheduleEventNode', schedule_event.id)
        # self.variables_create['input']['account'] = to_global_id('AccountNode', schedule_event.teacher.id)
        # self.variables_create['input']['account2'] = to_global_id('AccountNode', schedule_event.teacher_2.id)
        #
        # executed = execute_test_client_api_query(
        #     query,
        #     self.anon_user,
        #     variables=self.variables_create
        # )
        # print("#############")
        # print(executed)
        # print("&&&&&&&&&&&")
        # data = executed.get('data')
        # errors = executed.get('errors')
        # self.assertEqual(errors[0]['message'], 'Not logged in!')

    # def test_create_schedule_event_activity_permission_granted(self):
    #     """ Allow creating event activity for users with permissions """
    #     query = self.event_activity_create_mutation
    #     schedule_event = f.ScheduleEventFactory.create()
    #     self.variables_create['input']['scheduleEvent'] = to_global_id('ScheduleEventNode', schedule_event.id)
    #     self.variables_create['input']['account'] = to_global_id('AccountNode', schedule_event.teacher.id)
    #     self.variables_create['input']['account2'] = to_global_id('AccountNode', schedule_event.teacher_2.id)
    #
    #     account = f.RegularUserFactory.create()
    #     # Create regular user
    #     user = account
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=self.variables_create
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createScheduleItem']['scheduleItem']['scheduleEvent']['id'],
    #                      self.variables_create['input']['scheduleEvent'])
    #
    # def test_create_event_permission_denied(self):
    #     """ Check create event activity permission denied error message """
    #     query = self.event_activity_create_mutation
    #     schedule_event = f.ScheduleEventFactory.create()
    #     self.variables_create['input']['scheduleEvent'] = to_global_id('ScheduleEventNode', schedule_event.id)
    #     self.variables_create['input']['account'] = to_global_id('AccountNode', schedule_event.teacher.id)
    #     self.variables_create['input']['account2'] = to_global_id('AccountNode', schedule_event.teacher_2.id)
    #
    #     account = f.RegularUserFactory.create()
    #     # Create regular user
    #     user = account
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=self.variables_create
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    # def test_update_event(self):
    #     """ Update an event """
    #     query = self.event_update_mutation
    #     schedule_event = f.ScheduleEventFactory.create()
    #     self.variables_update['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=self.variables_update
    #     )
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['updateScheduleEvent']['scheduleEvent']['name'],
    #                      self.variables_update['input']['name'])
    #     self.assertEqual(data['updateScheduleEvent']['scheduleEvent']['tagline'],
    #                      self.variables_update['input']['tagline'])
    #     self.assertEqual(data['updateScheduleEvent']['scheduleEvent']['preview'],
    #                      self.variables_update['input']['preview'])
    #     self.assertEqual(data['updateScheduleEvent']['scheduleEvent']['description'],
    #                      self.variables_update['input']['description'])
    #     self.assertEqual(data['updateScheduleEvent']['scheduleEvent']['infoMailContent'],
    #                      self.variables_update['input']['infoMailContent'])
    #
    # def test_update_event_anon_user(self):
    #     """ Don't allow updating events for non-logged in users """
    #     query = self.event_update_mutation
    #     schedule_event = f.ScheduleEventFactory.create()
    #     self.variables_update['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=self.variables_update
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    # def test_update_event_permission_granted(self):
    #     """ Allow updating event for users with permissions """
    #     query = self.event_update_mutation
    #     schedule_event = f.ScheduleEventFactory.create()
    #     self.variables_update['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)
    #
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=self.variables_update
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateScheduleEvent']['scheduleEvent']['name'],
    #                      self.variables_update['input']['name'])
    #
    # def test_update_invoice_permission_denied(self):
    #     """ Check update event permission denied error message """
    #     query = self.event_update_mutation
    #     schedule_event = f.ScheduleEventFactory.create()
    #     self.variables_update['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)
    #
    #     user = f.RegularUserFactory.create()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=self.variables_update
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    # def test_archive_event(self):
    #     """ Archive an event """
    #     query = self.event_archive_mutation
    #     schedule_event = f.ScheduleEventFactory.create()
    #     self.variables_archive['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=self.variables_archive
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveScheduleEvent']['scheduleEvent']['id'],
    #                      to_global_id('ScheduleEventNode', schedule_event.id))
    #     self.assertEqual(data['archiveScheduleEvent']['scheduleEvent']['archived'],
    #                      self.variables_archive['input']['archived'])
    #
    # def test_archive_event_anon_user(self):
    #     """ Archive event denied for anon user """
    #     query = self.event_archive_mutation
    #     schedule_event = f.ScheduleEventFactory.create()
    #     self.variables_archive['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=self.variables_archive
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    # def test_archive_event_permission_granted(self):
    #     """ Allow archive events for users with permissions """
    #     query = self.event_archive_mutation
    #     schedule_event = f.ScheduleEventFactory.create()
    #     self.variables_archive['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)
    #
    #     # Give permissions
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=self.variables_archive
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveScheduleEvent']['scheduleEvent']['archived'],
    #                      self.variables_archive['input']['archived'])
    #
    # def test_archive_event_permission_denied(self):
    #     """ Check archive event permission denied error message """
    #     query = self.event_archive_mutation
    #     schedule_event = f.ScheduleEventFactory.create()
    #     self.variables_archive['input']['id'] = to_global_id('ScheduleEventNode', schedule_event.id)
    #
    #     user = f.RegularUserFactory.create()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=self.variables_archive
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')