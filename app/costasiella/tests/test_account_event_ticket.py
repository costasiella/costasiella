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
        other_user = self.account_schedule_event_ticket.schedule_event_ticket.schedule_event.teacher

        # Create regular user
        # user = get_user_model().objects.get(pk=self.account_schedule_event_ticket.account.id)
        executed = execute_test_client_api_query(query, other_user, variables=self.variables_query)
        data = executed.get('data')
        self.assertEqual(len(data['accountScheduleEventTickets']['edges']), 0)

    def test_query_not_listed_for_other_account_with_permission(self):
        """ Query list of account account_schedule_events - check permission denied """
        query = self.account_schedule_events_query
        other_user = self.account_schedule_event_ticket.schedule_event_ticket.schedule_event.teacher

        # Create regular user
        permission = Permission.objects.get(codename=self.permission_view)
        other_user.user_permissions.add(permission)
        other_user.save()
        executed = execute_test_client_api_query(query, other_user, variables=self.variables_query)
        data = executed.get('data')
        self.assertEqual(len(data['accountScheduleEventTickets']['edges']), 0)

    def test_query_not_list_for_own_account(self):
        """ Query list of account account_schedule_events - allow listing of event tickets for own account """
        query = self.account_schedule_events_query
        user = self.account_schedule_event_ticket.account

        # Create regular user
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
        print("**************")
        print(executed)
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
    #
    # def test_update_account_schedule_event(self):
    #     """ Update a account_schedule_event """
    #     query = self.account_schedule_event_update_mutation
    #     account_schedule_event = f.AccountSubscriptionFactory.create()
    #     organization_account_schedule_event = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', account_schedule_event.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_account_schedule_event.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #
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
    #
    # def test_update_account_schedule_event_anon_user(self):
    #     """ Don't allow updating account_schedule_events for non-logged in users """
    #     query = self.account_schedule_event_update_mutation
    #     account_schedule_event = f.AccountSubscriptionFactory.create()
    #     organization_account_schedule_event = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', account_schedule_event.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_account_schedule_event.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)
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
    # def test_update_account_schedule_event_permission_granted(self):
    #     """ Allow updating account_schedule_events for users with permissions """
    #     query = self.account_schedule_event_update_mutation
    #     account_schedule_event = f.AccountSubscriptionFactory.create()
    #     organization_account_schedule_event = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', account_schedule_event.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_account_schedule_event.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)
    #
    #     user = account_schedule_event.account
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
    #     self.assertEqual(data['updateAccountSubscription']['accountSubscription']['dateStart'], variables['input']['dateStart'])
    #
    # def test_update_account_schedule_event_permission_denied(self):
    #     """ Check update account_schedule_event permission denied error message """
    #     query = self.account_schedule_event_update_mutation
    #     account_schedule_event = f.AccountSubscriptionFactory.create()
    #     organization_account_schedule_event = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', account_schedule_event.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_account_schedule_event.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)
    #
    #     user = account_schedule_event.account
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
    # def test_delete_account_schedule_event(self):
    #     """ Delete an account account_schedule_event """
    #     query = self.account_schedule_event_delete_mutation
    #     account_schedule_event = f.AccountSubscriptionFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', account_schedule_event.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     print(data)
    #     self.assertEqual(data['deleteAccountSubscription']['ok'], True)
    #
    # def test_delete_account_schedule_event_anon_user(self):
    #     """ Delete account_schedule_event denied for anon user """
    #     query = self.account_schedule_event_delete_mutation
    #     account_schedule_event = f.AccountSubscriptionFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', account_schedule_event.id)
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
    # def test_delete_account_schedule_event_permission_granted(self):
    #     """ Allow deleting account_schedule_events for users with permissions """
    #     query = self.account_schedule_event_delete_mutation
    #     account_schedule_event = f.AccountSubscriptionFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', account_schedule_event.id)
    #
    #     # Give permissions
    #     user = account_schedule_event.account
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
    #     self.assertEqual(data['deleteAccountSubscription']['ok'], True)
    #
    # def test_delete_account_schedule_event_permission_denied(self):
    #     """ Check delete account_schedule_event permission denied error message """
    #     query = self.account_schedule_event_delete_mutation
    #     account_schedule_event = f.AccountSubscriptionFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', account_schedule_event.id)
    #
    #     user = account_schedule_event.account
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
