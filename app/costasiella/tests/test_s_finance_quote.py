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


class GQLFinanceQuote(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['app_settings.json', 'finance_quote_group.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financequote'
        self.permission_add = 'add_financequote'
        self.permission_change = 'change_financequote'
        self.permission_delete = 'delete_financequote'

        # self.account = f.RegularUserFactory.create()

        self.variables_create = {
            "input": {
                # Account will be added in the test create functions
                "financeQuoteGroup": to_global_id('FinanceQuoteGroupNode', 100),
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
              "quoteNumber": "INVT0001",
              "dateSent": "2019-01-03",
              "dateExpire": "2019-02-28",
              "status": "SENT",
              "terms": "Terms go there",
              "footer": "Footer here",
              "note": "Notes here"
            }
        }

        self.variables_cancel = {
            "input": {}
        }

        self.quotes_query = '''
  query FinanceQuotes($after: String, $before: String, $status: CostasiellaFinanceQuoteStatusChoices) {
    financeQuotes(first: 15, before: $before, after: $after, status: $status) {
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
          quoteNumber
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
          dateExpire
          total
          totalDisplay
        }
      }
    }
  }
'''

        self.quote_query = '''
  query FinanceQuote($id: ID!) {
    financeQuote(id:$id) {
      id
      account {
        id
        fullName
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
      quoteNumber
      dateSent
      dateExpire
      terms
      footer
      note
      subtotalDisplay
      taxDisplay
      totalDisplay
      updatedAt
    }
  }
'''

        self.quote_create_mutation = ''' 
  mutation CreateFinanceQuote($input: CreateFinanceQuoteInput!) {
    createFinanceQuote(input: $input) {
      financeQuote {
        id
        account {
          id
          fullName
        }
        business {
          id
        }
        financeQuoteGroup {
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
        quoteNumber
        dateSent
        dateExpire
        terms
        footer
        note
        subtotalDisplay
        taxDisplay
        totalDisplay
        updatedAt
      }
    }
  }
'''

        self.quote_update_mutation = '''
  mutation UpdateFinanceQuote($input: UpdateFinanceQuoteInput!) {
    updateFinanceQuote(input: $input) {
      financeQuote {
        id
        account {
          id
          fullName
        }
        business {
          id
        }
        financeQuoteGroup {
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
        quoteNumber
        dateSent
        dateExpire
        terms
        footer
        note
        subtotalDisplay
        taxDisplay
        totalDisplay
        updatedAt 
      }
    }
  }
'''

        self.quote_delete_mutation = '''
  mutation DeleteFinanceQuote($input: DeleteFinanceQuoteInput!) {
    deleteFinanceQuote(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account quotes """
        query = self.quotes_query
        quote = f.FinanceQuoteFactory.create()
        quote.save()

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')

        self.assertEqual(
            data['financeQuotes']['edges'][0]['node']['account']['id'], 
            to_global_id("AccountNode", quote.account.id)
        )
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['quoteNumber'], quote.quote_number)
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['dateSent'], str(timezone.now().date()))
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['dateExpire'], 
          str(timezone.now().date() + datetime.timedelta(days=quote.finance_quote_group.expires_after_days))
        )
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['summary'], quote.summary)
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['relationCompany'], quote.relation_company)
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['relationCompanyRegistration'], quote.relation_company_registration)
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['relationCompanyTaxRegistration'], quote.relation_company_tax_registration)
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['relationContactName'], quote.relation_contact_name)
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['relationAddress'], quote.relation_address)
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['relationPostcode'], quote.relation_postcode)
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['relationCity'], quote.relation_city)
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['relationCountry'], quote.relation_country)
        self.assertEqual(data['financeQuotes']['edges'][0]['node']['status'], quote.status)

    # def test_query_status_filter(self):
    #     """ Query list of account quotes - filtered by status """
    #     query = self.quotes_query
    #     quote = f.FinanceQuoteFactory.create()
    #     quote.status = "SENT"
    #     quote.finance_payment_method = f.FinancePaymentMethodFactory()
    #     quote.save()
    #
    #     variables = {
    #         "status": "SENT"
    #     }
    #
    #     executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     # Make sure the quote is in the list returned
    #     self.assertEqual(
    #         data['financeQuotes']['edges'][0]['node']['id'],
    #         to_global_id("FinanceQuoteNode", quote.id)
    #     )

    def test_query_permission_denied(self):
        """ Query list of account quotes - check permission denied
        A user can query the quotes linked to their account, so an error will never be thrown
        But a user shouldn't be able to view orders from other accounts without additional permission
        """
        query = self.quotes_query
        quote = f.FinanceQuoteFactory.create()
        other_user = f.InstructorFactory.create()

        # Create regular user
        user = get_user_model().objects.get(pk=quote.account.id)
        executed = execute_test_client_api_query(query, other_user)
        data = executed.get('data')

        for item in data['financeQuotes']['edges']:
            node = item['node']
            self.assertNotEqual(node['account']['id'], to_global_id("AccountNode", user.id))

    def test_query_permission_granted(self):
        """ Query list of account quotes with view permission """
        query = self.quotes_query
        quote = f.FinanceQuoteFactory.create()

        # Create regular user
        user = get_user_model().objects.get(pk=quote.account.id)
        permission = Permission.objects.get(codename='view_financequote')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user)
        data = executed.get('data')

        # List all quotes
        self.assertEqual(
            data['financeQuotes']['edges'][0]['node']['account']['id'], 
            to_global_id("AccountNode", quote.account.id)
        )

    def test_query_anon_user(self):
        """ Query list of account quotes - anon user """
        query = self.quotes_query
        quote = f.FinanceQuoteFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account quote as admin """   
        quote = f.FinanceQuoteFactory.create()

        variables = {
            "id": to_global_id("FinanceQuoteNode", quote.id),
        }

        # Now query single quote and check
        executed = execute_test_client_api_query(self.quote_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['financeQuote']['account']['id'], 
            to_global_id("AccountNode", quote.account.id)
        )
        self.assertEqual(data['financeQuote']['quoteNumber'], quote.quote_number)
        self.assertEqual(data['financeQuote']['dateSent'], str(timezone.now().date()))
        self.assertEqual(data['financeQuote']['dateExpire'], 
          str(timezone.now().date() + datetime.timedelta(days=quote.finance_quote_group.expires_after_days))
        )
        self.assertEqual(data['financeQuote']['summary'], quote.summary)
        self.assertEqual(data['financeQuote']['relationCompany'], quote.relation_company)
        self.assertEqual(data['financeQuote']['relationCompanyRegistration'], quote.relation_company_registration)
        self.assertEqual(data['financeQuote']['relationCompanyTaxRegistration'], quote.relation_company_tax_registration)
        self.assertEqual(data['financeQuote']['relationContactName'], quote.relation_contact_name)
        self.assertEqual(data['financeQuote']['relationAddress'], quote.relation_address)
        self.assertEqual(data['financeQuote']['relationPostcode'], quote.relation_postcode)
        self.assertEqual(data['financeQuote']['relationCity'], quote.relation_city)
        self.assertEqual(data['financeQuote']['relationCountry'], quote.relation_country)
        self.assertEqual(data['financeQuote']['status'], quote.status)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account quote """   
        quote = f.FinanceQuoteFactory.create()

        variables = {
            "id": to_global_id("FinanceQuoteNode", quote.id),
        }

        # Now query single quote and check
        executed = execute_test_client_api_query(self.quote_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        quote = f.FinanceQuoteFactory.create()
        user = f.Instructor2Factory.create()

        variables = {
            "id": to_global_id("FinanceQuoteNode", quote.id),
        }

        # Now query single quote and check
        executed = execute_test_client_api_query(self.quote_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        quote = f.FinanceQuoteFactory.create()
        user = quote.account
        permission = Permission.objects.get(codename='view_financequote')
        user.user_permissions.add(permission)
        user.save()
        

        variables = {
            "id": to_global_id("FinanceQuoteNode", quote.id),
        }

        # Now query single quote and check   
        executed = execute_test_client_api_query(self.quote_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['financeQuote']['account']['id'], 
            to_global_id('AccountNode', quote.account.id)
        )

    def test_create_quote_for_account(self):
        """ Create an account quote """
        query = self.quote_create_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        # Get quote
        rid = get_rid(data['createFinanceQuote']['financeQuote']['id'])
        quote = models.FinanceQuote.objects.get(pk=rid.id)

        self.assertEqual(
            data['createFinanceQuote']['financeQuote']['account']['id'], 
            variables['input']['account']
        )
        self.assertEqual(
            data['createFinanceQuote']['financeQuote']['financeQuoteGroup']['id'], 
            variables['input']['financeQuoteGroup']
        )
        self.assertEqual(data['createFinanceQuote']['financeQuote']['dateSent'], str(timezone.now().date()))
        self.assertEqual(data['createFinanceQuote']['financeQuote']['dateExpire'], 
            str(timezone.now().date() + datetime.timedelta(days=quote.finance_quote_group.expires_after_days))
        )
        self.assertEqual(data['createFinanceQuote']['financeQuote']['summary'], variables['input']['summary'])
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationCompany'], "")
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationCompanyRegistration'], "")
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationCompanyTaxRegistration'], "")
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationContactName'], account.full_name)
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationAddress'],
                         account.address)
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationPostcode'],
                         account.postcode)
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationCity'],
                         account.city)
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationCountry'],
                         account.country)

    def test_create_quote_for_business(self):
        """ Create an quote for a b2b relation"""
        query = self.quote_create_mutation

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

        # Get quote
        rid = get_rid(data['createFinanceQuote']['financeQuote']['id'])
        quote = models.FinanceQuote.objects.get(pk=rid.id)

        self.assertEqual(
            data['createFinanceQuote']['financeQuote']['account']['id'],
            variables['input']['account']
        )
        self.assertEqual(
            data['createFinanceQuote']['financeQuote']['business']['id'],
            variables['input']['business']
        )
        self.assertEqual(
            data['createFinanceQuote']['financeQuote']['financeQuoteGroup']['id'],
            variables['input']['financeQuoteGroup']
        )
        self.assertEqual(
            data['createFinanceQuote']['financeQuote']['relationCompany'],
            business.name
        )
        self.assertEqual(
            data['createFinanceQuote']['financeQuote']['relationCompanyRegistration'],
            business.registration
        )
        self.assertEqual(
            data['createFinanceQuote']['financeQuote']['relationCompanyTaxRegistration'],
            business.tax_registration
        )
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationContactName'],
                         "")
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationAddress'],
                         business.address)
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationPostcode'],
                         business.postcode)
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationCity'],
                         business.city)
        self.assertEqual(data['createFinanceQuote']['financeQuote']['relationCountry'],
                         business.country)

    def test_create_quote_group_id_plus_one(self):
        """ Create an account quote and check whether the FinanceInoiceGroup next id field increated by 1 """
        query = self.quote_create_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)

        finance_quote_group = models.FinanceQuoteGroup.objects.get(pk=100)
        next_id_before = finance_quote_group.next_id

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        # Get quote
        rid = get_rid(data['createFinanceQuote']['financeQuote']['id'])
        quote = models.FinanceQuote.objects.get(pk=rid.id)

        self.assertEqual(
            data['createFinanceQuote']['financeQuote']['account']['id'],
            variables['input']['account']
        )

        finance_quote_group = models.FinanceQuoteGroup.objects.get(pk=100)
        next_id_after = finance_quote_group.next_id

        self.assertEqual((next_id_before + 1), next_id_after)

    def test_create_quote_anon_user(self):
        """ Don't allow creating account quotes for non-logged in users """
        query = self.quote_create_mutation
        
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

    def test_create_quote_permission_granted(self):
        """ Allow creating quotes for users with permissions """
        query = self.quote_create_mutation

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
            data['createFinanceQuote']['financeQuote']['account']['id'], 
            variables['input']['account']
        )

    def test_create_quote_permission_denied(self):
        """ Check create quote permission denied error message """
        query = self.quote_create_mutation

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

    def test_update_quote_address_from_account(self):
        """ Update a quote """
        query = self.quote_update_mutation

        quote = f.FinanceQuoteFactory.create()
        account = quote.account
        business = f.BusinessB2BFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteNode', quote.id)
        variables['input']['business'] = None  # Set business to None to have the address set to relation fields

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')

        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCompany'], "")
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCompanyRegistration'], "")
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCompanyTaxRegistration'], "")
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationContactName'], account.full_name)
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationAddress'],
                         account.address)
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationPostcode'],
                         account.postcode)
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCity'],
                         account.city)
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCountry'],
                         account.country)
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['quoteNumber'],
                         variables['input']['quoteNumber'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['dateSent'], variables['input']['dateSent'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['dateExpire'], variables['input']['dateExpire'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['status'], variables['input']['status'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['summary'], variables['input']['summary'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['terms'], variables['input']['terms'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['footer'], variables['input']['footer'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['note'], variables['input']['note'])

    def test_update_quote_address_from_business(self):
        """ Update a quote """
        query = self.quote_update_mutation

        quote = f.FinanceQuoteFactory.create()
        business = f.BusinessB2BFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteNode', quote.id)
        variables['input']['business'] = to_global_id("BusinessNode", business.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')

        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCompany'],
                         business.name)
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCompanyRegistration'],
                         business.registration)
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCompanyTaxRegistration'],
                         business.tax_registration)
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationContactName'],
                         "")
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationAddress'],
                         business.address)
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationPostcode'],
                         business.postcode)
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCity'],
                         business.city)
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCountry'],
                         business.country)
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['quoteNumber'],
                         variables['input']['quoteNumber'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['dateSent'], variables['input']['dateSent'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['dateExpire'], variables['input']['dateExpire'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['status'], variables['input']['status'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['summary'], variables['input']['summary'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['terms'], variables['input']['terms'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['footer'], variables['input']['footer'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['note'], variables['input']['note'])

    def test_update_quote_custom_to(self):
        """ Update a quote """
        query = self.quote_update_mutation

        quote = f.FinanceQuoteFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteNode', quote.id)
        variables['input']['customTo'] = True

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')

        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCompany'], variables['input']['relationCompany'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCompanyRegistration'], variables['input']['relationCompanyRegistration'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationContactName'], variables['input']['relationContactName'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationAddress'], variables['input']['relationAddress'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationPostcode'], variables['input']['relationPostcode'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCity'], variables['input']['relationCity'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['relationCountry'], variables['input']['relationCountry'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['quoteNumber'], variables['input']['quoteNumber'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['dateSent'], variables['input']['dateSent'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['dateExpire'], variables['input']['dateExpire'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['status'], variables['input']['status'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['summary'], variables['input']['summary'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['terms'], variables['input']['terms'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['footer'], variables['input']['footer'])
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['note'], variables['input']['note'])

    def test_update_quote_anon_user(self):
        """ Don't allow updating quotes for non-logged in users """
        query = self.quote_update_mutation
        quote = f.FinanceQuoteFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteNode', quote.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_quote_permission_granted(self):
        """ Allow updating quotes for users with permissions """
        query = self.quote_update_mutation
        quote = f.FinanceQuoteFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteNode', quote.id)

        user = quote.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinanceQuote']['financeQuote']['dateSent'], variables['input']['dateSent'])

    def test_update_quote_permission_denied(self):
        """ Check update quote permission denied error message """
        query = self.quote_update_mutation
        quote = f.FinanceQuoteFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteNode', quote.id)

        user = quote.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_quote(self):
        """ Delete an account quote """
        query = self.quote_delete_mutation
        quote = f.FinanceQuoteFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceQuoteNode', quote.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceQuote']['ok'], True)

    def test_delete_quote_anon_user(self):
        """ Delete quote denied for anon user """
        query = self.quote_delete_mutation
        quote = f.FinanceQuoteFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('FinanceQuoteNode', quote.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_quote_permission_granted(self):
        """ Allow deleting quotes for users with permissions """
        query = self.quote_delete_mutation
        quote = f.FinanceQuoteFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceQuoteNode', quote.id)

        # Give permissions
        user = quote.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceQuote']['ok'], True)

    def test_delete_quote_permission_denied(self):
        """ Check delete quote permission denied error message """
        query = self.quote_delete_mutation
        quote = f.FinanceQuoteFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceQuoteNode', quote.id)
        
        user = quote.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

