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


class GQLFinanceQuoteItem(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['finance_quote_group.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financequoteitem'
        self.permission_add = 'add_financequoteitem'
        self.permission_change = 'change_financequoteitem'
        self.permission_delete = 'delete_financequoteitem'

        self.finance_tax_rate = f.FinanceTaxRateFactory.create()
        self.finance_glaccount = f.FinanceGLAccountFactory.create()
        self.finance_costcenter = f.FinanceCostCenterFactory.create()

        self.variables_create = {
            "input": {}
        }

        self.variables_update = {
            "input": {
              "productName": "Updated product",
              "description": "Updated description",
              "quantity": "10",
              "price": "12.51",
              "financeTaxRate": to_global_id("FinanceTaxRateNode", self.finance_tax_rate.pk),
              "financeGlaccount": to_global_id("FinanceGLAccountNode", self.finance_glaccount.pk),
              "financeCostcenter": to_global_id("FinanceCostCenterNode", self.finance_costcenter.pk)
            }
        }

        self.quote_items_query = '''
  query FinanceQuotesItems($financeQuote: ID!) {
    financeQuoteItems(first: 100, financeQuote: $financeQuote) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          financeQuote {
            id
          }
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
'''

        self.quote_item_query = '''
  query FinanceQuoteItem($id: ID!) {
    financeQuoteItem(id:$id) {
      id
      financeQuote {
        id
      }
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
'''

        self.quote_item_create_mutation = ''' 
  mutation CreateFinanceQuoteItem($input: CreateFinanceQuoteItemInput!) {
    createFinanceQuoteItem(input: $input) {
      financeQuoteItem {
        id
        financeQuote {
          id
        }
        lineNumber
        productName
        description
        quantity
        price
        financeTaxRate {
          id
          name
        }
      }
    }
  }
'''

        self.quote_item_update_mutation = '''
  mutation UpdateFinanceQuoteItem($input: UpdateFinanceQuoteItemInput!) {
    updateFinanceQuoteItem(input: $input) {
      financeQuoteItem {
        id
        financeQuote {
          id
        }
        lineNumber
        productName
        description
        quantity
        price
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

        self.quote_item_delete_mutation = '''
  mutation DeleteFinanceQuoteItem($input: DeleteFinanceQuoteItemInput!) {
    deleteFinanceQuoteItem(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account quote items """
        query = self.quote_items_query
        quote_item = f.FinanceQuoteItemFactory.create()

        variables = {
          "financeQuote": to_global_id('FinanceQuoteItemNode', quote_item.finance_quote.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['financeQuoteItems']['edges'][0]['node']['id'],
          to_global_id('FinanceQuoteItemNode', quote_item.id)
        )
        self.assertEqual(
          data['financeQuoteItems']['edges'][0]['node']['financeQuote']['id'],
          to_global_id('FinanceQuoteNode', quote_item.finance_quote.id)
        )
        self.assertEqual(data['financeQuoteItems']['edges'][0]['node']['lineNumber'], quote_item.line_number)
        self.assertEqual(data['financeQuoteItems']['edges'][0]['node']['productName'], quote_item.product_name)
        self.assertEqual(data['financeQuoteItems']['edges'][0]['node']['description'], quote_item.description)
        self.assertEqual(data['financeQuoteItems']['edges'][0]['node']['quantity'],
                         format(quote_item.quantity, ".2f"))
        self.assertEqual(data['financeQuoteItems']['edges'][0]['node']['price'],
                         format(quote_item.price, ".2f"))
        self.assertEqual(data['financeQuoteItems']['edges'][0]['node']['financeTaxRate']['id'], 
                         to_global_id('FinanceTaxRateNode', quote_item.finance_tax_rate.id))
        self.assertEqual(data['financeQuoteItems']['edges'][0]['node']['subtotal'],
                         format(quote_item.subtotal, ".2f"))
        self.assertEqual(data['financeQuoteItems']['edges'][0]['node']['tax'], format(quote_item.tax, ".2f"))
        self.assertEqual(data['financeQuoteItems']['edges'][0]['node']['total'], format(quote_item.total, ".2f"))
        self.assertEqual(data['financeQuoteItems']['edges'][0]['node']['financeGlaccount']['id'], 
                         to_global_id('FinanceGLAccountNode', quote_item.finance_glaccount.id))
        self.assertEqual(data['financeQuoteItems']['edges'][0]['node']['financeCostcenter']['id'], 
                         to_global_id('FinanceCostCenterNode', quote_item.finance_costcenter.id))

    def test_query_permission_denied(self):
        """ Query list of account quote items - check permission denied """
        query = self.quote_items_query
        quote_item = f.FinanceQuoteItemFactory.create()

        variables = {
          "financeQuote": to_global_id('FinanceQuoteItemNode', quote_item.finance_quote.pk)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=quote_item.finance_quote.account.id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of account quote items with view permission """
        query = self.quote_items_query
        quote_item = f.FinanceQuoteItemFactory.create()

        variables = {
          "financeQuote": to_global_id('FinanceQuoteItemNode', quote_item.finance_quote.pk)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=quote_item.finance_quote.account.id)
        permission = Permission.objects.get(codename='view_financequoteitem')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List selected quote items
        self.assertEqual(
          data['financeQuoteItems']['edges'][0]['node']['id'],
          to_global_id('FinanceQuoteItemNode', quote_item.id)
        )

    def test_query_anon_user(self):
        """ Query list of account quote items - anon user """
        query = self.quote_items_query
        quote_item = f.FinanceQuoteItemFactory.create()

        variables = {
          "financeQuote": to_global_id('FinanceQuoteItemNode', quote_item.finance_quote.pk)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account quote item as admin """   
        quote_item = f.FinanceQuoteItemFactory.create()
        
        variables = {
            "id": to_global_id("FinanceQuoteItemNode", quote_item.id),
        }

        # Now query single quote and check
        executed = execute_test_client_api_query(self.quote_item_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['financeQuoteItem']['id'],
            to_global_id('FinanceQuoteItemNode', quote_item.id)
        )

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account quote """   
        quote_item = f.FinanceQuoteItemFactory.create()
        
        variables = {
            "id": to_global_id("FinanceQuoteItemNode", quote_item.id),
        }

        # Now query single quote and check
        executed = execute_test_client_api_query(self.quote_item_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        quote_item = f.FinanceQuoteItemFactory.create()
        user = quote_item.finance_quote.account

        variables = {
            "id": to_global_id("FinanceQuoteItemNode", quote_item.id),
        }

        # Now query single quote and check
        executed = execute_test_client_api_query(self.quote_item_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        quote_item = f.FinanceQuoteItemFactory.create()
        user = quote_item.finance_quote.account
        permission = Permission.objects.get(codename='view_financequoteitem')
        user.user_permissions.add(permission)
        user.save()
        
        variables = {
            "id": to_global_id("FinanceQuoteItemNode", quote_item.id),
        }

        # Now query single quote and check   
        executed = execute_test_client_api_query(self.quote_item_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['financeQuoteItem']['id'],
            to_global_id('FinanceQuoteItemNode', quote_item.id)
        )

    def test_create_quote_item(self):
        """ Create an account quote """
        query = self.quote_item_create_mutation

        quote = f.FinanceQuoteFactory.create()
        variables = self.variables_create
        variables['input']['financeQuote'] = to_global_id('FinanceQuoteNode', quote.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        # Get quote
        rid = get_rid(data['createFinanceQuoteItem']['financeQuoteItem']['financeQuote']['id'])
        quote = models.FinanceQuote.objects.get(pk=rid.id)

        self.assertEqual(
            data['createFinanceQuoteItem']['financeQuoteItem']['financeQuote']['id'], 
            variables['input']['financeQuote']
        )

    def test_create_quote_item_increate_line_number(self):
        """ Create an account quote """
        query = self.quote_item_create_mutation

        quote = f.FinanceQuoteFactory.create()
        variables = self.variables_create
        variables['input']['financeQuote'] = to_global_id('FinanceQuoteNode', quote.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        # Get quote
        rid = get_rid(data['createFinanceQuoteItem']['financeQuoteItem']['financeQuote']['id'])
        quote = models.FinanceQuote.objects.get(pk=rid.id)

        self.assertEqual(
            data['createFinanceQuoteItem']['financeQuoteItem']['financeQuote']['id'], 
            variables['input']['financeQuote']
        )
        self.assertEqual(data['createFinanceQuoteItem']['financeQuoteItem']['lineNumber'], 0)

        # Execute again and check if the line number for the 2nd item = 1
        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['createFinanceQuoteItem']['financeQuoteItem']['lineNumber'], 1)

    def test_create_quote_item_anon_user(self):
        """ Don't allow creating account quotes for non-logged in users """
        query = self.quote_item_create_mutation

        quote = f.FinanceQuoteFactory.create()
        variables = self.variables_create
        variables['input']['financeQuote'] = to_global_id('FinanceQuoteNode', quote.id)
        
        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_quote_item_permission_granted(self):
        """ Allow creating quotes for users with permissions """
        query = self.quote_item_create_mutation

        quote = f.FinanceQuoteFactory.create()
        variables = self.variables_create
        variables['input']['financeQuote'] = to_global_id('FinanceQuoteNode', quote.id)

        # Create regular user
        user = get_user_model().objects.get(pk=quote.account.id)
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
            data['createFinanceQuoteItem']['financeQuoteItem']['financeQuote']['id'], 
            variables['input']['financeQuote']
        )

    def test_create_quote_item_permission_denied(self):
        """ Check create quote permission denied error message """
        query = self.quote_item_create_mutation

        quote = f.FinanceQuoteFactory.create()
        variables = self.variables_create
        variables['input']['financeQuote'] = to_global_id('FinanceQuoteNode', quote.id)

        # Create regular user
        user = get_user_model().objects.get(pk=quote.account.id)

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_quote_item(self):
        """ Update a quote item """
        query = self.quote_item_update_mutation

        quote_item = f.FinanceQuoteItemFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteItemNode', quote_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['updateFinanceQuoteItem']['financeQuoteItem']['productName'],
                         variables['input']['productName'])
        self.assertEqual(data['updateFinanceQuoteItem']['financeQuoteItem']['description'],
                         variables['input']['description'])
        self.assertEqual(data['updateFinanceQuoteItem']['financeQuoteItem']['quantity'],
                         variables['input']['quantity'])
        self.assertEqual(data['updateFinanceQuoteItem']['financeQuoteItem']['price'],
                         variables['input']['price'])
        self.assertEqual(
          data['updateFinanceQuoteItem']['financeQuoteItem']['financeTaxRate']['id'], 
          variables['input']['financeTaxRate']
        )
        self.assertEqual(
          data['updateFinanceQuoteItem']['financeQuoteItem']['financeGlaccount']['id'], 
          variables['input']['financeGlaccount']
        )
        self.assertEqual(
          data['updateFinanceQuoteItem']['financeQuoteItem']['financeCostcenter']['id'], 
          variables['input']['financeCostcenter']
        )

    def test_update_quote_item_line_number(self):
        """ Update a quote item line number"""
        query = self.quote_item_update_mutation
        query_create = self.quote_item_create_mutation

        quote = f.FinanceQuoteFactory.create()
        quote_item = f.FinanceQuoteItemFactory.create(
          finance_quote=quote
        )

        query_create = self.quote_item_create_mutation
        variables_create = self.variables_create
        variables_create['input']['financeQuote'] = to_global_id('FinanceQuoteNode', quote.id)

        # Add 2 more items
        # Execute again and check if the line number for the 2nd item = 1
        executed = execute_test_client_api_query(
            query_create, 
            self.admin_user, 
            variables=variables_create
        )

        data = executed.get('data')
        id_2 = data['createFinanceQuoteItem']['financeQuoteItem']['id']
        rid_2 = get_rid(id_2)
        line_nr_2 = data['createFinanceQuoteItem']['financeQuoteItem']['lineNumber']

        self.assertEqual(data['createFinanceQuoteItem']['financeQuoteItem']['lineNumber'], 1)

        # Execute again and check if the line number for the 3rd item = 2
        executed = execute_test_client_api_query(
            query_create, 
            self.admin_user, 
            variables=variables_create
        )

        data = executed.get('data')
        id_3 = data['createFinanceQuoteItem']['financeQuoteItem']['id']
        rid_3 = get_rid(id_3)
        line_nr_3 = data['createFinanceQuoteItem']['financeQuoteItem']['lineNumber']

        self.assertEqual(data['createFinanceQuoteItem']['financeQuoteItem']['lineNumber'], 2)

        variables = {
          "input": {
            "lineNumber": 0
          }
        }
        variables['input']['id'] = id_3

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateFinanceQuoteItem']['financeQuoteItem']['lineNumber'], 
          variables['input']['lineNumber']
        )

        item_1 = models.FinanceQuoteItem.objects.get(id=quote_item.id)
        item_2 = models.FinanceQuoteItem.objects.get(id=rid_2.id)
        item_3 = models.FinanceQuoteItem.objects.get(id=rid_3.id)
        self.assertEqual(item_1.line_number, 1)
        self.assertEqual(item_2.line_number, 2)
        self.assertEqual(item_3.line_number, 0)

    def test_update_quote_item_anon_user(self):
        """ Don't allow updating quotes for non-logged in users """
        query = self.quote_item_update_mutation

        quote_item = f.FinanceQuoteItemFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteItemNode', quote_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_quote_item_permission_granted(self):
        """ Allow updating quotes for users with permissions """
        query = self.quote_item_update_mutation

        quote_item = f.FinanceQuoteItemFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteItemNode', quote_item.id)

        user = quote_item.finance_quote.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateFinanceQuoteItem']['financeQuoteItem']['productName'], variables['input']['productName'])

    def test_update_quote_item_permission_denied(self):
        """ Check update quote permission denied error message """
        query = self.quote_item_update_mutation

        quote_item = f.FinanceQuoteItemFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteItemNode', quote_item.id)

        user = quote_item.finance_quote.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_quote_item(self):
        """ Delete an account quote item """
        query = self.quote_item_delete_mutation
        quote_item = f.FinanceQuoteItemFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceQuoteItemNode', quote_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceQuoteItem']['ok'], True)

    def test_delete_quote_item_check_line_number(self):
        """ Delete an account quote item """
        query = self.quote_item_delete_mutation
        quote = f.FinanceQuoteFactory.create()
        quote_item = f.FinanceQuoteItemFactory.create(
          finance_quote=quote
        )

        query_create = self.quote_item_create_mutation
        variables_create = self.variables_create
        variables_create['input']['financeQuote'] = to_global_id('FinanceQuoteNode', quote.id)

        # Add 2 more items
        # Execute again and check if the line number for the 2nd item = 1
        executed = execute_test_client_api_query(
            query_create, 
            self.admin_user, 
            variables=variables_create
        )

        data = executed.get('data')
        id_2 = data['createFinanceQuoteItem']['financeQuoteItem']['id']
        rid_2 = get_rid(id_2)
        line_nr_2 = data['createFinanceQuoteItem']['financeQuoteItem']['lineNumber']

        self.assertEqual(data['createFinanceQuoteItem']['financeQuoteItem']['lineNumber'], 1)

        # Execute again and check if the line number for the 3rd item = 2
        executed = execute_test_client_api_query(
            query_create, 
            self.admin_user, 
            variables=variables_create
        )
        data = executed.get('data')
        id_3 = data['createFinanceQuoteItem']['financeQuoteItem']['id']
        rid_3 = get_rid(id_3)
        line_nr_3 = data['createFinanceQuoteItem']['financeQuoteItem']['lineNumber']

        self.assertEqual(data['createFinanceQuoteItem']['financeQuoteItem']['lineNumber'], 2)
        
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceQuoteItemNode', quote_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceQuoteItem']['ok'], True)

        # Check re-numbering items 2 and 3
        item_2 = models.FinanceQuoteItem.objects.get(pk=rid_2.id)
        item_3 = models.FinanceQuoteItem.objects.get(pk=rid_3.id)

        self.assertEqual(item_2.line_number, line_nr_2 - 1)
        self.assertEqual(item_3.line_number, line_nr_3 - 1)

    def test_delete_quote_item_anon_user(self):
        """ Delete quote denied for anon user """
        query = self.quote_item_delete_mutation
        quote_item = f.FinanceQuoteItemFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceQuoteItemNode', quote_item.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_quote_item_permission_granted(self):
        """ Allow deleting quotes for users with permissions """
        query = self.quote_item_delete_mutation
        quote_item = f.FinanceQuoteItemFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceQuoteItemNode', quote_item.id)

        # Give permissions
        user = quote_item.finance_quote.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceQuoteItem']['ok'], True)

    def test_delete_quote_item_permission_denied(self):
        """ Check delete quote permission denied error message """
        query = self.quote_item_delete_mutation
        quote_item = f.FinanceQuoteItemFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('FinanceQuoteItemNode', quote_item.id)
        
        user = quote_item.finance_quote.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
