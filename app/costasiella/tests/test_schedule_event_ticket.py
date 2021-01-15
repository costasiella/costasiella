# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema

from graphql_relay import to_global_id


class GQLScheduleEventTicket(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleeventticket'
        self.permission_add = 'add_scheduleeventticket'
        self.permission_change = 'change_scheduleeventticket'
        self.permission_delete = 'delete_scheduleeventticket'

        # self.schedule_event = f.ScheduleEventFactory.create()
        # self.organization_location_room = f.OrganizationLocationRoomFactory.create()

        self.variables_create = {
            "input": {
                "displayPublic": True,
                "name": "First room",
            }
        }

        self.variables_update = {
            "input": {
                "displayPublic": True,
                "name": "Updated room",
            }
        }

        self.variables_delete = {
            "input": {
                "archived": True,
            }
        }

        self.event_tickets_query = '''
  query ScheduleEventTickets($before:String, $after:String, $scheduleEvent:ID!) {
    scheduleEventTickets(first: 100, before:$before, after:$after, scheduleEvent:$scheduleEvent) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          scheduleEvent {
            id
          }
          fullEvent
          deletable
          displayPublic
          name
          description
          price
          priceDisplay
          isSoldOut
          financeTaxRate {
            id
            name
          }
          financeGlaccount {
            id
            name
          }
          financeCostcenter {
            id
            name
          }
        }
      }
    }
  }
'''

        self.event_ticket_query = '''
query ScheduleEventTicket($id:ID!) {
  scheduleEventTicket(id: $id) {
    id
    deletable
    fullEvent
    displayPublic
    name
    description
    price
    scheduleEvent {
      id
    }
    financeTaxRate {
      id
      name
    }
    financeGlaccount {
      id
      name
    }
    financeCostcenter {
      id
      name
    }
  }
}
'''

        self.event_ticket_create_mutation = ''' 
  mutation CreateScheduleEventTicket($input:CreateScheduleEventTicketInput!) {
    createScheduleEventTicket(input: $input) {
      scheduleEventTicket {
        id
      }
    }
  }
'''

        self.event_ticket_update_mutation = '''
  mutation UpdateScheduleEventTicket($input:UpdateScheduleEventTicketInput!) {
    updateScheduleEventTicket(input: $input) {
      scheduleEventTicket {
        id
      }
    }
  }
'''

        self.event_ticket_delete_mutation = '''
  mutation DeleteScheduleEventTicket($input: DeleteScheduleEventTicketInput!) {
    deleteScheduleEventTicket(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of event tickets """
        query = self.event_tickets_query
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()

        variables = {
            'scheduleEvent': to_global_id('ScheduleEventNode', schedule_event_ticket.schedule_event.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['scheduleEventTickets']['edges'][0]['node']['scheduleEvent']['id'],
            variables['scheduleEvent']
        )
        self.assertEqual(
            data['scheduleEventTickets']['edges'][0]['node']['fullEvent'],
            schedule_event_ticket.full_event
        )
        self.assertEqual(
            data['scheduleEventTickets']['edges'][0]['node']['deletable'],
            schedule_event_ticket.deletable
        )
        self.assertEqual(
            data['scheduleEventTickets']['edges'][0]['node']['displayPublic'],
            schedule_event_ticket.display_public
        )
        self.assertEqual(
            data['scheduleEventTickets']['edges'][0]['node']['name'],
            schedule_event_ticket.name
        )
        self.assertEqual(
            data['scheduleEventTickets']['edges'][0]['node']['description'],
            schedule_event_ticket.description
        )
        self.assertEqual(
            data['scheduleEventTickets']['edges'][0]['node']['price'],
            schedule_event_ticket.price
        )
        self.assertEqual(
            data['scheduleEventTickets']['edges'][0]['node']['financeTaxRate']['id'],
            to_global_id('FinanceTaxRateNode', schedule_event_ticket.finance_tax_rate.id)
        )
        self.assertEqual(
            data['scheduleEventTickets']['edges'][0]['node']['financeGlaccount']['id'],
            to_global_id('FinanceGLAccountNode', schedule_event_ticket.finance_glaccount.id)
        )
        self.assertEqual(
            data['scheduleEventTickets']['edges'][0]['node']['financeCostcenter']['id'],
            to_global_id('FinanceCostCenterNode', schedule_event_ticket.finance_costcenter.id)
        )

    def test_query_permission_denied(self):
        """ Query list of event tickets """
        query = self.event_tickets_query
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()

        variables = {
            'scheduleEvent': to_global_id('ScheduleEventNode', schedule_event_ticket.schedule_event.pk)
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # Public tickets only
        non_public_found = False
        for item in data['scheduleEventTickets']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)

    def test_query_permission_granted(self):
        """ Query list of public & non public tickets with permission """
        query = self.event_tickets_query
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        non_public_schedule_event_ticket = f.ScheduleEventFullTicketFactory.build()
        non_public_schedule_event_ticket.schedule_event = schedule_event_ticket.schedule_event
        non_public_schedule_event_ticket.finance_tax_rate = None
        non_public_schedule_event_ticket.finance_costcenter = None
        non_public_schedule_event_ticket.finance_glaccount = None
        non_public_schedule_event_ticket.display_public = False
        non_public_schedule_event_ticket.save()

        variables = {
            'scheduleEvent': to_global_id('ScheduleEventNode', schedule_event_ticket.schedule_event.pk)
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all locations, including non public
        non_public_found = False
        for item in data['scheduleEventTickets']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        # Assert non public locations are listed
        self.assertEqual(non_public_found, True)

    def test_query_anon_user(self):
        """ Query list of public event tickets for anon users """
        query = self.event_tickets_query
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        non_public_schedule_event_ticket = f.ScheduleEventFullTicketFactory.build()
        non_public_schedule_event_ticket.schedule_event = schedule_event_ticket.schedule_event
        non_public_schedule_event_ticket.finance_tax_rate = None
        non_public_schedule_event_ticket.finance_costcenter = None
        non_public_schedule_event_ticket.finance_glaccount = None
        non_public_schedule_event_ticket.display_public = False
        non_public_schedule_event_ticket.save()

        variables = {
            'scheduleEvent': to_global_id('ScheduleEventNode', schedule_event_ticket.schedule_event.pk)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        data = executed.get('data')

        # Ensure only public tickets are found
        non_public_found = False
        for item in data['scheduleEventTickets']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)

    def test_query_one(self):
        """ Query one schedule event ticket """
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('ScheduleEventTicketNode', schedule_event_ticket.pk)

        # Now query single location and check
        query = self.event_ticket_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['scheduleEventTicket']['scheduleEvent']['id'],
                         to_global_id('ScheduleEventNode', schedule_event_ticket.schedule_event.pk))
        self.assertEqual(data['scheduleEventTicket']['fullEvent'], schedule_event_ticket.full_event)
        self.assertEqual(data['scheduleEventTicket']['deletable'], schedule_event_ticket.deletable)
        self.assertEqual(data['scheduleEventTicket']['displayPublic'], schedule_event_ticket.display_public)
        self.assertEqual(data['scheduleEventTicket']['name'], schedule_event_ticket.name)
        self.assertEqual(data['scheduleEventTicket']['description'], schedule_event_ticket.description)
        self.assertEqual(data['scheduleEventTicket']['price'], schedule_event_ticket.price)
        self.assertEqual(data['scheduleEventTicket']['financeTaxRate']['id'],
                         to_global_id('FinanceTaxRateNode', schedule_event_ticket.finance_tax_rate.pk))
        self.assertEqual(data['scheduleEventTicket']['financeGlaccount']['id'],
                         to_global_id('FinanceGLAccountNode', schedule_event_ticket.finance_glaccount.pk))
        self.assertEqual(data['scheduleEventTicket']['financeCostcenter']['id'],
                         to_global_id('FinanceCostCenterNode', schedule_event_ticket.finance_costcenter.pk))

    def test_query_one_anon_user_public(self):
        """ Grant permission for anon users Query public ticket """
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        node_id = to_global_id('ScheduleEventTicketNode', schedule_event_ticket.pk)

        # Now query single location and check
        query = self.event_ticket_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')

        # Now query single location and check
        query = self.event_ticket_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['scheduleEventTicket']['scheduleEvent']['id'],
                         to_global_id('ScheduleEventNode', schedule_event_ticket.schedule_event.pk))

    def test_query_one_anon_user_nonpublic(self):
        """ Deny permission for anon users Query non-public ticket """
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        schedule_event_ticket.display_public = False
        schedule_event_ticket.save()
        node_id = to_global_id('ScheduleEventTicketNode', schedule_event_ticket.pk)

        # Now query single location and check
        query = self.event_ticket_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')

        # Now query single location and check
        query = self.event_ticket_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    #
    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     location_room = f.OrganizationLocationRoomFactory.create()
    #
    #     # First query locations to get node id easily
    #     node_id = to_global_id('OrganizationLocationRoomNode', location_room.pk)
    #
    #     # Now query single location and check
    #     query = self.location_room_query
    #     executed = execute_test_client_api_query(query, user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    #
    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_scheduleeventticket')
    #     user.user_permissions.add(permission)
    #     user.save()
    #     location_room = f.OrganizationLocationRoomFactory.create()
    #
    #     # First query locations to get node id easily
    #     node_id = to_global_id('OrganizationLocationRoomNode', location_room.pk)
    #
    #     # Now query single location and check
    #     query = self.location_room_query
    #     executed = execute_test_client_api_query(query, user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['organizationLocationRoom']['name'], location_room.name)
    #
    #
    # def test_create_location_room(self):
    #     """ Create a location room """
    #     query = self.location_room_create_mutation
    #     variables = self.variables_create
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #
    #     data = executed.get('data')
    #     self.assertEqual(
    #       data['createOrganizationLocationRoom']['organizationLocationRoom']['organizationLocation']['id'],
    #       variables['input']['organizationLocation'])
    #     self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['name'], variables['input']['name'])
    #     self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['archived'], False)
    #     self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['displayPublic'], variables['input']['displayPublic'])
    #
    #
    # def test_create_location_room_anon_user(self):
    #     """ Don't allow creating locations rooms for non-logged in users """
    #     query = self.location_room_create_mutation
    #     variables = self.variables_create
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    #
    # def test_create_location_room_permission_granted(self):
    #     """ Allow creating location rooms for users with permissions """
    #     query = self.location_room_create_mutation
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     variables = self.variables_create
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(
    #       data['createOrganizationLocationRoom']['organizationLocationRoom']['organizationLocation']['id'],
    #       variables['input']['organizationLocation'])
    #     self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['name'], variables['input']['name'])
    #     self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['archived'], False)
    #     self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['displayPublic'], variables['input']['displayPublic'])
    #
    #
    # def test_create_location_room_permission_denied(self):
    #     """ Check create location room permission denied error message """
    #     query = self.location_room_create_mutation
    #     variables = self.variables_create
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    #
    # def test_update_location_room(self):
    #     """ Update a location room """
    #     query = self.location_room_update_mutation
    #     variables = self.variables_update
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #
    #     data = executed.get('data')
    #     self.assertEqual(data['updateOrganizationLocationRoom']['organizationLocationRoom']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateOrganizationLocationRoom']['organizationLocationRoom']['displayPublic'], variables['input']['displayPublic'])
    #
    #
    # def test_update_location_room_anon_user(self):
    #     """ Don't allow updating location rooms for non-logged in users """
    #     query = self.location_room_update_mutation
    #     variables = self.variables_update
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    #
    # def test_update_location_room_permission_granted(self):
    #     """ Allow updating location rooms for users with permissions """
    #     query = self.location_room_update_mutation
    #     variables = self.variables_update
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateOrganizationLocationRoom']['organizationLocationRoom']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateOrganizationLocationRoom']['organizationLocationRoom']['displayPublic'], variables['input']['displayPublic'])
    #
    #
    # def test_update_location_room_permission_denied(self):
    #     """ Check update location room permission denied error message """
    #     query = self.location_room_update_mutation
    #     variables = self.variables_update
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    #
    # def test_archive_location_room(self):
    #     """ Archive a location room"""
    #     query = self.location_room_archive_mutation
    #     variables = self.variables_archive
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveOrganizationLocationRoom']['organizationLocationRoom']['archived'], variables['input']['archived'])
    #
    #
    # def test_archive_location_room_anon_user(self):
    #     """ Archive a location room """
    #     query = self.location_room_archive_mutation
    #     variables = self.variables_archive
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    #
    # def test_archive_location_room_permission_granted(self):
    #     """ Allow archiving locations for users with permissions """
    #     query = self.location_room_archive_mutation
    #     variables = self.variables_archive
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveOrganizationLocationRoom']['organizationLocationRoom']['archived'], variables['input']['archived'])
    #
    #
    # def test_archive_location_room_permission_denied(self):
    #     """ Check archive location room permission denied error message """
    #     query = self.location_room_archive_mutation
    #     variables = self.variables_archive
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
