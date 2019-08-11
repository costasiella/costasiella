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



class GQLFinanceInvoice(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['finance_invoice_group.json', 'finance_payment_methods.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financeinvoice'
        self.permission_add = 'add_financeinvoice'
        self.permission_change = 'change_financeinvoice'
        self.permission_delete = 'delete_financeinvoice'

        # self.account = f.RegularUserFactory.create()

        self.variables_create = {
            "input": {
                # "account": to_global_id('AccountNode', self.account.id),
                "financeInvoiceGroup": to_global_id('FinanceInvoiceGroup', 100),
                "summary": "create summary",
                "note": "test"
            }
        }

        self.variables_update = {
            "input": {
                "dateStart": "2017-01-01",
                "dateEnd": "2020-12-31",
                "note": "Update note",
                "registrationFeePaid": True
            }
        }

        self.invoices_query = '''
  query FinanceInvoices($after: String, $before: String, $status: String) {
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
  query FinanceInvoice($id: ID!, $accountId: ID!, $after: String, $before: String, $archived: Boolean!) {
    financeInvoice(id:$id) {
      id
      account {
          id
      }
      organizationSubscription {
        id
        name
      }
      financePaymentMethod {
        id
        name
      }
      dateStart
      dateEnd
      note
      registrationFeePaid
      createdAt
    }
    organizationSubscriptions(first: 100, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          name
        }
      }
    }
    financePaymentMethods(first: 100, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          name
          code
        }
      }
    }
    account(id:$accountId) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
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
          firstName
          lastName
          email
        }
        organizationSubscription {
          id
          name
        }
        financePaymentMethod {
          id
          name
        }
        dateStart
        dateEnd
        note
        registrationFeePaid        
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
          firstName
          lastName
          email
        }
        organizationSubscription {
          id
          name
        }
        financePaymentMethod {
          id
          name
        }
        dateStart
        dateEnd
        note
        registrationFeePaid        
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



    def test_query_permision_denied(self):
        """ Query list of account invoices - check permission denied """
        query = self.invoices_query
        invoice = f.FinanceInvoiceFactory.create()

        # Create regular user
        user = get_user_model().objects.get(pk=invoice.account.id)
        executed = execute_test_client_api_query(query, user)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permision_granted(self):
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


    # def test_query_one(self):
    #     """ Query one account invoice as admin """   
    #     invoice = f.FinanceInvoiceFactory.create()
        
    #     variables = {
    #         "id": to_global_id("FinanceInvoiceNode", invoice.id),
    #         "accountId": to_global_id("AccountNode", invoice.account.id),
    #         "archived": False,
    #     }

    #     # Now query single invoice and check
    #     executed = execute_test_client_api_query(self.invoice_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['financeInvoice']['account']['id'], 
    #         to_global_id('AccountNode', invoice.account.id)
    #     )
    #     self.assertEqual(
    #         data['financeInvoice']['organizationSubscription']['id'], 
    #         to_global_id('OrganizationSubscriptionNode', invoice.organization_invoice.id)
    #     )
    #     self.assertEqual(
    #         data['financeInvoice']['financePaymentMethod']['id'], 
    #         to_global_id('FinancePaymentMethodNode', invoice.finance_payment_method.id)
    #     )
    #     self.assertEqual(data['financeInvoice']['dateStart'], str(invoice.date_start))
    #     self.assertEqual(data['financeInvoice']['dateEnd'], invoice.date_end)
    #     self.assertEqual(data['financeInvoice']['note'], invoice.note)
    #     self.assertEqual(data['financeInvoice']['registrationFeePaid'], invoice.registration_fee_paid)


    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one account invoice """   
    #     invoice = f.FinanceInvoiceFactory.create()

    #     variables = {
    #         "id": to_global_id("FinanceInvoiceNode", invoice.id),
    #         "accountId": to_global_id("AccountNode", invoice.account.id),
    #         "archived": False,
    #     }

    #     # Now query single invoice and check
    #     executed = execute_test_client_api_query(self.invoice_query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     invoice = f.FinanceInvoiceFactory.create()
    #     user = invoice.account

    #     variables = {
    #         "id": to_global_id("FinanceInvoiceNode", invoice.id),
    #         "accountId": to_global_id("AccountNode", invoice.account.id),
    #         "archived": False,
    #     }

    #     # Now query single invoice and check
    #     executed = execute_test_client_api_query(self.invoice_query, user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     invoice = f.FinanceInvoiceFactory.create()
    #     user = invoice.account
    #     permission = Permission.objects.get(codename='view_financeinvoice')
    #     user.user_permissions.add(permission)
    #     user.save()
        

    #     variables = {
    #         "id": to_global_id("FinanceInvoiceNode", invoice.id),
    #         "accountId": to_global_id("AccountNode", invoice.account.id),
    #         "archived": False,
    #     }

    #     # Now query single invoice and check   
    #     executed = execute_test_client_api_query(self.invoice_query, user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['financeInvoice']['organizationSubscription']['id'], 
    #         to_global_id('OrganizationSubscriptionNode', invoice.organization_invoice.id)
    #     )


    # def test_create_invoice(self):
    #     """ Create an account invoice """
    #     query = self.invoice_create_mutation

    #     account = f.RegularUserFactory.create()
    #     organization_invoice = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_invoice.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')

    #     self.assertEqual(
    #         data['createFinanceInvoice']['financeInvoice']['account']['id'], 
    #         variables['input']['account']
    #     )
    #     self.assertEqual(
    #         data['createFinanceInvoice']['financeInvoice']['organizationSubscription']['id'], 
    #         variables['input']['organizationSubscription']
    #     )
    #     self.assertEqual(
    #         data['createFinanceInvoice']['financeInvoice']['financePaymentMethod']['id'], 
    #         variables['input']['financePaymentMethod']
    #     )
    #     self.assertEqual(data['createFinanceInvoice']['financeInvoice']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['createFinanceInvoice']['financeInvoice']['dateEnd'], variables['input']['dateEnd'])
    #     self.assertEqual(data['createFinanceInvoice']['financeInvoice']['note'], variables['input']['note'])
    #     self.assertEqual(data['createFinanceInvoice']['financeInvoice']['registrationFeePaid'], variables['input']['registrationFeePaid'])


    # def test_create_invoice_anon_user(self):
    #     """ Don't allow creating account invoices for non-logged in users """
    #     query = self.invoice_create_mutation
        
    #     account = f.RegularUserFactory.create()
    #     organization_invoice = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_invoice.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_create_location_permission_granted(self):
    #     """ Allow creating invoices for users with permissions """
    #     query = self.invoice_create_mutation

    #     account = f.RegularUserFactory.create()
    #     organization_invoice = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_invoice.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     # Create regular user
    #     user = account
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['createFinanceInvoice']['financeInvoice']['organizationSubscription']['id'], 
    #         variables['input']['organizationSubscription']
    #     )


    # def test_create_invoice_permission_denied(self):
    #     """ Check create invoice permission denied error message """
    #     query = self.invoice_create_mutation
    #     account = f.RegularUserFactory.create()
    #     organization_invoice = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_invoice.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     # Create regular user
    #     user = account

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_update_invoice(self):
    #     """ Update a invoice """
    #     query = self.invoice_update_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     organization_invoice = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_invoice.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')

    #     self.assertEqual(
    #       data['updateFinanceInvoice']['financeInvoice']['organizationSubscription']['id'], 
    #       variables['input']['organizationSubscription']
    #     )
    #     self.assertEqual(
    #       data['updateFinanceInvoice']['financeInvoice']['financePaymentMethod']['id'], 
    #       variables['input']['financePaymentMethod']
    #     )
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateEnd'], variables['input']['dateEnd'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['note'], variables['input']['note'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['registrationFeePaid'], variables['input']['registrationFeePaid'])


    # def test_update_invoice_anon_user(self):
    #     """ Don't allow updating invoices for non-logged in users """
    #     query = self.invoice_update_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     organization_invoice = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_invoice.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_invoice_permission_granted(self):
    #     """ Allow updating invoices for users with permissions """
    #     query = self.invoice_update_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     organization_invoice = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_invoice.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     user = invoice.account
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateStart'], variables['input']['dateStart'])


    # def test_update_invoice_permission_denied(self):
    #     """ Check update invoice permission denied error message """
    #     query = self.invoice_update_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     organization_invoice = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_invoice.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

    #     user = invoice.account

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_delete_invoice(self):
    #     """ Delete an account invoice """
    #     query = self.invoice_delete_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     print(data)
    #     self.assertEqual(data['deleteFinanceInvoice']['ok'], True)


    # def test_delete_invoice_anon_user(self):
    #     """ Delete invoice denied for anon user """
    #     query = self.invoice_delete_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_delete_invoice_permission_granted(self):
    #     """ Allow deleting invoices for users with permissions """
    #     query = self.invoice_delete_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)

    #     # Give permissions
    #     user = invoice.account
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['deleteFinanceInvoice']['ok'], True)


    # def test_delete_invoice_permission_denied(self):
    #     """ Check delete invoice permission denied error message """
    #     query = self.invoice_delete_mutation
    #     invoice = f.FinanceInvoiceFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', invoice.id)
        
    #     user = invoice.account

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')

