# from graphql.error.located_error import GraphQLLocatedError
import graphql
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
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
        self.organization_level = f.OrganizationLevelFactory.create()
        self.organization_location = f.OrganizationLocationFactory.create()

        self.variables_create = {
            "input": {
                "organizationLocation": to_global_id("OrganizationLocationNode", self.organization_location.id),
                "organizationLevel": to_global_id("OrganizationLevelNode", self.organization_level.id),
                "name": "Created event",
                "tagline": "Tagline for event",
                "preview": "Event preview",
                "description": "Event description",
                "infoMailContent": "hello world"
            }
        }

        self.variables_update = {
            "input": {
                "organizationLocation": to_global_id("OrganizationLocationNode", self.organization_location.id),
                "organizationLevel": to_global_id("OrganizationLevelNode", self.organization_level.id),
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
query ScheduleEventActivity($before:String, $after:String, $id:ID!) {
  scheduleItem(id: $id) {
    id
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
  accounts(first: 100, before: $before, after: $after, isActive:true, teacher: true) {
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
    }
    edges {
      node {
        id
        fullName
      }
    }
  }
  organizationLocationRooms(first: 100, before: $before, after: $after, archived: false) {
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
    }
    edges {
      node {
        id
        name
        organizationLocation {
          id 
          name
        }
      }
    }
  }
}
'''

        self.event_activity_create_mutation = ''' 
  mutation CreateScheduleItem($input:CreateScheduleItemInput!) {
    createScheduleItem(input: $input) {
      scheduleItem {
        id
      }
    }
  }
'''

        self.event_activity_update_mutation = '''
  mutation UpdateScheduleItem($input:UpdateScheduleItemInput!) {
    updateScheduleItem(input: $input) {
      scheduleItem {
        id
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

    # def test_query_anon_user(self):
    #     """ Query list of schedule events - anon user """
    #     query = self.events_query
    #     schedule_event = f.ScheduleEventFactory.create()
    #
    #     executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
    #     print(executed)
    #     data = executed.get('data')
    #
    #     # List all events
    #     self.assertEqual(data['scheduleEvents']['edges'][0]['node']['organizationLocation']['id'],
    #                      to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))
    #
    # def test_query_one(self):
    #     """ Query one schedule event as admin """
    #     schedule_event = f.ScheduleEventFactory.create()
    #
    #     variables = {
    #         "id": to_global_id("ScheduleEventNode", schedule_event.id),
    #     }
    #
    #     # Now query single invoice and check
    #     executed = execute_test_client_api_query(self.event_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['scheduleEvent']['organizationLocation']['id'],
    #                      to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))
    #     self.assertEqual(data['scheduleEvent']['name'], schedule_event.name)
    #     self.assertEqual(data['scheduleEvent']['tagline'], schedule_event.tagline)
    #     self.assertEqual(data['scheduleEvent']['preview'], schedule_event.preview)
    #     self.assertEqual(data['scheduleEvent']['description'], schedule_event.description)
    #     self.assertEqual(data['scheduleEvent']['infoMailContent'],
    #                      schedule_event.info_mail_content)
    #     self.assertEqual(data['scheduleEvent']['organizationLevel']['id'],
    #                      to_global_id("OrganizationLevelNode", schedule_event.organization_level.id))
    #     self.assertEqual(data['scheduleEvent']['teacher']['id'],
    #                      to_global_id("AccountNode", schedule_event.teacher.id))
    #     self.assertEqual(data['scheduleEvent']['teacher2']['id'],
    #                      to_global_id("AccountNode", schedule_event.teacher_2.id))
    #
    # def test_query_one_anon_user_nonpublic_not_allowed(self):
    #     """ Deny permission for anon users Query one schedule event """
    #     schedule_event = f.ScheduleEventFactory.create()
    #     schedule_event.display_public = False
    #     schedule_event.display_shop = False
    #     schedule_event.save()
    #
    #     variables = {
    #         "id": to_global_id("ScheduleEventNode", schedule_event.id),
    #     }
    #
    #     # Now query single invoice and check
    #     executed = execute_test_client_api_query(self.event_query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    # def test_query_one_anon_user_public_allowed(self):
    #     """ Deny permission for anon users Query one schedule event """
    #     schedule_event = f.ScheduleEventFactory.create()
    #
    #     variables = {
    #         "id": to_global_id("ScheduleEventNode", schedule_event.id),
    #     }
    #
    #     # Now query single invoice and check
    #     executed = execute_test_client_api_query(self.event_query, self.anon_user, variables=variables)
    #     data = executed['data']
    #     self.assertEqual(data['scheduleEvent']['organizationLocation']['id'],
    #                      to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))
    #
    # def test_query_one_display_nonpublic_permission_denied(self):
    #     """ Don't list non-public events when user lacks authorization """
    #     schedule_event = f.ScheduleEventFactory.create()
    #     schedule_event.display_public = False
    #     schedule_event.display_shop = False
    #     schedule_event.save()
    #     # Create regular user
    #     user = f.RegularUserFactory()
    #
    #     variables = {
    #         "id": to_global_id("ScheduleEventNode", schedule_event.id),
    #     }
    #
    #     # Now query single event and check
    #     executed = execute_test_client_api_query(self.event_query, user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    # def test_query_one_display_nonpublic_permission_granted(self):
    #     """ Respond with data when user has permission """
    #     schedule_event = f.ScheduleEventFactory.create()
    #     schedule_event.display_public = False
    #     schedule_event.display_shop = False
    #     schedule_event.save()
    #     # Create regular user
    #     user = f.RegularUserFactory()
    #     permission = Permission.objects.get(codename=self.permission_view)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     variables = {
    #         "id": to_global_id("ScheduleEventNode", schedule_event.id),
    #     }
    #
    #     # Now query single schedule event and check
    #     executed = execute_test_client_api_query(self.event_query, user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(data['scheduleEvent']['organizationLocation']['id'],
    #                      to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))
    #
    # def test_create_schedule_event(self):
    #     """ Create a schedule event """
    #     query = self.event_create_mutation
    #     teacher = f.TeacherFactory.create()
    #     teacher2 = f.Teacher2Factory.create()
    #     self.variables_create['input']['teacher'] = to_global_id('AccountNode', teacher.id)
    #     self.variables_create['input']['teacher2'] = to_global_id('AccountNode', teacher2.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=self.variables_create
    #     )
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['createScheduleEvent']['scheduleEvent']['name'],
    #                      self.variables_create['input']['name'])
    #     self.assertEqual(data['createScheduleEvent']['scheduleEvent']['tagline'],
    #                      self.variables_create['input']['tagline'])
    #     self.assertEqual(data['createScheduleEvent']['scheduleEvent']['preview'],
    #                      self.variables_create['input']['preview'])
    #     self.assertEqual(data['createScheduleEvent']['scheduleEvent']['description'],
    #                      self.variables_create['input']['description'])
    #     self.assertEqual(data['createScheduleEvent']['scheduleEvent']['infoMailContent'],
    #                      self.variables_create['input']['infoMailContent'])
    #     self.assertEqual(data['createScheduleEvent']['scheduleEvent']['teacher']['id'],
    #                      self.variables_create['input']['teacher'])
    #     self.assertEqual(data['createScheduleEvent']['scheduleEvent']['teacher2']['id'],
    #                      self.variables_create['input']['teacher2'])
    #
    # def test_create_schedule_event_full_ticket_added(self):
    #     """ Create a schedule event and check if the full event ticket is added """
    #     query = self.event_create_mutation
    #     teacher = f.TeacherFactory.create()
    #     teacher2 = f.Teacher2Factory.create()
    #     self.variables_create['input']['teacher'] = to_global_id('AccountNode', teacher.id)
    #     self.variables_create['input']['teacher2'] = to_global_id('AccountNode', teacher2.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=self.variables_create
    #     )
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['createScheduleEvent']['scheduleEvent']['name'],
    #                      self.variables_create['input']['name'])
    #
    #     gql_id = data['createScheduleEvent']['scheduleEvent']['id']
    #     rid = get_rid(gql_id)
    #
    #     schedule_event = models.ScheduleEvent.objects.get(pk=rid.id)
    #     schedule_event_ticket = models.ScheduleEventTicket.objects.filter(schedule_event=schedule_event).first()
    #
    #     self.assertEqual(schedule_event_ticket.schedule_event, schedule_event)
    #     self.assertEqual(schedule_event_ticket.name, "Full event")
    #
    # def test_create_event_anon_user(self):
    #     """ Don't allow creating schedule events for non-logged in users """
    #     query = self.event_create_mutation
    #     teacher = f.TeacherFactory.create()
    #     teacher2 = f.Teacher2Factory.create()
    #     self.variables_create['input']['teacher'] = to_global_id('AccountNode', teacher.id)
    #     self.variables_create['input']['teacher2'] = to_global_id('AccountNode', teacher2.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=self.variables_create
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    # def test_create_location_permission_granted(self):
    #     """ Allow creating events for users with permissions """
    #     query = self.event_create_mutation
    #     teacher = f.TeacherFactory.create()
    #     teacher2 = f.Teacher2Factory.create()
    #     self.variables_create['input']['teacher'] = to_global_id('AccountNode', teacher.id)
    #     self.variables_create['input']['teacher2'] = to_global_id('AccountNode', teacher2.id)
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
    #     self.assertEqual(data['createScheduleEvent']['scheduleEvent']['name'],
    #                      self.variables_create['input']['name'])
    #
    # def test_create_event_permission_denied(self):
    #     """ Check create event permission denied error message """
    #     query = self.event_create_mutation
    #     teacher = f.TeacherFactory.create()
    #     teacher2 = f.Teacher2Factory.create()
    #     self.variables_create['input']['teacher'] = to_global_id('AccountNode', teacher.id)
    #     self.variables_create['input']['teacher2'] = to_global_id('AccountNode', teacher2.id)
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
