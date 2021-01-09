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


class GQLScheduleEvent(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['app_settings.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleevent'
        self.permission_add = 'add_scheduleevent'
        self.permission_change = 'change_scheduleevent'
        self.permission_delete = 'delete_scheduleevent'

        # self.account = f.RegularUserFactory.create()

        self.variables_query = {
            "archived": False
        }

        self.variables_create = {
            "input": {
                # Account will be added in the test create functions
                "financeInvoiceGroup": to_global_id('FinanceInvoiceGroupNode', 100),
                "summary": "create summary"
            }
        }

        self.variables_update = {
            "input": {
              "summary": "create summary",
              "relationCompany": "ACME INC.",
              "relationCompanyRegistration": "ACME 4312",
              "relationCompanyTaxRegistration": "ACME TAX 99",
              "relationContactName": "Contact person",
              "relationAddress": "Street 1",
              "relationPostcode": "1233434 545",
              "relationCity": "Amsterdam",
              "relationCountry": "NL",
              "invoiceNumber": "INVT0001",
              "dateSent": "2019-01-03",
              "dateDue": "2019-02-28",
              "status": "SENT",
              "terms": "Terms go there",
              "footer": "Footer here",
              "note": "Notes here"
            }
        }

        self.events_query = '''
  query ScheduleEvents($before:String, $after:String, $archived:Boolean!) {
    scheduleEvents(first: 100, before: $before, after:$after, archived:$archived) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          archived
          displayPublic
          displayShop
          autoSendInfoMail
          organizationLocation {
            id
            name
          }
          name
          tagline
          preview
          description
          organizationLevel {
            id
            name
          }
          teacher {
            id 
            fullName
          }
          teacher2 {
            id
            fullName
          }
          dateStart
          dateEnd
          timeStart
          timeEnd
          infoMailContent
          scheduleItems {
            edges {
              node {
                id
              }
            }
          }
          createdAt
          updatedAt
        }
      }
    }
  }
'''

        self.event_query = '''
  query ScheduleEvent($id: ID!) {
    scheduleEvent(id: $id) {
      id
      archived
      displayPublic
      displayShop
      autoSendInfoMail
      organizationLocation {
        id
        name
      }
      name
      tagline
      preview
      description
      organizationLevel {
        id
        name
      }
      teacher {
        id 
        fullName
      }
      teacher2 {
        id
        fullName
      }
      dateStart
      dateEnd
      timeStart
      timeEnd
      infoMailContent
      scheduleItems {
        edges {
          node {
            id
          }
        }
      }
      createdAt
      updatedAt
    }
  }
'''

        self.event_create_mutation = ''' 
  mutation CreateScheduleEvent($input:CreateScheduleEventInput!) {
    createScheduleEvent(input: $input) {
      scheduleEvent{
        id
        displayPublic
        displayShop
        autoSendInfoMail
        organizationLocation {
          id
        }
        organizationLevel {
          id
        }
        name
        tagline
        preview
        description
        infoMailContent
        teacher {
          id
        }
        teacher2 {
          id 
        }
      }
    }
  }
'''

        self.event_update_mutation = '''
  mutation UpdateScheduleEvent($input:CreateScheduleEventInput!) {
    updateScheduleEvent(input: $input) {
      scheduleEvent{
        id
        displayPublic
        displayShop
        autoSendInfoMail
        organizationLocation {
          id
        }
        organizationLevel {
          id
        }
        name
        tagline
        preview
        description
        infoMailContent
        teacher {
          id
        }
        teacher2 {
          id 
        }
      }
    }
  }
'''

        self.event_archive_mutation = '''
  mutation ArchiveScheduleEvent($input: ArchiveScheduleEventInput!) {
    archiveScheduleEvent(input: $input) {
      scheduleEvent {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of schedule events """
        query = self.events_query
        schedule_event = f.ScheduleEventFactory.create()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['organizationLocation']['id'],
                         to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['name'], schedule_event.name)
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['tagline'], schedule_event.tagline)
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['preview'], schedule_event.preview)
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['description'], schedule_event.description)
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['infoMailContent'],
                         schedule_event.info_mail_content)
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['organizationLevel']['id'],
                         to_global_id("OrganizationLevelNode", schedule_event.organization_level.id))
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['teacher']['id'],
                         to_global_id("AccountNode", schedule_event.teacher.id))
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['teacher2']['id'],
                         to_global_id("AccountNode", schedule_event.teacher_2.id))

    def test_query_permission_denied_dont_show_nonpublic_events(self):
        """ Query list of events - check permission denied
        A user can query the invoices linked to their account, so an error will never be thrown
        But a user shouldn't be able to view orders from other accounts without additional permission
        """
        query = self.events_query
        schedule_event = f.ScheduleEventFactory.create()
        schedule_event.display_public = False
        schedule_event.save()

        # Create regular user
        user = f.RegularUserFactory()
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        # No items should be listed
        self.assertEqual(len(data['scheduleEvents']['edges']), 0)

    def test_query_permission_granted_show_nonpublic_events(self):
        """ Query list of schedule events with view permission """
        query = self.events_query
        schedule_event = f.ScheduleEventFactory.create()
        schedule_event.display_public = False
        schedule_event.save()

        # Create regular user
        user = f.RegularUserFactory()
        permission = Permission.objects.get(codename='view_scheduleevent')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        # List all events
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['organizationLocation']['id'],
                         to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))

    def test_query_anon_user(self):
        """ Query list of schedule events - anon user """
        query = self.events_query
        schedule_event = f.ScheduleEventFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        print(executed)
        data = executed.get('data')

        # List all events
        self.assertEqual(data['scheduleEvents']['edges'][0]['node']['organizationLocation']['id'],
                         to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))

    def test_query_one(self):
        """ Query one schedule event as admin """
        schedule_event = f.ScheduleEventFactory.create()

        variables = {
            "id": to_global_id("ScheduleEventNode", schedule_event.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.event_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['scheduleEvent']['organizationLocation']['id'],
                         to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))
        self.assertEqual(data['scheduleEvent']['name'], schedule_event.name)
        self.assertEqual(data['scheduleEvent']['tagline'], schedule_event.tagline)
        self.assertEqual(data['scheduleEvent']['preview'], schedule_event.preview)
        self.assertEqual(data['scheduleEvent']['description'], schedule_event.description)
        self.assertEqual(data['scheduleEvent']['infoMailContent'],
                         schedule_event.info_mail_content)
        self.assertEqual(data['scheduleEvent']['organizationLevel']['id'],
                         to_global_id("OrganizationLevelNode", schedule_event.organization_level.id))
        self.assertEqual(data['scheduleEvent']['teacher']['id'],
                         to_global_id("AccountNode", schedule_event.teacher.id))
        self.assertEqual(data['scheduleEvent']['teacher2']['id'],
                         to_global_id("AccountNode", schedule_event.teacher_2.id))

    def test_query_one_anon_user_nonpublic_not_allowed(self):
        """ Deny permission for anon users Query one schedule event """
        schedule_event = f.ScheduleEventFactory.create()
        schedule_event.display_public = False
        schedule_event.display_shop = False
        schedule_event.save()

        variables = {
            "id": to_global_id("ScheduleEventNode", schedule_event.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.event_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_anon_user_public_allowed(self):
        """ Deny permission for anon users Query one schedule event """
        schedule_event = f.ScheduleEventFactory.create()

        variables = {
            "id": to_global_id("ScheduleEventNode", schedule_event.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.event_query, self.anon_user, variables=variables)
        data = executed['data']
        self.assertEqual(data['scheduleEvent']['organizationLocation']['id'],
                         to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))

    def test_query_one_display_nonpublic_permission_denied(self):
        """ Don't list non-public events when user lacks authorization """
        schedule_event = f.ScheduleEventFactory.create()
        schedule_event.display_public = False
        schedule_event.display_shop = False
        schedule_event.save()
        # Create regular user
        user = f.RegularUserFactory()

        variables = {
            "id": to_global_id("ScheduleEventNode", schedule_event.id),
        }

        # Now query single event and check
        executed = execute_test_client_api_query(self.event_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_display_nonpublic_permission_granted(self):
        """ Respond with data when user has permission """
        schedule_event = f.ScheduleEventFactory.create()
        schedule_event.display_public = False
        schedule_event.display_shop = False
        schedule_event.save()
        # Create regular user
        user = f.RegularUserFactory()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        variables = {
            "id": to_global_id("ScheduleEventNode", schedule_event.id),
        }

        # Now query single schedule event and check
        executed = execute_test_client_api_query(self.event_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['scheduleEvent']['organizationLocation']['id'],
                         to_global_id("OrganizationLocationNode", schedule_event.organization_location.id))

    def test_create_schedule_event(self):
        """ Create a schedule event """
        query = self.invoice_create_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        # Get invoice
        rid = get_rid(data['createFinanceInvoice']['financeInvoice']['id'])
        invoice = models.FinanceInvoice.objects.get(pk=rid.id)

        self.assertEqual(
            data['createFinanceInvoice']['financeInvoice']['account']['id'],
            variables['input']['account']
        )
        self.assertEqual(
            data['createFinanceInvoice']['financeInvoice']['financeInvoiceGroup']['id'],
            variables['input']['financeInvoiceGroup']
        )
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['dateSent'], str(timezone.now().date()))
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['dateDue'],
            str(timezone.now().date() + datetime.timedelta(days=invoice.finance_invoice_group.due_after_days))
        )
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['summary'], variables['input']['summary'])
    #
    # def test_create_invoice_group_id_plus_one(self):
    #     """ Create an account invoice and check whether the FinanceInoiceGroup next id field increated by 1 """
    #     query = self.invoice_create_mutation
    #
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #
    #     finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)
    #     next_id_before = finance_invoice_group.next_id
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #
    #     # Get invoice
    #     rid = get_rid(data['createFinanceInvoice']['financeInvoice']['id'])
    #     invoice = models.FinanceInvoice.objects.get(pk=rid.id)
    #
    #     self.assertEqual(
    #         data['createFinanceInvoice']['financeInvoice']['account']['id'],
    #         variables['input']['account']
    #     )
    #
    #     finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)
    #     next_id_after = finance_invoice_group.next_id
    #
    #     self.assertEqual((next_id_before + 1), next_id_after)
    #
    # def test_create_account_subscription_invoice(self):
    #     """ Create an account invoice with a subscription item"""
    #     query = self.invoice_create_mutation
    #
    #     account_subscription = f.AccountSubscriptionFactory.create()
    #     account = account_subscription.account
    #     organization_subscription_price = f.OrganizationSubscriptionPriceFactory(
    #         initial_organization_subscription=account_subscription.organization_subscription
    #     )
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['accountSubscription'] = to_global_id('AccountSubscriptionNode', account_subscription.id)
    #     variables['input']['financeInvoiceGroup'] = to_global_id('FinanceInvoiceGroupNode', 100)
    #     variables['input']['subscriptionYear'] = 2019
    #     variables['input']['subscriptionMonth'] = 1
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #
    #     # Get invoice
    #     rid = get_rid(data['createFinanceInvoice']['financeInvoice']['id'])
    #     invoice = models.FinanceInvoice.objects.get(pk=rid.id)
    #
    #     # Check schema response
    #     self.assertEqual(
    #         data['createFinanceInvoice']['financeInvoice']['account']['id'],
    #         variables['input']['account']
    #     )
    #     self.assertEqual(
    #         data['createFinanceInvoice']['financeInvoice']['financeInvoiceGroup']['id'],
    #         variables['input']['financeInvoiceGroup']
    #     )
    #     self.assertEqual(data['createFinanceInvoice']['financeInvoice']['dateSent'], str(timezone.now().date()))
    #     self.assertEqual(data['createFinanceInvoice']['financeInvoice']['dateDue'],
    #         str(timezone.now().date() + datetime.timedelta(days=invoice.finance_invoice_group.due_after_days))
    #     )
    #     self.assertEqual(data['createFinanceInvoice']['financeInvoice']['summary'], variables['input']['summary'])
    #
    #     # Check that the item is added to the database as well.
    #     items = invoice.items
    #     first_item = items.first()
    #     self.assertEqual(first_item.account_subscription, account_subscription)
    #
    # def test_create_invoice_anon_user(self):
    #     """ Don't allow creating account invoices for non-logged in users """
    #     query = self.invoice_create_mutation
    #
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
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
    # def test_create_location_permission_granted(self):
    #     """ Allow creating invoices for users with permissions """
    #     query = self.invoice_create_mutation
    #
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #
    #     # Create regular user
    #     user = account
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['createFinanceInvoice']['financeInvoice']['account']['id'],
    #         variables['input']['account']
    #     )
    #
    # def test_create_invoice_permission_denied(self):
    #     """ Check create invoice permission denied error message """
    #     query = self.invoice_create_mutation
    #
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #
    #     # Create regular user
    #     user = account
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
    # def test_update_invoice(self):
    #     """ Update a invoice """
    #     query = self.invoice_update_mutation
    #
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCompany'], variables['input']['relationCompany'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCompanyRegistration'], variables['input']['relationCompanyRegistration'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationContactName'], variables['input']['relationContactName'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationAddress'], variables['input']['relationAddress'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationPostcode'], variables['input']['relationPostcode'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCity'], variables['input']['relationCity'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCountry'], variables['input']['relationCountry'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['invoiceNumber'], variables['input']['invoiceNumber'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateSent'], variables['input']['dateSent'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateDue'], variables['input']['dateDue'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['status'], variables['input']['status'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['summary'], variables['input']['summary'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['terms'], variables['input']['terms'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['footer'], variables['input']['footer'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['note'], variables['input']['note'])
    #
    # def test_update_invoice_anon_user(self):
    #     """ Don't allow updating invoices for non-logged in users """
    #     query = self.invoice_update_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
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
    # def test_update_invoice_permission_granted(self):
    #     """ Allow updating invoices for users with permissions """
    #     query = self.invoice_update_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
    #
    #     user = invoice.account
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
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateSent'], variables['input']['dateSent'])
    #
    # def test_update_invoice_permission_denied(self):
    #     """ Check update invoice permission denied error message """
    #     query = self.invoice_update_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
    #
    #     user = invoice.account
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
    # def test_delete_invoice(self):
    #     """ Delete an account invoice """
    #     query = self.invoice_delete_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['deleteFinanceInvoice']['ok'], True)
    #
    # def test_delete_invoice_anon_user(self):
    #     """ Delete invoice denied for anon user """
    #     query = self.invoice_delete_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
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
    # def test_delete_invoice_permission_granted(self):
    #     """ Allow deleting invoices for users with permissions """
    #     query = self.invoice_delete_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
    #
    #     # Give permissions
    #     user = invoice.account
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
    #     self.assertEqual(data['deleteFinanceInvoice']['ok'], True)
    #
    # def test_delete_invoice_permission_denied(self):
    #     """ Check delete invoice permission denied error message """
    #     query = self.invoice_delete_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
    #
    #     user = invoice.account
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
