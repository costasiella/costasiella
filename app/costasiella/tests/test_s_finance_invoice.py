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
from ..dudes import CountryDude
from .. import models
from .. import schema
from ..modules.gql_tools import get_rid


class GQLFinanceInvoice(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['app_settings.json', 'finance_invoice_group.json', 'finance_payment_methods.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.country_dude = CountryDude()

        self.permission_view = 'view_financeinvoice'
        self.permission_add = 'add_financeinvoice'
        self.permission_change = 'change_financeinvoice'
        self.permission_delete = 'delete_financeinvoice'

        # self.account = f.RegularUserFactory.create()

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

        self.variables_cancel = {
            "input": {}
        }

        self.invoices_query = '''
  query FinanceInvoices($after: String, $before: String, $status: CostasiellaFinanceInvoiceStatusChoices) {
    financeInvoices(first: 15, before: $before, after: $after, status: $status) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          account {
            id
            fullName
          }
          financePaymentMethod {
            id
            name
          }
          invoiceNumber
          status
          summary
          relationCompany
          relationCompanyRegistration
          relationCompanyTaxRegistration
          relationContactName
          relationAddress
          relationPostcode
          relationCity
          relationCountry
          dateSent
          dateDue
          total
          totalDisplay
          balance
          balanceDisplay
        }
      }
    }
  }
'''

        self.invoice_query = '''
  query FinanceInvoice($id: ID!) {
    financeInvoice(id:$id) {
      id
      account {
        id
        fullName
      }
      financePaymentMethod {
        id
        name
      }
      relationCompany
      relationCompanyRegistration
      relationCompanyTaxRegistration
      relationContactName
      relationAddress
      relationPostcode
      relationCity
      relationCountry
      status
      summary
      invoiceNumber
      dateSent
      dateDue
      terms
      footer
      note
      subtotalDisplay
      taxDisplay
      totalDisplay
      paidDisplay
      balanceDisplay
      updatedAt
    }
  }
'''

        self.invoice_create_mutation = ''' 
  mutation CreateFinanceInvoice($input: CreateFinanceInvoiceInput!) {
    createFinanceInvoice(input: $input) {
      financeInvoice {
        id
        account {
          id
          fullName
        }
        business {
          id
        }
        financeInvoiceGroup {
          id 
          name
        }
        financePaymentMethod {
          id
          name
        }
        relationCompany
        relationCompanyRegistration
        relationCompanyTaxRegistration
        relationContactName
        relationAddress
        relationPostcode
        relationCity
        relationCountry
        status
        summary
        invoiceNumber
        dateSent
        dateDue
        terms
        footer
        note
        subtotalDisplay
        taxDisplay
        totalDisplay
        paidDisplay
        balanceDisplay
        updatedAt
      }
    }
  }
'''

        self.invoice_update_mutation = '''
  mutation UpdateFinanceInvoice($input: UpdateFinanceInvoiceInput!) {
    updateFinanceInvoice(input: $input) {
      financeInvoice {
        id
        account {
          id
          fullName
        }
        business {
          id
        }
        financeInvoiceGroup {
          id 
          name
        }
        financePaymentMethod {
          id
          name
        }
        relationCompany
        relationCompanyRegistration
        relationCompanyTaxRegistration
        relationContactName
        relationAddress
        relationPostcode
        relationCity
        relationCountry
        status
        summary
        invoiceNumber
        dateSent
        dateDue
        terms
        footer
        note
        subtotalDisplay
        taxDisplay
        totalDisplay
        paidDisplay
        balanceDisplay
        updatedAt 
      }
    }
  }
'''

        self.invoice_cancel_and_create_credit_invoice_mutation = '''
  mutation CancelAndCreateCreditFinanceInvoice($input: CancelAndCreateCreditFinanceInvoiceInput!) {
    cancelAndCreateCreditFinanceInvoice(input: $input) {
      financeInvoice {
        id
        creditInvoiceFor
        account {
          id
          fullName
        }
        financePaymentMethod {
          id
          name
        }
        relationCompany
        relationCompanyRegistration
        relationCompanyTaxRegistration
        relationContactName
        relationAddress
        relationPostcode
        relationCity
        relationCountry
        status
        summary
        invoiceNumber
        dateSent
        dateDue
        terms
        footer
        note
        subtotalDisplay
        taxDisplay
        totalDisplay
        paidDisplay
        balanceDisplay
        updatedAt
        items {
          edges {
            node {
              id
              lineNumber
              productName
              description
              quantity
              price
              financeTaxRate {
                id
                name
                percentage
                rateType
              }
              subtotal
              subtotalDisplay
              tax
              taxDisplay
              total
              totalDisplay
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
    }
  }
'''

        self.invoice_delete_mutation = '''
  mutation DeleteFinanceInvoice($input: DeleteFinanceInvoiceInput!) {
    deleteFinanceInvoice(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account invoices """
        query = self.invoices_query
        invoice = f.FinanceInvoiceFactory.create()
        invoice.finance_payment_method = f.FinancePaymentMethodFactory()
        invoice.save()

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')

        self.assertEqual(
            data['financeInvoices']['edges'][0]['node']['account']['id'], 
            to_global_id("AccountNode", invoice.account.id)
        )
        self.assertEqual(
            data['financeInvoices']['edges'][0]['node']['financePaymentMethod']['id'], 
            to_global_id("FinancePaymentMethodNode", invoice.finance_payment_method.id)
        )
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['invoiceNumber'], invoice.invoice_number)
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['dateSent'], str(timezone.now().date()))
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['dateDue'], 
          str(timezone.now().date() + datetime.timedelta(days=invoice.finance_invoice_group.due_after_days))
        )
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['summary'], invoice.summary)
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['relationCompany'], invoice.relation_company)
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['relationCompanyRegistration'], invoice.relation_company_registration)
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['relationCompanyTaxRegistration'], invoice.relation_company_tax_registration)
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['relationContactName'], invoice.relation_contact_name)
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['relationAddress'], invoice.relation_address)
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['relationPostcode'], invoice.relation_postcode)
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['relationCity'], invoice.relation_city)
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['relationCountry'], invoice.relation_country)
        self.assertEqual(data['financeInvoices']['edges'][0]['node']['status'], invoice.status)

    def test_query_status_filter(self):
        """ Query list of account invoices - filtered by status """
        query = self.invoices_query
        invoice = f.FinanceInvoiceFactory.create()
        invoice.status = "SENT"
        invoice.finance_payment_method = f.FinancePaymentMethodFactory()
        invoice.save()

        variables = {
            "status": "SENT"
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        # Make sure the invoice is in the list returned
        self.assertEqual(
            data['financeInvoices']['edges'][0]['node']['id'], 
            to_global_id("FinanceInvoiceNode", invoice.id)
        )

    def test_query_permission_denied(self):
        """ Query list of account invoices - check permission denied
        A user can query the invoices linked to their account, so an error will never be thrown
        But a user shouldn't be able to view orders from other accounts without additional permission
        """
        query = self.invoices_query
        invoice = f.FinanceInvoiceFactory.create()
        other_user = f.InstructorFactory.create()

        # Create regular user
        user = get_user_model().objects.get(pk=invoice.account.id)
        executed = execute_test_client_api_query(query, other_user)
        data = executed.get('data')

        for item in data['financeInvoices']['edges']:
            node = item['node']
            self.assertNotEqual(node['account']['id'], to_global_id("AccountNode", user.id))

    def test_query_permission_granted(self):
        """ Query list of account invoices with view permission """
        query = self.invoices_query
        invoice = f.FinanceInvoiceFactory.create()

        # Create regular user
        user = get_user_model().objects.get(pk=invoice.account.id)
        permission = Permission.objects.get(codename='view_financeinvoice')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user)
        data = executed.get('data')

        # List all invoices
        self.assertEqual(
            data['financeInvoices']['edges'][0]['node']['account']['id'], 
            to_global_id("AccountNode", invoice.account.id)
        )

    def test_query_anon_user(self):
        """ Query list of account invoices - anon user """
        query = self.invoices_query
        invoice = f.FinanceInvoiceFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account invoice as admin """   
        invoice = f.FinanceInvoiceFactory.create()

        variables = {
            "id": to_global_id("FinanceInvoiceNode", invoice.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.invoice_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['financeInvoice']['account']['id'], 
            to_global_id("AccountNode", invoice.account.id)
        )
        self.assertEqual(data['financeInvoice']['invoiceNumber'], invoice.invoice_number)
        self.assertEqual(data['financeInvoice']['dateSent'], str(timezone.now().date()))
        self.assertEqual(data['financeInvoice']['dateDue'], 
          str(timezone.now().date() + datetime.timedelta(days=invoice.finance_invoice_group.due_after_days))
        )
        self.assertEqual(data['financeInvoice']['summary'], invoice.summary)
        self.assertEqual(data['financeInvoice']['relationCompany'], invoice.relation_company)
        self.assertEqual(data['financeInvoice']['relationCompanyRegistration'], invoice.relation_company_registration)
        self.assertEqual(data['financeInvoice']['relationCompanyTaxRegistration'], invoice.relation_company_tax_registration)
        self.assertEqual(data['financeInvoice']['relationContactName'], invoice.relation_contact_name)
        self.assertEqual(data['financeInvoice']['relationAddress'], invoice.relation_address)
        self.assertEqual(data['financeInvoice']['relationPostcode'], invoice.relation_postcode)
        self.assertEqual(data['financeInvoice']['relationCity'], invoice.relation_city)
        self.assertEqual(data['financeInvoice']['relationCountry'], invoice.relation_country)
        self.assertEqual(data['financeInvoice']['status'], invoice.status)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account invoice """   
        invoice = f.FinanceInvoiceFactory.create()

        variables = {
            "id": to_global_id("FinanceInvoiceNode", invoice.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.invoice_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        invoice = f.FinanceInvoiceFactory.create()
        user = f.Instructor2Factory.create()

        variables = {
            "id": to_global_id("FinanceInvoiceNode", invoice.id),
        }

        # Now query single invoice and check
        executed = execute_test_client_api_query(self.invoice_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        invoice = f.FinanceInvoiceFactory.create()
        user = invoice.account
        permission = Permission.objects.get(codename='view_financeinvoice')
        user.user_permissions.add(permission)
        user.save()
        

        variables = {
            "id": to_global_id("FinanceInvoiceNode", invoice.id),
        }

        # Now query single invoice and check   
        executed = execute_test_client_api_query(self.invoice_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['financeInvoice']['account']['id'], 
            to_global_id('AccountNode', invoice.account.id)
        )

    def test_create_invoice_for_account(self):
        """ Create an account invoice """
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
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationCompany'], "")
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationCompanyRegistration'], "")
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationCompanyTaxRegistration'], "")
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationContactName'], account.full_name)
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationAddress'],
                         account.address)
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationPostcode'],
                         account.postcode)
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationCity'],
                         account.city)
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationCountry'],
                         account.country)

    def test_create_invoice_empty_invoice_item_added(self):
        """ Create an account invoice - check that an empty item is added on creation"""
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
        finance_invoice = models.FinanceInvoice.objects.get(pk=rid.id)

        nr_of_invoice_items = models.FinanceInvoiceItem.objects.filter(finance_invoice=finance_invoice).count()

        self.assertEqual(nr_of_invoice_items, 1)

    def test_create_invoice_for_business(self):
        """ Create an invoice for a b2b relation"""
        query = self.invoice_create_mutation

        account = f.RegularUserFactory.create()
        business = f.BusinessB2BFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['business'] = to_global_id('BusinessNode', business.id)

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
            data['createFinanceInvoice']['financeInvoice']['business']['id'],
            variables['input']['business']
        )
        self.assertEqual(
            data['createFinanceInvoice']['financeInvoice']['financeInvoiceGroup']['id'],
            variables['input']['financeInvoiceGroup']
        )
        self.assertEqual(
            data['createFinanceInvoice']['financeInvoice']['relationCompany'],
            business.name
        )
        self.assertEqual(
            data['createFinanceInvoice']['financeInvoice']['relationCompanyRegistration'],
            business.registration
        )
        self.assertEqual(
            data['createFinanceInvoice']['financeInvoice']['relationCompanyTaxRegistration'],
            business.tax_registration
        )
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationContactName'],
                         "")
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationAddress'],
                         business.address)
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationPostcode'],
                         business.postcode)
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationCity'],
                         business.city)
        self.assertEqual(data['createFinanceInvoice']['financeInvoice']['relationCountry'],
                         self.country_dude.iso_country_code_to_name(business.country))


    def test_create_invoice_group_id_plus_one(self):
        """ Create an account invoice and check whether the FinanceInoiceGroup next id field increated by 1 """
        query = self.invoice_create_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)

        finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)
        next_id_before = finance_invoice_group.next_id

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

        finance_invoice_group = models.FinanceInvoiceGroup.objects.get(pk=100)
        next_id_after = finance_invoice_group.next_id

        self.assertEqual((next_id_before + 1), next_id_after)

    def test_create_account_subscription_invoice(self):
        """ Create an account invoice with a subscription item"""
        query = self.invoice_create_mutation

        account_subscription = f.AccountSubscriptionFactory.create()
        account = account_subscription.account
        organization_subscription_price = f.OrganizationSubscriptionPriceFactory(
            organization_subscription=account_subscription.organization_subscription
        )
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['accountSubscription'] = to_global_id('AccountSubscriptionNode', account_subscription.id)
        variables['input']['financeInvoiceGroup'] = to_global_id('FinanceInvoiceGroupNode', 100)
        variables['input']['subscriptionYear'] = 2019
        variables['input']['subscriptionMonth'] = 1

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        # Get invoice
        rid = get_rid(data['createFinanceInvoice']['financeInvoice']['id'])
        invoice = models.FinanceInvoice.objects.get(pk=rid.id)

        # Check schema response
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

        # Check that the item is added to the database as well.
        items = invoice.items
        first_item = items.first()
        self.assertEqual(first_item.account_subscription, account_subscription)

    def test_create_invoice_anon_user(self):
        """ Don't allow creating account invoices for non-logged in users """
        query = self.invoice_create_mutation
        
        account = f.RegularUserFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_invoice_permission_granted(self):
        """ Allow creating invoices for users with permissions """
        query = self.invoice_create_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)

        # Create regular user
        user = account
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
            data['createFinanceInvoice']['financeInvoice']['summary'],
            variables['input']['summary']
        )

    def test_create_invoice_permission_denied(self):
        """ Check create invoice permission denied error message """
        query = self.invoice_create_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)

        # Create regular user
        user = account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_invoice_address_from_account(self):
        """ Update a invoice """
        query = self.invoice_update_mutation

        invoice = f.FinanceInvoiceFactory.create()
        account = invoice.account
        business = f.BusinessB2BFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
        variables['input']['business'] = None  # Set business to None to have the address set to relation fields

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')

        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCompany'], "")
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCompanyRegistration'], "")
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCompanyTaxRegistration'], "")
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationContactName'], account.full_name)
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationAddress'],
                         account.address)
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationPostcode'],
                         account.postcode)
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCity'],
                         account.city)
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCountry'],
                         account.country)
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['invoiceNumber'],
                         variables['input']['invoiceNumber'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateSent'], variables['input']['dateSent'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateDue'], variables['input']['dateDue'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['status'], variables['input']['status'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['summary'], variables['input']['summary'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['terms'], variables['input']['terms'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['footer'], variables['input']['footer'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['note'], variables['input']['note'])

    def test_update_invoice_address_from_business(self):
        """ Update a invoice """
        query = self.invoice_update_mutation

        invoice = f.FinanceInvoiceFactory.create()
        business = f.BusinessB2BFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
        variables['input']['business'] = to_global_id("BusinessNode", business.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')

        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCompany'],
                         business.name)
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCompanyRegistration'],
                         business.registration)
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCompanyTaxRegistration'],
                         business.tax_registration)
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationContactName'],
                         "")
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationAddress'],
                         business.address)
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationPostcode'],
                         business.postcode)
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCity'],
                         business.city)
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCountry'],
                         self.country_dude.iso_country_code_to_name(business.country))
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['invoiceNumber'],
                         variables['input']['invoiceNumber'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateSent'], variables['input']['dateSent'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateDue'], variables['input']['dateDue'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['status'], variables['input']['status'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['summary'], variables['input']['summary'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['terms'], variables['input']['terms'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['footer'], variables['input']['footer'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['note'], variables['input']['note'])

    def test_update_invoice_custom_to(self):
        """ Update a invoice """
        query = self.invoice_update_mutation

        invoice = f.FinanceInvoiceFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
        variables['input']['customTo'] = True

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')

        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCompany'], variables['input']['relationCompany'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCompanyRegistration'], variables['input']['relationCompanyRegistration'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationContactName'], variables['input']['relationContactName'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationAddress'], variables['input']['relationAddress'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationPostcode'], variables['input']['relationPostcode'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCity'], variables['input']['relationCity'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['relationCountry'], variables['input']['relationCountry'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['invoiceNumber'], variables['input']['invoiceNumber'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateSent'], variables['input']['dateSent'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateDue'], variables['input']['dateDue'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['status'], variables['input']['status'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['summary'], variables['input']['summary'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['terms'], variables['input']['terms'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['footer'], variables['input']['footer'])
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['note'], variables['input']['note'])

    def test_update_invoice_anon_user(self):
        """ Don't allow updating invoices for non-logged in users """
        query = self.invoice_update_mutation
        invoice = f.FinanceInvoiceFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_invoice_permission_granted(self):
        """ Allow updating invoices for users with permissions """
        query = self.invoice_update_mutation
        invoice = f.FinanceInvoiceFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

        user = invoice.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateSent'], variables['input']['dateSent'])

    def test_update_invoice_permission_denied(self):
        """ Check update invoice permission denied error message """
        query = self.invoice_update_mutation
        invoice = f.FinanceInvoiceFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

        user = invoice.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_cancel_and_create_credit_invoice(self):
        """ Cancel invoice and create credit invoice """
        query = self.invoice_cancel_and_create_credit_invoice_mutation

        invoice_item = f.FinanceInvoiceItemFactory.create()
        invoice = invoice_item.finance_invoice
        variables = self.variables_cancel
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['cancelAndCreateCreditFinanceInvoice']['financeInvoice']['account']['id'],
                         to_global_id('AccountNode', invoice.account.id))
        self.assertEqual(data['cancelAndCreateCreditFinanceInvoice']['financeInvoice']['creditInvoiceFor'],
                         invoice.id)
        self.assertEqual(data['cancelAndCreateCreditFinanceInvoice']['financeInvoice']['summary'],
                         invoice.summary)
        self.assertEqual(data['cancelAndCreateCreditFinanceInvoice']['financeInvoice']['note'],
                         invoice.note)
        self.assertEqual(data['cancelAndCreateCreditFinanceInvoice']['financeInvoice']['note'],
                         invoice.note)
        self.assertNotEqual(data['cancelAndCreateCreditFinanceInvoice']['financeInvoice']['invoiceNumber'],
                            invoice.invoice_number)

        # Check item
        credit_item = data['cancelAndCreateCreditFinanceInvoice']['financeInvoice']['items']['edges'][0]['node']
        self.assertEqual(credit_item['productName'],
                         invoice_item.product_name)
        self.assertEqual(credit_item['description'],
                         invoice_item.description)
        self.assertEqual(credit_item['lineNumber'],
                         invoice_item.line_number)
        self.assertEqual(credit_item['price'],
                         format(invoice_item.price * -1, ".2f"))
        self.assertEqual(credit_item['subtotal'],
                         format(invoice_item.subtotal * -1, ".2f"))
        self.assertEqual(credit_item['total'],
                         format(invoice_item.total * -1, ".2f"))
        self.assertEqual(credit_item['quantity'],
                         format(invoice_item.quantity, ".2f"))
        self.assertEqual(credit_item['price'],
                         format(invoice_item.price * -1, ".2f"))
        self.assertEqual(credit_item['financeTaxRate']['id'],
                         to_global_id('FinanceTaxRateNode', invoice_item.finance_tax_rate.id))
        self.assertEqual(credit_item['financeCostcenter']['id'],
                         to_global_id('FinanceCostCenterNode', invoice_item.finance_costcenter.id))
        self.assertEqual(credit_item['financeGlaccount']['id'],
                         to_global_id('FinanceGLAccountNode', invoice_item.finance_glaccount.id))

    def test_cancel_and_create_credit_invoice_anon_user(self):
        """ Don't allow crediting credit invoices for non-logged in users """
        query = self.invoice_cancel_and_create_credit_invoice_mutation

        invoice_item = f.FinanceInvoiceItemFactory.create()
        invoice = invoice_item.finance_invoice
        variables = self.variables_cancel
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_cancel_and_create_credit_invoice_permission_granted(self):
        """ Allow updating invoices for users with permissions """
        query = self.invoice_cancel_and_create_credit_invoice_mutation

        invoice_item = f.FinanceInvoiceItemFactory.create()
        invoice = invoice_item.finance_invoice
        variables = self.variables_cancel
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

        user = invoice.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['cancelAndCreateCreditFinanceInvoice']['financeInvoice']['account']['id'],
                         to_global_id('AccountNode', invoice.account.id))

    def test_cancel_and_create_credit_invoice_permission_denied(self):
        """ Check update invoice permission denied error message """
        query = self.invoice_cancel_and_create_credit_invoice_mutation

        invoice_item = f.FinanceInvoiceItemFactory.create()
        invoice = invoice_item.finance_invoice
        variables = self.variables_cancel
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

        user = invoice.account
        permission = Permission.objects.get(codename=self.permission_change)

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_invoice(self):
        """ Delete an account invoice """
        query = self.invoice_delete_mutation
        invoice = f.FinanceInvoiceFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceInvoice']['ok'], True)

    def test_delete_invoice_anon_user(self):
        """ Delete invoice denied for anon user """
        query = self.invoice_delete_mutation
        invoice = f.FinanceInvoiceFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_invoice_permission_granted(self):
        """ Allow deleting invoices for users with permissions """
        query = self.invoice_delete_mutation
        invoice = f.FinanceInvoiceFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

        # Give permissions
        user = invoice.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceInvoice']['ok'], True)

    def test_delete_invoice_permission_denied(self):
        """ Check delete invoice permission denied error message """
        query = self.invoice_delete_mutation
        invoice = f.FinanceInvoiceFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
        
        user = invoice.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

