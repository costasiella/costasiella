# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64
from decimal import Decimal

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

        # self.organization_location_room = f.OrganizationLocationRoomFactory.create()
        self.finance_tax_rate = f.FinanceTaxRateFactory.create()
        self.finance_glaccount = f.FinanceGLAccountFactory.create()
        self.finance_costcenter = f.FinanceCostCenterFactory.create()

        self.variables_create = {
            "input": {
                "displayPublic": True,
                "name": "New ticket",
                "description": "Ticket description here",
                "price": "100",
                "financeTaxRate": to_global_id("FinanceTaxRateNode", self.finance_tax_rate.pk),
                "financeGlaccount": to_global_id("FinanceGLAccountNode", self.finance_glaccount.pk),
                "financeCostcenter": to_global_id("FinanceCostCenterNode", self.finance_costcenter.pk)
            }
        }

        self.variables_update = {
            "input": {
                "displayPublic": True,
                "name": "Updated ticket",
                "description": "Ticket description here",
                "price": "100",
                "financeTaxRate": to_global_id("FinanceTaxRateNode", self.finance_tax_rate.pk),
                "financeGlaccount": to_global_id("FinanceGLAccountNode", self.finance_glaccount.pk),
                "financeCostcenter": to_global_id("FinanceCostCenterNode", self.finance_costcenter.pk)
            }
        }

        self.variables_delete = {
            "input": {}
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
          isEarlybirdPrice
          earlybirdDiscount
          earlybirdDiscountDisplay
          totalPrice
          totalPriceDisplay
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
    isSoldOut
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
  }
'''

        self.event_ticket_update_mutation = '''
  mutation UpdateScheduleEventTicket($input:UpdateScheduleEventTicketInput!) {
    updateScheduleEventTicket(input: $input) {
      scheduleEventTicket {
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
            format(schedule_event_ticket.price, ".2f")
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

    def test_query_earlybird_fields(self):
        """ Query list of event tickets - earlybird fields"""
        query = self.event_tickets_query
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        schedule_event_earlybird = f.ScheduleEventEarlybirdFactory.create(
            schedule_event=schedule_event_ticket.schedule_event
        )

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
            data['scheduleEventTickets']['edges'][0]['node']['isEarlybirdPrice'],
            True
        )
        self.assertEqual(
            data['scheduleEventTickets']['edges'][0]['node']['earlybirdDiscount'],
            "10.00"
        )
        self.assertEqual(
            data['scheduleEventTickets']['edges'][0]['node']['totalPrice'],
            "90.00"
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
        self.assertEqual(data['scheduleEventTicket']['price'], format(schedule_event_ticket.price, ".2f"))
        self.assertEqual(data['scheduleEventTicket']['financeTaxRate']['id'],
                         to_global_id('FinanceTaxRateNode', schedule_event_ticket.finance_tax_rate.pk))
        self.assertEqual(data['scheduleEventTicket']['financeGlaccount']['id'],
                         to_global_id('FinanceGLAccountNode', schedule_event_ticket.finance_glaccount.pk))
        self.assertEqual(data['scheduleEventTicket']['financeCostcenter']['id'],
                         to_global_id('FinanceCostCenterNode', schedule_event_ticket.finance_costcenter.pk))

    def test_query_one_sold_out(self):
        """ Query one schedule event ticket - sold out """

        account_schedule_event_ticket = f.AccountScheduleEventTicketFactory.create()
        schedule_event_ticket = account_schedule_event_ticket.schedule_event_ticket
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create(
            schedule_event=schedule_event_ticket.schedule_event,
            spaces=1
        )
        schedule_event_ticket_schedule_item = f.ScheduleEventTicketScheduleItemIncludedFactory.create(
            schedule_item=schedule_event_activity,
            schedule_event_ticket=schedule_event_ticket,
        )

        schedule_item_attendance = f.ScheduleItemAttendanceScheduleEventFactory.create(
            account_schedule_event_ticket=account_schedule_event_ticket,
            schedule_item=schedule_event_activity
        )

        # account = schedule_item_attendance.account

        # First query locations to get node id easily
        node_id = to_global_id('ScheduleEventTicketNode', schedule_event_ticket.pk)

        # Now query single ticket and check
        query = self.event_ticket_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['scheduleEventTicket']['scheduleEvent']['id'],
                         to_global_id('ScheduleEventNode', schedule_event_ticket.schedule_event.pk))
        self.assertEqual(data['scheduleEventTicket']['isSoldOut'], True)

    def test_query_one_not_sold_out(self):
        """ Query one schedule event ticket - not sold out """

        account_schedule_event_ticket = f.AccountScheduleEventTicketFactory.create()
        schedule_event_ticket = account_schedule_event_ticket.schedule_event_ticket
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create(
            schedule_event=schedule_event_ticket.schedule_event,
            spaces=10
        )
        schedule_event_ticket_schedule_item = f.ScheduleEventTicketScheduleItemIncludedFactory.create(
            schedule_item=schedule_event_activity,
            schedule_event_ticket=schedule_event_ticket,
        )

        schedule_item_attendance = f.ScheduleItemAttendanceScheduleEventFactory.create(
            account_schedule_event_ticket=account_schedule_event_ticket,
            schedule_item=schedule_event_activity
        )

        # account = schedule_item_attendance.account

        # First query locations to get node id easily
        node_id = to_global_id('ScheduleEventTicketNode', schedule_event_ticket.pk)

        # Now query single ticket and check
        query = self.event_ticket_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['scheduleEventTicket']['scheduleEvent']['id'],
                         to_global_id('ScheduleEventNode', schedule_event_ticket.schedule_event.pk))
        self.assertEqual(data['scheduleEventTicket']['isSoldOut'], False)

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

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        user = f.RegularUserFactory.create()
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        schedule_event_ticket.display_public = False
        schedule_event_ticket.save()
        node_id = to_global_id('ScheduleEventTicketNode', schedule_event_ticket.pk)

        # Now query single ticket and check
        query = self.event_ticket_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        schedule_event_ticket.display_public = False
        schedule_event_ticket.save()
        node_id = to_global_id('ScheduleEventTicketNode', schedule_event_ticket.pk)

        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        # Now query single ticket and check
        query = self.event_ticket_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['scheduleEventTicket']['scheduleEvent']['id'],
                         to_global_id('ScheduleEventNode', schedule_event_ticket.schedule_event.pk))

    def test_create_event_ticket(self):
        """ Create event ticket """
        query = self.event_ticket_create_mutation
        schedule_event = f.ScheduleEventFactory.create()

        variables = self.variables_create
        variables['input']['scheduleEvent'] = to_global_id("ScheduleEventNode", schedule_event.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
          data['createScheduleEventTicket']['scheduleEventTicket']['scheduleEvent']['id'],
          variables['input']['scheduleEvent']
        )
        self.assertEqual(
          data['createScheduleEventTicket']['scheduleEventTicket']['name'],
          variables['input']['name']
        )
        self.assertEqual(
          data['createScheduleEventTicket']['scheduleEventTicket']['displayPublic'],
          variables['input']['displayPublic']
        )
        self.assertEqual(
          data['createScheduleEventTicket']['scheduleEventTicket']['description'],
          variables['input']['description']
        )
        self.assertEqual(
          data['createScheduleEventTicket']['scheduleEventTicket']['price'],
          variables['input']['price']
        )
        self.assertEqual(
          data['createScheduleEventTicket']['scheduleEventTicket']['financeTaxRate']['id'],
          variables['input']['financeTaxRate']
        )
        self.assertEqual(
          data['createScheduleEventTicket']['scheduleEventTicket']['financeGlaccount']['id'],
          variables['input']['financeGlaccount']
        )
        self.assertEqual(
          data['createScheduleEventTicket']['scheduleEventTicket']['financeCostcenter']['id'],
          variables['input']['financeCostcenter']
        )

    def test_create_event_ticket_and_add_to_all_schedule_items(self):
        """ Create event ticket and check if entries in ScheduleEventTicketScheduleItem are created """
        query = self.event_ticket_create_mutation
        schedule_event_activity = f.ScheduleItemEventActivityFactory.create()
        schedule_event = schedule_event_activity.schedule_event

        variables = self.variables_create
        variables['input']['scheduleEvent'] = to_global_id("ScheduleEventNode", schedule_event.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
          data['createScheduleEventTicket']['scheduleEventTicket']['scheduleEvent']['id'],
          variables['input']['scheduleEvent']
        )

        # Check line is added to ScheduleEventTicketScheduleItem model
        rid = get_rid(data['createScheduleEventTicket']['scheduleEventTicket']['id'])
        schedule_event_ticket = models.ScheduleEventTicket.objects.get(pk=rid.id)
        schedule_event_ticket_schedule_item = models.ScheduleEventTicketScheduleItem.objects.last()
        self.assertEqual(schedule_event_ticket_schedule_item.schedule_event_ticket, schedule_event_ticket)
        self.assertEqual(schedule_event_ticket_schedule_item.schedule_item, schedule_event_activity)

    def test_create_event_ticket_anon_user(self):
        """ Don't allow creating event tickets for non-logged in users """
        query = self.event_ticket_create_mutation
        schedule_event = f.ScheduleEventFactory.create()

        variables = self.variables_create
        variables['input']['scheduleEvent'] = to_global_id("ScheduleEventNode", schedule_event.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_event_ticket_permission_granted(self):
        """ Allow creating event tickets for users with permissions """
        query = self.event_ticket_create_mutation
        schedule_event = f.ScheduleEventFactory.create()

        variables = self.variables_create
        variables['input']['scheduleEvent'] = to_global_id("ScheduleEventNode", schedule_event.pk)

        # Create regular user
        user = f.RegularUserFactory.create()
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
          data['createScheduleEventTicket']['scheduleEventTicket']['scheduleEvent']['id'],
          variables['input']['scheduleEvent']
        )

    def test_create_event_ticket_permission_denied(self):
        """ Check create event ticket permission denied error message """
        query = self.event_ticket_create_mutation
        schedule_event = f.ScheduleEventFactory.create()

        variables = self.variables_create
        variables['input']['scheduleEvent'] = to_global_id("ScheduleEventNode", schedule_event.pk)

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

    def test_update_event_ticket(self):
        """ Update event ticket """
        query = self.event_ticket_update_mutation
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id("ScheduleEventTicketNode", schedule_event_ticket.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
          data['updateScheduleEventTicket']['scheduleEventTicket']['id'],
          variables['input']['id']
        )
        self.assertEqual(
          data['updateScheduleEventTicket']['scheduleEventTicket']['name'],
          variables['input']['name']
        )
        self.assertEqual(
          data['updateScheduleEventTicket']['scheduleEventTicket']['displayPublic'],
          variables['input']['displayPublic']
        )
        self.assertEqual(
          data['updateScheduleEventTicket']['scheduleEventTicket']['description'],
          variables['input']['description']
        )
        self.assertEqual(
          data['updateScheduleEventTicket']['scheduleEventTicket']['price'],
          variables['input']['price']
        )
        self.assertEqual(
          data['updateScheduleEventTicket']['scheduleEventTicket']['financeTaxRate']['id'],
          variables['input']['financeTaxRate']
        )
        self.assertEqual(
          data['updateScheduleEventTicket']['scheduleEventTicket']['financeGlaccount']['id'],
          variables['input']['financeGlaccount']
        )
        self.assertEqual(
          data['updateScheduleEventTicket']['scheduleEventTicket']['financeCostcenter']['id'],
          variables['input']['financeCostcenter']
        )

    def test_update_event_ticket_anon_user(self):
        """ Don't allow updating event tickets for non-logged in users """
        query = self.event_ticket_update_mutation
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id("ScheduleEventTicketNode", schedule_event_ticket.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_event_ticket_permission_granted(self):
        """ Allow updating event tickets for users with permissions """
        query = self.event_ticket_update_mutation
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id("ScheduleEventTicketNode", schedule_event_ticket.pk)

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
          data['updateScheduleEventTicket']['scheduleEventTicket']['id'],
          variables['input']['id']
        )

    def test_update_event_ticket_permission_denied(self):
        """ Check update event ticket permission denied error message """
        query = self.event_ticket_update_mutation
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id("ScheduleEventTicketNode", schedule_event_ticket.pk)

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

    def test_delete_event_ticket_not_deletable(self):
        """ Event tickets with deletable set to false shouldn't be deletable """
        query = self.event_ticket_delete_mutation
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()

        variables = self.variables_delete
        variables['input']['id'] = to_global_id("ScheduleEventTicketNode", schedule_event_ticket.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleEventTicket']['ok'], False)

    def test_delete_event_ticket_deletable(self):
        """ Event tickets with deletable set to false shouldn't be deletable """
        query = self.event_ticket_delete_mutation
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        schedule_event_ticket.deletable = True
        schedule_event_ticket.full_event = False
        schedule_event_ticket.save()

        variables = self.variables_delete
        variables['input']['id'] = to_global_id("ScheduleEventTicketNode", schedule_event_ticket.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleEventTicket']['ok'], True)

    def test_delete_event_ticket_anon_user(self):
        """ Not possible to delete tickets as anon user """
        query = self.event_ticket_delete_mutation
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()

        variables = self.variables_delete
        variables['input']['id'] = to_global_id("ScheduleEventTicketNode", schedule_event_ticket.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_event_ticket_permission_granted(self):
        """ Allow deleting tickets for users with permissions """
        query = self.event_ticket_delete_mutation
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        schedule_event_ticket.deletable = True
        schedule_event_ticket.full_event = False
        schedule_event_ticket.save()

        variables = self.variables_delete
        variables['input']['id'] = to_global_id("ScheduleEventTicketNode", schedule_event_ticket.pk)

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleEventTicket']['ok'], True)

    def test_delete_event_ticket_permission_denied(self):
        """ Check delete ticket permission denied error message """
        query = self.event_ticket_delete_mutation
        schedule_event_ticket = f.ScheduleEventFullTicketFactory.create()
        schedule_event_ticket.deletable = True
        schedule_event_ticket.full_event = False
        schedule_event_ticket.save()

        variables = self.variables_delete
        variables['input']['id'] = to_global_id("ScheduleEventTicketNode", schedule_event_ticket.pk)

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
