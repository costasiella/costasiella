# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from graphql_relay import to_global_id

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema
from ..modules.gql_tools import get_rid


class GQLScheduleEventTicketScheduleItem(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleeventticketscheduleitem'
        self.permission_add = 'add_scheduleeventticketscheduleitem'
        self.permission_change = 'change_scheduleeventticketscheduleitem'
        self.permission_delete = 'delete_scheduleeventticketscheduleitem'

        self.schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        self.schedule_event_activity = f.ScheduleItemEventActivityFactory.create(
            schedule_event=self.schedule_event_ticket.schedule_event
        )
        self.schedule_event_ticket_schedule_item = f.ScheduleEventTicketScheduleItemIncludedFactory.create(
            schedule_item=self.schedule_event_activity,
            schedule_event_ticket=self.schedule_event_ticket
        )

        self.variables_query_list = {
            "scheduleEventTicket": to_global_id('ScheduleEventTicketNode', self.schedule_event_ticket.id)
        }

        self.variables_update = {
            "input": {
                "id": to_global_id("ScheduleEventTicketScheduleItemNode", self.schedule_event_ticket_schedule_item.id),
                "included": False
            }
        }

        self.event_ticket_activities_query = '''
    query ScheduleEventTicketScheduleItem($before:String, $after:String, $scheduleEventTicket:ID!) {
      scheduleEventTicketScheduleItems(
        first: 100, 
        before: $before, 
        after: $after, 
        scheduleEventTicket:$scheduleEventTicket,
        orderBy: "dateStart"        
    ) {
        pageInfo {
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
        }
        edges {
          node {
            id
            included
            scheduleEventTicket {
              id
              name
              fullEvent
            }
            scheduleItem {
              id
              name
            }
          }
        }
      }
    }
'''

        self.event_ticket_schedule_item_update_mutation = '''
  mutation UpdateScheduleEventTicketScheduleItem($input:UpdateScheduleEventTicketScheduleItemInput!) {
    updateScheduleEventTicketScheduleItem(input: $input) {
      scheduleEventTicketScheduleItem {
        id
        included
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of schedule items for event ticket """
        query = self.event_ticket_activities_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['scheduleEventTicketScheduleItems']['edges'][0]['node']['scheduleItem']['id'],
            to_global_id("ScheduleItemNode", self.schedule_event_activity.id)
        )
        self.assertEqual(
            data['scheduleEventTicketScheduleItems']['edges'][0]['node']['scheduleEventTicket']['id'],
            self.variables_query_list['scheduleEventTicket']
        )
        self.assertEqual(
            data['scheduleEventTicketScheduleItems']['edges'][0]['node']['included'],
            self.schedule_event_ticket_schedule_item.included
        )

    def test_query_permission_denied(self):
        """ Query list of schedule items for event ticket - permission denied for non public tickets"""
        query = self.event_ticket_activities_query
        self.schedule_event_ticket.display_public = False
        self.schedule_event_ticket.save()

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(len(data['scheduleEventTicketScheduleItems']['edges']), 0)

    def test_query_permission_granted(self):
        """ Query list of activities for non-public ticket tickets with permission """
        query = self.event_ticket_activities_query
        self.schedule_event_ticket.display_public = False
        self.schedule_event_ticket.save()

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename="view_scheduleeventticket")
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['scheduleEventTicketScheduleItems']['edges'][0]['node']['included'],
            self.schedule_event_ticket_schedule_item.included
        )

    def test_query_anon_user(self):
        """ Permission denied when listing activities for ticket as anon user """
        query = self.event_ticket_activities_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_event_ticket_schedule_item_remove_included_from_full_event_error(self):
        """ Update event ticket schedule item not possible for full event ticket"""
        query = self.event_ticket_schedule_item_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'],
                         'For a full event ticket, all schedule items for this event are included!')

    def test_update_event_ticket_schedule_item(self):
        """ Update event ticket schedule item """
        query = self.event_ticket_schedule_item_update_mutation
        self.schedule_event_ticket.full_event = False
        self.schedule_event_ticket.save()

        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
            data['updateScheduleEventTicketScheduleItem']['scheduleEventTicketScheduleItem']['included'],
            variables['input']['included']
        )

    def test_update_event_ticket_schedule_item_add_attendance(self):
        """ Update event ticket schedule item """
        query = self.event_ticket_schedule_item_update_mutation
        self.schedule_event_ticket.full_event = False
        self.schedule_event_ticket.save()
        account_schedule_event_ticket = f.AccountScheduleEventTicketFactory.create(
            schedule_event_ticket=self.schedule_event_ticket
        )

        variables = self.variables_update
        variables['input']['included'] = True

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
            data['updateScheduleEventTicketScheduleItem']['scheduleEventTicketScheduleItem']['included'],
            variables['input']['included']
        )

        # Was an attendance item created?
        schedule_item_attendance = models.ScheduleItemAttendance.objects.last()
        self.assertEqual(schedule_item_attendance.account_schedule_event_ticket,
                         account_schedule_event_ticket)
        self.assertEqual(schedule_item_attendance.schedule_item, self.schedule_event_activity)

    def test_update_event_ticket_schedule_item_remove_attendance(self):
        """ Update event ticket schedule item """
        query = self.event_ticket_schedule_item_update_mutation

        account_schedule_event_ticket = f.AccountScheduleEventTicketFactory.create(
            schedule_event_ticket=self.schedule_event_ticket
        )
        schedule_event_ticket = account_schedule_event_ticket.schedule_event_ticket
        schedule_event_ticket.full_event = False
        schedule_event_ticket.save()

        schedule_item_attendance = f.ScheduleItemAttendanceScheduleEventFactory.create(
            account_schedule_event_ticket=account_schedule_event_ticket,
            schedule_item=self.schedule_event_activity
        )

        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
            data['updateScheduleEventTicketScheduleItem']['scheduleEventTicketScheduleItem']['included'],
            variables['input']['included']
        )

        # Check attendance was removed
        qs = models.ScheduleItemAttendance.objects.filter(schedule_item=self.schedule_event_activity)
        self.assertEqual(qs.count(), 0)

    def test_update_event_ticket_schedule_item_anon_user(self):
        """ Don't allow updating event ticket schedule items for non-logged in users """
        query = self.event_ticket_schedule_item_update_mutation
        self.schedule_event_ticket.full_event = False
        self.schedule_event_ticket.save()

        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_event_ticket_permission_granted(self):
        """ Allow updating event ticket schedule items for users with permissions """
        query = self.event_ticket_schedule_item_update_mutation
        self.schedule_event_ticket.full_event = False
        self.schedule_event_ticket.save()

        variables = self.variables_update

        # Create regular user
        user = f.RegularUserFactory.create()
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
            data['updateScheduleEventTicketScheduleItem']['scheduleEventTicketScheduleItem']['included'],
            variables['input']['included']
        )

    def test_update_event_ticket_scheudle_item_permission_denied(self):
        """ Check update event ticket schedule item permission denied error message """
        query = self.event_ticket_schedule_item_update_mutation
        self.schedule_event_ticket.full_event = False
        self.schedule_event_ticket.save()

        variables = self.variables_update

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
