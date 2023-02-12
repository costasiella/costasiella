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
        self.permission_view_attendances = 'view_scheduleitemattendance'
        self.permission_view_enrollments = 'view_scheduleitemenrollment'
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
                "name": "Created event activity",
                "spaces": 20,
                "dateStart": "2021-01-01",
                "timeStart": "09:00:00",
                "timeEnd": "11:00:00",
                "frequencyType": "SPECIFIC",
                "frequencyInterval": 0,
                "scheduleItemType": "EVENT_ACTIVITY",
                "displayPublic": True
            }
        }

        self.variables_update = {
            "input": {
                "organizationLocationRoom": to_global_id("OrganizationLocationRoomNode",
                                                         self.organization_location_room.id),
                "name": "Updated event activity",
                "spaces": 20,
                "dateStart": "2021-01-01",
                "timeStart": "10:00:00",
                "timeEnd": "12:00:00",
                "displayPublic": True
            }
        }

        self.variables_delete = {
            "input": {}
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

        self.schedule_item_enrollments_query = '''
      query ScheduleItemEnrollments($after: String, $before: String, $scheduleItem: ID!, $dateEnd_Isnull:Boolean) {
    scheduleItem(id:$scheduleItem) {
      id
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
      displayPublic
      enrollments(first: 1000, before: $before, after: $after, scheduleItem: $scheduleItem, dateEnd_Isnull: $dateEnd_Isnull) {
        pageInfo {
          startCursor
          endCursor
          hasNextPage
          hasPreviousPage
        }
        edges {
          node {
            id 
            dateStart
            dateEnd
            accountSubscription {
              id
              dateStart
              dateEnd
              organizationSubscription {
                id
                name
              }
              account {
                id
                fullName
              }            
            }
          }
        }
      }
    }
  }
'''

        self.schedule_item_attendances_query = '''
  query ScheduleItemAttendances($after: String, $before: String, $scheduleItem: ID!) {
    scheduleItem(id:$scheduleItem) {
      id
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
      displayPublic
      attendances(first: 1000, before: $before, after: $after, scheduleItem: $scheduleItem) {
        pageInfo {
          startCursor
          endCursor
          hasNextPage
          hasPreviousPage
        }
        edges {
          node {
            id 
            date
            account {
              id
            }
          }
        }
      }
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


    def test_query_one_schedule_item_enrollments_permission_denied(self):
        """ Query schedule item with enrollments - ensure enrollment permissions are checked """
        schedule_item_enrollment = f.ScheduleItemEnrollmentFactory.create()
        # Create regular user
        user = schedule_item_enrollment.account_subscription.account

        variables = {
            "scheduleItem": to_global_id("ScheduleItemNode", schedule_item_enrollment.schedule_item.id),
        }

        # Now query single event and check
        executed = execute_test_client_api_query(self.schedule_item_enrollments_query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')
        self.assertEqual(errors[0]['path'], ['scheduleItem', 'enrollments'])


    def test_query_one_schedule_item_enrollments_permission_granted(self):
        """ Query schedule item with enrollments - ensure enrollment permissions are checked """
        schedule_item_enrollment = f.ScheduleItemEnrollmentFactory.create()
        # Create regular user
        user = schedule_item_enrollment.account_subscription.account
        permission = Permission.objects.get(codename=self.permission_view_enrollments)
        user.user_permissions.add(permission)

        variables = {
            "scheduleItem": to_global_id("ScheduleItemNode", schedule_item_enrollment.schedule_item.id),
        }

        # Now query single event and check
        executed = execute_test_client_api_query(self.schedule_item_enrollments_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['scheduleItem']['enrollments']['edges'][0]['node']['id'],
                         to_global_id("ScheduleItemEnrollmentNode", schedule_item_enrollment.id))


    def test_query_one_schedule_item_attendances_permission_denied(self):
        """ Query schedule item with attendancess - ensure attendance permissions are checked """
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        # Create regular user
        user = schedule_item_attendance.account

        variables = {
            "scheduleItem": to_global_id("ScheduleItemNode", schedule_item_attendance.schedule_item.id),
        }

        # Now query single event and check
        executed = execute_test_client_api_query(self.schedule_item_attendances_query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')
        self.assertEqual(errors[0]['path'], ['scheduleItem', 'attendances'])


    def test_query_one_schedule_item_attendances_permission_granted(self):
        """ Query schedule item with attendances - ensure attendance permissions are checked """
        schedule_item_attendance = f.ScheduleItemAttendanceClasspassFactory.create()
        # Create regular user
        user = schedule_item_attendance.account
        permission = Permission.objects.get(codename=self.permission_view_attendances)
        user.user_permissions.add(permission)

        variables = {
            "scheduleItem": to_global_id("ScheduleItemNode", schedule_item_attendance.schedule_item.id),
        }

        # Now query single event and check
        executed = execute_test_client_api_query(self.schedule_item_attendances_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['scheduleItem']['attendances']['edges'][0]['node']['id'],
                         to_global_id("ScheduleItemAttendanceNode", schedule_item_attendance.id))


    def test_create_schedule_event_activity(self):
        """ Create a schedule event activity """
        query = self.event_activity_create_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_create['input']['scheduleEvent'] = to_global_id('ScheduleEventNode', schedule_event.id)
        self.variables_create['input']['account'] = to_global_id('AccountNode', schedule_event.instructor.id)
        self.variables_create['input']['account2'] = to_global_id('AccountNode', schedule_event.instructor_2.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_create
        )
        data = executed.get('data')

        # Check general data for schedule item
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

    def test_create_schedule_event_activity_add_attendance_full_event(self):
        """ Create a schedule event activity - add attendance """
        query = self.event_activity_create_mutation

        account_schedule_event_ticket = f.AccountScheduleEventTicketFactory.create()
        schedule_event_ticket = account_schedule_event_ticket.schedule_event_ticket
        schedule_event = schedule_event_ticket.schedule_event

        self.variables_create['input']['scheduleEvent'] = to_global_id('ScheduleEventNode', schedule_event.id)
        self.variables_create['input']['account'] = to_global_id('AccountNode', schedule_event.instructor.id)
        self.variables_create['input']['account2'] = to_global_id('AccountNode', schedule_event.instructor_2.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_create
        )
        data = executed.get('data')

        # Check general data for schedule item
        self.assertEqual(data['createScheduleItem']['scheduleItem']['scheduleEvent']['id'],
                         self.variables_create['input']['scheduleEvent'])

        # Check an attendance record was added
        rid = get_rid(data['createScheduleItem']['scheduleItem']['id'])
        schedule_item = models.ScheduleItem.objects.get(pk=rid.id)
        schedule_item_attendance = models.ScheduleItemAttendance.objects.first()

        self.assertEqual(schedule_item_attendance.account_schedule_event_ticket, account_schedule_event_ticket)
        self.assertEqual(schedule_item_attendance.schedule_item, schedule_item)

    def test_create_schedule_event_activity_set_included_true_for_full_event_ticket(self):
        """ Create a schedule event activity and check if an object with includes set to true is created in
         the ScheduleEventTicketScheduleItem model """
        query = self.event_activity_create_mutation
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        schedule_event = schedule_event_ticket.schedule_event
        self.variables_create['input']['scheduleEvent'] = to_global_id('ScheduleEventNode', schedule_event.id)
        self.variables_create['input']['account'] = to_global_id('AccountNode', schedule_event.instructor.id)
        self.variables_create['input']['account2'] = to_global_id('AccountNode', schedule_event.instructor_2.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_create
        )
        data = executed.get('data')

        # Check general data for schedule item
        self.assertEqual(data['createScheduleItem']['scheduleItem']['scheduleEvent']['id'],
                         self.variables_create['input']['scheduleEvent'])

        # Check that "included" was set to true
        schedule_event_ticket_schedule_item = models.ScheduleEventTicketScheduleItem.objects.last()
        self.assertEqual(schedule_event_ticket_schedule_item.included, True)

    def test_create_schedule_event_activity_check_added_to_schedule_event_ticket_schedule_item_model(self):
        """ Create a schedule event activity and check if an object with includes set to true is created in
         the ScheduleEventTicketScheduleItem model """
        query = self.event_activity_create_mutation
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        schedule_event = schedule_event_ticket.schedule_event
        self.variables_create['input']['scheduleEvent'] = to_global_id('ScheduleEventNode', schedule_event.id)
        self.variables_create['input']['account'] = to_global_id('AccountNode', schedule_event.instructor.id)
        self.variables_create['input']['account2'] = to_global_id('AccountNode', schedule_event.instructor_2.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_create
        )
        data = executed.get('data')

        # Check general data for schedule item
        self.assertEqual(data['createScheduleItem']['scheduleItem']['scheduleEvent']['id'],
                         self.variables_create['input']['scheduleEvent'])

        # Check line is added to ScheduleEventTicketScheduleItem model
        rid = get_rid(data['createScheduleItem']['scheduleItem']['id'])
        schedule_item = models.ScheduleItem.objects.get(pk=rid.id)
        schedule_event_ticket_schedule_item = models.ScheduleEventTicketScheduleItem.objects.last()
        self.assertEqual(schedule_event_ticket_schedule_item.schedule_event_ticket, schedule_event_ticket)
        self.assertEqual(schedule_event_ticket_schedule_item.schedule_item, schedule_item)

    def test_create_schedule_event_activity_set_event_dates_and_times(self):
        """ Check of activity dates & times are set on schedule event """
        query = self.event_activity_create_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_create['input']['scheduleEvent'] = to_global_id('ScheduleEventNode', schedule_event.id)
        self.variables_create['input']['account'] = to_global_id('AccountNode', schedule_event.instructor.id)
        self.variables_create['input']['account2'] = to_global_id('AccountNode', schedule_event.instructor_2.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_create
        )
        data = executed.get('data')

        # Check general data for schedule item
        self.assertEqual(data['createScheduleItem']['scheduleItem']['scheduleEvent']['id'],
                         self.variables_create['input']['scheduleEvent'])

        # Check event dates & times after refetching schedule event
        schedule_event = models.ScheduleEvent.objects.get(pk=schedule_event.pk)
        self.assertEqual(str(schedule_event.date_start), self.variables_create['input']['dateStart'])
        self.assertEqual(str(schedule_event.time_start), self.variables_create['input']['timeStart'])
        self.assertEqual(str(schedule_event.date_end), self.variables_create['input']['dateStart'])
        self.assertEqual(str(schedule_event.time_end), self.variables_create['input']['timeEnd'])

    def test_create_event_activity_anon_user(self):
        """ Don't allow creating schedule events for non-logged in users """
        query = self.event_activity_create_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_create['input']['scheduleEvent'] = to_global_id('ScheduleEventNode', schedule_event.id)
        self.variables_create['input']['account'] = to_global_id('AccountNode', schedule_event.instructor.id)
        self.variables_create['input']['account2'] = to_global_id('AccountNode', schedule_event.instructor_2.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_schedule_event_activity_permission_granted(self):
        """ Allow creating event activity for users with permissions """
        query = self.event_activity_create_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_create['input']['scheduleEvent'] = to_global_id('ScheduleEventNode', schedule_event.id)
        self.variables_create['input']['account'] = to_global_id('AccountNode', schedule_event.instructor.id)
        self.variables_create['input']['account2'] = to_global_id('AccountNode', schedule_event.instructor_2.id)

        account = f.RegularUserFactory.create()
        # Create regular user
        user = account
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_create
        )
        data = executed.get('data')
        self.assertEqual(data['createScheduleItem']['scheduleItem']['scheduleEvent']['id'],
                         self.variables_create['input']['scheduleEvent'])

    def test_create_event_activity_permission_denied(self):
        """ Check create event activity permission denied error message """
        query = self.event_activity_create_mutation
        schedule_event = f.ScheduleEventFactory.create()
        self.variables_create['input']['scheduleEvent'] = to_global_id('ScheduleEventNode', schedule_event.id)
        self.variables_create['input']['account'] = to_global_id('AccountNode', schedule_event.instructor.id)
        self.variables_create['input']['account2'] = to_global_id('AccountNode', schedule_event.instructor_2.id)

        account = f.RegularUserFactory.create()
        # Create regular user
        user = account
        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_schedule_event_activity(self):
        """ Update an event activity """
        query = self.event_activity_update_mutation
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        self.variables_update['input']['id'] = to_global_id('ScheduleItemNode', schedule_event_activity.id)
        self.variables_update['input']['account'] = to_global_id('AccountNode',
                                                                 schedule_event_activity.schedule_event.instructor.id)
        self.variables_update['input']['account2'] = to_global_id('AccountNode',
                                                                  schedule_event_activity.schedule_event.instructor_2.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_update
        )
        data = executed.get('data')

        self.assertEqual(data['updateScheduleItem']['scheduleItem']['organizationLocationRoom']['id'],
                         self.variables_update['input']['organizationLocationRoom'])
        self.assertEqual(data['updateScheduleItem']['scheduleItem']['account']['id'],
                         self.variables_update['input']['account'])
        self.assertEqual(data['updateScheduleItem']['scheduleItem']['account2']['id'],
                         self.variables_update['input']['account2'])
        self.assertEqual(data['updateScheduleItem']['scheduleItem']['displayPublic'],
                         self.variables_update['input']['displayPublic'])
        self.assertEqual(data['updateScheduleItem']['scheduleItem']['name'],
                         self.variables_update['input']['name'])
        self.assertEqual(data['updateScheduleItem']['scheduleItem']['spaces'],
                         self.variables_update['input']['spaces'])
        self.assertEqual(data['updateScheduleItem']['scheduleItem']['dateStart'],
                         self.variables_update['input']['dateStart'])
        self.assertEqual(data['updateScheduleItem']['scheduleItem']['timeStart'],
                         self.variables_update['input']['timeStart'])

    def test_update_schedule_event_activity_set_event_dates_and_times(self):
        """ Check of activity dates & times are set on schedule event """
        query = self.event_activity_update_mutation
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        self.variables_update['input']['id'] = to_global_id('ScheduleItemNode', schedule_event_activity.id)
        self.variables_update['input']['account'] = to_global_id('AccountNode',
                                                                 schedule_event_activity.schedule_event.instructor.id)
        self.variables_update['input']['account2'] = to_global_id('AccountNode',
                                                                  schedule_event_activity.schedule_event.instructor_2.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_update
        )
        data = executed.get('data')

        # Check general data for schedule item
        self.assertEqual(data['updateScheduleItem']['scheduleItem']['organizationLocationRoom']['id'],
                         self.variables_update['input']['organizationLocationRoom'])

        # Check event dates & times after refetching schedule event
        schedule_event = models.ScheduleEvent.objects.get(pk=schedule_event_activity.schedule_event.pk)
        self.assertEqual(str(schedule_event.date_start), self.variables_update['input']['dateStart'])
        self.assertEqual(str(schedule_event.time_start), self.variables_update['input']['timeStart'])
        self.assertEqual(str(schedule_event.date_end), self.variables_update['input']['dateStart'])
        self.assertEqual(str(schedule_event.time_end), self.variables_update['input']['timeEnd'])

    def test_update_event_anon_user(self):
        """ Don't allow updating event activities for non-logged in users """
        query = self.event_activity_update_mutation
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        self.variables_update['input']['id'] = to_global_id('ScheduleItemNode', schedule_event_activity.id)
        self.variables_update['input']['account'] = to_global_id('AccountNode',
                                                                 schedule_event_activity.schedule_event.instructor.id)
        self.variables_update['input']['account2'] = to_global_id('AccountNode',
                                                                  schedule_event_activity.schedule_event.instructor_2.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_update
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_event_permission_granted(self):
        """ Allow updating event activity for users with permissions """
        query = self.event_activity_update_mutation
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        self.variables_update['input']['id'] = to_global_id('ScheduleItemNode', schedule_event_activity.id)
        self.variables_update['input']['account'] = to_global_id('AccountNode',
                                                                 schedule_event_activity.schedule_event.instructor.id)
        self.variables_update['input']['account2'] = to_global_id('AccountNode',
                                                                  schedule_event_activity.schedule_event.instructor_2.id)

        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_update
        )
        data = executed.get('data')
        self.assertEqual(data['updateScheduleItem']['scheduleItem']['organizationLocationRoom']['id'],
                         self.variables_update['input']['organizationLocationRoom'])

    def test_delete_event_activity(self):
        """ Delete schedule event acivity (schedule item) """
        query = self.event_activity_delete_mutation
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        self.variables_delete['input']['id'] = to_global_id('ScheduleItemNode', schedule_event_activity.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_delete
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleItem']['ok'], True)

    def test_delete_event_activity_check_delete_attendance(self):
        """ Delete schedule event acivity (schedule item)
        Check attendance linked to activity is deleted as well"""
        query = self.event_activity_delete_mutation
        account_schedule_event_ticket = f.AccountScheduleEventTicketFactory.create()
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create(
            schedule_event=account_schedule_event_ticket.schedule_event_ticket.schedule_event
        )

        schedule_item_attendance = f.ScheduleItemAttendanceScheduleEventFactory.create(
            account_schedule_event_ticket=account_schedule_event_ticket,
            schedule_item=schedule_event_activity
        )

        self.variables_delete['input']['id'] = to_global_id('ScheduleItemNode', schedule_event_activity.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_delete
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleItem']['ok'], True)

        qs = models.ScheduleItemAttendance.objects.filter(schedule_item=schedule_event_activity)
        self.assertEqual(qs.count(), 0)

    def test_delete_event_activity_anon_user(self):
        """ Delete schedule event acivity (schedule item) for anon user """
        query = self.event_activity_delete_mutation
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        self.variables_delete['input']['id'] = to_global_id('ScheduleItemNode', schedule_event_activity.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_delete
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_event_activity_permission_granted(self):
        """ Allow archive event activity for users with permissions """
        query = self.event_activity_delete_mutation
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        self.variables_delete['input']['id'] = to_global_id('ScheduleItemNode', schedule_event_activity.id)

        # Give permissions
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_delete
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleItem']['ok'], True)

    def test_delete_event_activity_permission_denied(self):
        """ Check delete event activity permission denied error message """
        query = self.event_activity_delete_mutation
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        self.variables_delete['input']['id'] = to_global_id('ScheduleItemNode', schedule_event_activity.id)

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_delete
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
