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


class GQLAccountScheduleEventTicket(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = [
        'app_settings.json',
        'finance_invoice_group.json',
        'finance_invoice_group_defaults.json',
        'finance_payment_methods.json'
    ]

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountscheduleeventticket'
        self.permission_add = 'add_accountscheduleeventticket'
        self.permission_change = 'change_accountscheduleeventticket'
        self.permission_delete = 'delete_accountscheduleeventticket'

        self.account_schedule_event_ticket = f.AccountScheduleEventTicketFactory.create()

        self.variables_query = {
            "account": to_global_id("accountId", self.account_schedule_event_ticket.account.id)
        }

        self.variables_create = {
            "input": {
                "account": to_global_id("AccountNode", self.account_schedule_event_ticket.account.id),
                "scheduleEventTicket": to_global_id("ScheduleEventTicketNode",
                                                    self.account_schedule_event_ticket.schedule_event_ticket.id)
            }
        }

        self.variables_update = {
            "input": {
                "id": to_global_id("AccountScheduleEventTicketNode", self.account_schedule_event_ticket.id),
                "cancelled": True,
                "paymentConfirmation": True,
                "infoMailSent": True
            }
        }

        self.variables_delete = {
            "input": {
                "id": to_global_id("AccountScheduleEventTicketNode", self.account_schedule_event_ticket.id),
            }
        }

        self.account_schedule_events_query = '''
  query AccountScheduleEventTickets($after: String, $before: String, $account: ID!) {
    accountScheduleEventTickets(first: 15, before: $before, after: $after, account: $account) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          cancelled
          paymentConfirmation
          infoMailSent
          account {
            id
          }
          scheduleEventTicket {
            id
            name
            scheduleEvent {
              id
              name
              dateStart
              organizationLocation {
                name
              }
            }
          }
          invoiceItems(first:1) {
            edges {
              node {
                financeInvoice {
                  id
                  invoiceNumber
                  status
                }
              }
            }
          }
        }
        
      }
    }
  }
'''
#
#         self.account_schedule_event_query = '''
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

        self.account_schedule_event_create_mutation = ''' 
    mutation CreateAccountScheduleEventTicket($input:CreateAccountScheduleEventTicketInput!) {
      createAccountScheduleEventTicket(input: $input) {
        accountScheduleEventTicket {
          id
          account {
            id
          }
          scheduleEventTicket {
            id
          }
          cancelled
          paymentConfirmation
          infoMailSent
        }
      }
    }
'''

        self.account_schedule_event_update_mutation = '''
  mutation UpdateAccountScheduleEventTicket($input:UpdateAccountScheduleEventTicketInput!) {
    updateAccountScheduleEventTicket(input: $input) {
      accountScheduleEventTicket {
        id
        account {
          id
        }
        scheduleEventTicket {
          id
        }
        cancelled
        paymentConfirmation
        infoMailSent
      }
    }
  }
'''

        self.account_schedule_event_delete_mutation = '''
  mutation DeleteAccountScheduleEventTicket($input: DeleteAccountScheduleEventTicketInput!) {
    deleteAccountScheduleEventTicket(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account account_schedule_events """
        query = self.account_schedule_events_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')
        self.assertEqual(
            data['accountScheduleEventTickets']['edges'][0]['node']['account']['id'],
            to_global_id("AccountNode", self.account_schedule_event_ticket.account.id)
        )
        self.assertEqual(
            data['accountScheduleEventTickets']['edges'][0]['node']['scheduleEventTicket']['id'],
            to_global_id("ScheduleEventTicketNode", self.account_schedule_event_ticket.schedule_event_ticket.id)
        )
        self.assertEqual(
            data['accountScheduleEventTickets']['edges'][0]['node']['cancelled'],
            self.account_schedule_event_ticket.cancelled
        )
        self.assertEqual(
            data['accountScheduleEventTickets']['edges'][0]['node']['paymentConfirmation'],
            self.account_schedule_event_ticket.payment_confirmation
        )
        self.assertEqual(
            data['accountScheduleEventTickets']['edges'][0]['node']['infoMailSent'],
            self.account_schedule_event_ticket.info_mail_sent
        )

    def test_query_not_listed_for_other_account_without_permission(self):
        """ Query list of account account_schedule_events - check permission denied """
        query = self.account_schedule_events_query
        other_user = self.account_schedule_event_ticket.schedule_event_ticket.schedule_event.instructor

        # Create regular user
        # user = get_user_model().objects.get(pk=self.account_schedule_event_ticket.account.id)
        executed = execute_test_client_api_query(query, other_user, variables=self.variables_query)
        data = executed.get('data')
        self.assertEqual(len(data['accountScheduleEventTickets']['edges']), 0)

    def test_query_not_listed_for_other_account_with_permission(self):
        """ Query list of account account_schedule_events - check permission denied """
        query = self.account_schedule_events_query
        other_user = self.account_schedule_event_ticket.schedule_event_ticket.schedule_event.instructor

        # Create regular user
        permission = Permission.objects.get(codename=self.permission_view)
        other_user.user_permissions.add(permission)
        other_user.save()
        executed = execute_test_client_api_query(query, other_user, variables=self.variables_query)
        data = executed.get('data')
        self.assertEqual(len(data['accountScheduleEventTickets']['edges']), 0)

    def test_query_list_for_own_account(self):
        """ Query list of account account_schedule_events - allow listing of event tickets for own account """
        query = self.account_schedule_events_query
        user = self.account_schedule_event_ticket.account

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')
        self.assertEqual(
            data['accountScheduleEventTickets']['edges'][0]['node']['account']['id'],
            to_global_id("AccountNode", self.account_schedule_event_ticket.account.id)
        )

    def test_query_anon_user(self):
        """ Query list of account account_schedule_events - anon user """
        query = self.account_schedule_events_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    # Query one is currently not implemented.

    #
    # def test_query_one(self):
    #     """ Query one account account_schedule_event as admin """
    #     account_schedule_event = f.AccountSubscriptionFactory.create()
    #
    #     variables = {
    #         "id": to_global_id("AccountSubscriptionNode", account_schedule_event.id),
    #         "accountId": to_global_id("AccountNode", account_schedule_event.account.id),
    #         "archived": False,
    #     }
    #
    #     # Now query single account_schedule_event and check
    #     executed = execute_test_client_api_query(self.account_schedule_event_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['accountSubscription']['account']['id'],
    #         to_global_id('AccountNode', account_schedule_event.account.id)
    #     )
    #     self.assertEqual(
    #         data['accountSubscription']['organizationSubscription']['id'],
    #         to_global_id('OrganizationSubscriptionNode', account_schedule_event.organization_account_schedule_event.id)
    #     )
    #     self.assertEqual(
    #         data['accountSubscription']['financePaymentMethod']['id'],
    #         to_global_id('FinancePaymentMethodNode', account_schedule_event.finance_payment_method.id)
    #     )
    #     self.assertEqual(data['accountSubscription']['dateStart'], str(account_schedule_event.date_start))
    #     self.assertEqual(data['accountSubscription']['dateEnd'], account_schedule_event.date_end)
    #     self.assertEqual(data['accountSubscription']['note'], account_schedule_event.note)
    #     self.assertEqual(data['accountSubscription']['registrationFeePaid'], account_schedule_event.registration_fee_paid)
    #
    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one account account_schedule_event """
    #     account_schedule_event = f.AccountSubscriptionFactory.create()
    #
    #     variables = {
    #         "id": to_global_id("AccountSubscriptionNode", account_schedule_event.id),
    #         "accountId": to_global_id("AccountNode", account_schedule_event.account.id),
    #         "archived": False,
    #     }
    #
    #     # Now query single account_schedule_event and check
    #     executed = execute_test_client_api_query(self.account_schedule_event_query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """
    #     # Create regular user
    #     account_schedule_event = f.AccountSubscriptionFactory.create()
    #     user = account_schedule_event.account
    #
    #     variables = {
    #         "id": to_global_id("AccountSubscriptionNode", account_schedule_event.id),
    #         "accountId": to_global_id("AccountNode", account_schedule_event.account.id),
    #         "archived": False,
    #     }
    #
    #     # Now query single account_schedule_event and check
    #     executed = execute_test_client_api_query(self.account_schedule_event_query, user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """
    #     account_schedule_event = f.AccountSubscriptionFactory.create()
    #     user = account_schedule_event.account
    #     permission = Permission.objects.get(codename='view_accounteventticket')
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #
    #     variables = {
    #         "id": to_global_id("AccountSubscriptionNode", account_schedule_event.id),
    #         "accountId": to_global_id("AccountNode", account_schedule_event.account.id),
    #         "archived": False,
    #     }
    #
    #     # Now query single account_schedule_event and check
    #     executed = execute_test_client_api_query(self.account_schedule_event_query, user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['accountSubscription']['organizationSubscription']['id'],
    #         to_global_id('OrganizationSubscriptionNode', account_schedule_event.organization_account_schedule_event.id)
    #     )
    #
    def test_create_account_schedule_event(self):
        """ Create an account account_schedule_event """
        query = self.account_schedule_event_create_mutation

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_create
        )
        data = executed.get('data')


        self.assertEqual(
            data['createAccountScheduleEventTicket']['accountScheduleEventTicket']['account']['id'],
            self.variables_create['input']['account']
        )
        self.assertEqual(
            data['createAccountScheduleEventTicket']['accountScheduleEventTicket']['scheduleEventTicket']['id'],
            self.variables_create['input']['scheduleEventTicket']
        )

    def test_create_account_schedule_event_anon_user(self):
        """ Don't allow creating account account_schedule_events for non-logged in users """
        query = self.account_schedule_event_create_mutation

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_account_schedule_event_permission_granted(self):
        """ Allow creating account_schedule_events for users with permissions """
        query = self.account_schedule_event_create_mutation

        # Create regular user
        user = self.account_schedule_event_ticket.account
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_create
        )
        data = executed.get('data')
        self.assertEqual(
            data['createAccountScheduleEventTicket']['accountScheduleEventTicket']['account']['id'],
            self.variables_create['input']['account']
        )

    def test_create_account_schedule_event_permission_denied(self):
        """ Check create account_schedule_event permission denied error message """
        query = self.account_schedule_event_create_mutation

        # Create regular user
        user = self.account_schedule_event_ticket.account
        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_account_schedule_event(self):
        """ Update a account_schedule_event """
        query = self.account_schedule_event_update_mutation

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_update
        )
        data = executed.get('data')

        self.assertEqual(
            data['updateAccountScheduleEventTicket']['accountScheduleEventTicket']['id'],
            self.variables_update['input']['id']
        )

        self.assertEqual(
            data['updateAccountScheduleEventTicket']['accountScheduleEventTicket']['cancelled'],
            self.variables_update['input']['cancelled']
        )

        self.assertEqual(
            data['updateAccountScheduleEventTicket']['accountScheduleEventTicket']['paymentConfirmation'],
            self.variables_update['input']['paymentConfirmation']
        )

        self.assertEqual(
            data['updateAccountScheduleEventTicket']['accountScheduleEventTicket']['infoMailSent'],
            self.variables_update['input']['infoMailSent']
        )

    def test_update_account_schedule_event_cancel_should_cancel_related_invoice(self):
        """ Update a account_schedule_event """
        query = self.account_schedule_event_update_mutation
        finance_invoice = f.FinanceInvoiceFactory.create(
            account=self.account_schedule_event_ticket.account
        )
        finance_invoice_item = f.FinanceInvoiceItemFactory.create(
            account_schedule_event_ticket=self.account_schedule_event_ticket,
            finance_invoice=finance_invoice
        )

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_update
        )
        data = executed.get('data')

        self.assertEqual(
            data['updateAccountScheduleEventTicket']['accountScheduleEventTicket']['id'],
            self.variables_update['input']['id']
        )

        # Check invoice was cancelled
        finance_invoice = models.FinanceInvoice.objects.get(id=finance_invoice.id)
        self.assertEqual(finance_invoice.status, 'CANCELLED')

    def test_update_account_schedule_event_cancel_attendances_related_to_ticket(self):
        """ Update a account_schedule_event - cancel attendanced related to ticket """
        query = self.account_schedule_event_update_mutation

        schedule_event_ticket = self.account_schedule_event_ticket.schedule_event_ticket
        schedule_event_ticket.full_event = False
        schedule_event_ticket.save()

        schedule_event_activity = f.ScheduleItemEventActivityFactory.create(
            schedule_event=schedule_event_ticket.schedule_event
        )

        schedule_item_attendance = f.ScheduleItemAttendanceScheduleEventFactory.create(
            account_schedule_event_ticket=self.account_schedule_event_ticket,
            schedule_item=schedule_event_activity,
            booking_status="BOOKED"
        )

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_update
        )
        data = executed.get('data')

        self.assertEqual(
            data['updateAccountScheduleEventTicket']['accountScheduleEventTicket']['id'],
            self.variables_update['input']['id']
        )

        # Refresh attendance object
        schedule_item_attendance = models.ScheduleItemAttendance.objects.get(id=schedule_item_attendance.id)
        self.assertEqual(schedule_item_attendance.booking_status, "CANCELLED")

    def test_update_account_schedule_event_uncancel_attendances_related_to_ticket(self):
        """ Update a account_schedule_event - uncancel attendances related to ticket """
        query = self.account_schedule_event_update_mutation

        schedule_event_ticket = self.account_schedule_event_ticket.schedule_event_ticket
        schedule_event_ticket.full_event = False
        schedule_event_ticket.save()

        schedule_event_activity = f.ScheduleItemEventActivityFactory.create(
            schedule_event=schedule_event_ticket.schedule_event
        )

        schedule_item_attendance = f.ScheduleItemAttendanceScheduleEventFactory.create(
            account_schedule_event_ticket=self.account_schedule_event_ticket,
            schedule_item=schedule_event_activity,
            booking_status="CANCELLED"
        )

        self.variables_update['input']['cancelled'] = False

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_update
        )
        data = executed.get('data')

        self.assertEqual(
            data['updateAccountScheduleEventTicket']['accountScheduleEventTicket']['id'],
            self.variables_update['input']['id']
        )
        self.assertEqual(
            data['updateAccountScheduleEventTicket']['accountScheduleEventTicket']['cancelled'],
            self.variables_update['input']['cancelled']
        )

        # Refresh attendance object
        schedule_item_attendance = models.ScheduleItemAttendance.objects.get(id=schedule_item_attendance.id)
        self.assertEqual(schedule_item_attendance.booking_status, "BOOKED")

    def test_update_account_schedule_event_uncancel_attendances_related_to_ticket_error_sold_out(self):
        """ Update a account_schedule_event - uncancel attendances related to ticket - error when sold out"""
        query = self.account_schedule_event_update_mutation

        schedule_event_ticket = self.account_schedule_event_ticket.schedule_event_ticket
        schedule_event_ticket.full_event = False
        schedule_event_ticket.save()

        schedule_event_activity = f.ScheduleItemEventActivityFactory.create(
            schedule_event=schedule_event_ticket.schedule_event,
            spaces=0
        )

        schedule_event_ticket_schedule_item = f.ScheduleEventTicketScheduleItemIncludedFactory.create(
            schedule_item=schedule_event_activity,
            schedule_event_ticket=schedule_event_ticket
        )

        schedule_item_attendance = f.ScheduleItemAttendanceScheduleEventFactory.create(
            account_schedule_event_ticket=self.account_schedule_event_ticket,
            schedule_item=schedule_event_activity,
            booking_status="CANCELLED"
        )

        self.variables_update['input']['cancelled'] = False

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_update
        )
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'This ticket is sold out')

    def test_update_account_schedule_event_anon_user(self):
        """ Don't allow updating account_schedule_events for non-logged in users """
        query = self.account_schedule_event_update_mutation

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_update
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_account_schedule_event_permission_granted(self):
        """ Allow updating account_schedule_events for users with permissions """
        query = self.account_schedule_event_update_mutation

        # Create regular user
        user = self.account_schedule_event_ticket.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()
        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_update
        )
        data = executed.get('data')
        self.assertEqual(
            data['updateAccountScheduleEventTicket']['accountScheduleEventTicket']['id'],
            self.variables_update['input']['id']
        )

    def test_update_account_schedule_event_permission_denied(self):
        """ Check update account_schedule_event permission denied error message """
        query = self.account_schedule_event_update_mutation

        # Create regular user
        user = self.account_schedule_event_ticket.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_update
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_account_schedule_event(self):
        """ Delete an account account_schedule_event """
        query = self.account_schedule_event_delete_mutation

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_delete
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountScheduleEventTicket']['ok'], True)

    def test_delete_account_schedule_event_anon_user(self):
        """ Delete account_schedule_event denied for anon user """
        query = self.account_schedule_event_delete_mutation

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_delete
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_account_schedule_event_permission_granted(self):
        """ Allow deleting account_schedule_events for users with permissions """
        query = self.account_schedule_event_delete_mutation

        # Give permissions
        user = self.account_schedule_event_ticket.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_delete
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountScheduleEventTicket']['ok'], True)

    def test_delete_account_schedule_event_permission_denied(self):
        """ Check delete account_schedule_event permission denied error message """
        query = self.account_schedule_event_delete_mutation
        user = self.account_schedule_event_ticket.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_delete
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
