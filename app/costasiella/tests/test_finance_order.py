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



class GQLFinanceOrder(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financeorder'
        self.permission_add = 'add_financeorder'
        self.permission_change = 'change_financeorder'
        self.permission_delete = 'delete_financeorder'

        self.organization_classpass = f.OrganizationClasspassFactory.create()

        self.variables_create_classpass = {
            "input": {
                "organization_classpass": to_global_id('OrganizationClasspassNode', self.organization_classpass.id),
                "messsage": "customers' message",

            }
        }

        # self.variables_update = {
        #     "input": {
        #       "summary": "create summary",
        #       "relationCompany": "ACME INC.",
        #       "relationCompanyRegistration": "ACME 4312",
        #       "relationCompanyTaxRegistration": "ACME TAX 99",
        #       "relationContactName": "Contact person",
        #       "relationAddress": "Street 1",
        #       "relationPostcode": "1233434 545",
        #       "relationCity": "Amsterdam",
        #       "relationCountry": "NL",
        #       "orderNumber": "INVT0001",
        #       "dateSent": "2019-01-03",
        #       "dateDue": "2019-02-28",
        #       "status": "SENT",
        #       "terms": "Terms go there",
        #       "footer": "Footer here",
        #       "note": "Notes here"
        #     }
        # }

        self.orders_query = '''
  query FinanceOrders($after: String, $before: String, $status: String) {
    financeOrders(first: 15, before: $before, after: $after, status: $status) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          orderNumber
          account {
            id
            fullName
          }
          message
          status
          total
          totalDisplay
          createdAt
        }
      }
    }
  }
'''

#         self.order_query = '''
#   query FinanceInvoice($id: ID!) {
#     financeInvoice(id:$id) {
#       id
#       account {
#         id
#         fullName
#       }
#       financePaymentMethod {
#         id
#         name
#       }
#       relationCompany
#       relationCompanyRegistration
#       relationCompanyTaxRegistration
#       relationContactName
#       relationAddress
#       relationPostcode
#       relationCity
#       relationCountry
#       status
#       summary
#       orderNumber
#       dateSent
#       dateDue
#       terms
#       footer
#       note
#       subtotalDisplay
#       taxDisplay
#       totalDisplay
#       paidDisplay
#       balanceDisplay
#       updatedAt
#     }
#   }
# '''
#
#         self.order_create_mutation = '''
#   mutation CreateFinanceInvoice($input: CreateFinanceInvoiceInput!) {
#     createFinanceInvoice(input: $input) {
#       financeInvoice {
#         id
#         account {
#           id
#           fullName
#         }
#         financeInvoiceGroup {
#           id
#           name
#         }
#         financePaymentMethod {
#           id
#           name
#         }
#         relationCompany
#         relationCompanyRegistration
#         relationCompanyTaxRegistration
#         relationContactName
#         relationAddress
#         relationPostcode
#         relationCity
#         relationCountry
#         status
#         summary
#         orderNumber
#         dateSent
#         dateDue
#         terms
#         footer
#         note
#         subtotalDisplay
#         taxDisplay
#         totalDisplay
#         paidDisplay
#         balanceDisplay
#         updatedAt
#       }
#     }
#   }
# '''
#
#         self.order_update_mutation = '''
#   mutation UpdateFinanceInvoice($input: UpdateFinanceInvoiceInput!) {
#     updateFinanceInvoice(input: $input) {
#       financeInvoice {
#         id
#         account {
#           id
#           fullName
#         }
#         financeInvoiceGroup {
#           id
#           name
#         }
#         financePaymentMethod {
#           id
#           name
#         }
#         relationCompany
#         relationCompanyRegistration
#         relationCompanyTaxRegistration
#         relationContactName
#         relationAddress
#         relationPostcode
#         relationCity
#         relationCountry
#         status
#         summary
#         orderNumber
#         dateSent
#         dateDue
#         terms
#         footer
#         note
#         subtotalDisplay
#         taxDisplay
#         totalDisplay
#         paidDisplay
#         balanceDisplay
#         updatedAt
#       }
#     }
#   }
# '''
#
#         self.order_delete_mutation = '''
#   mutation DeleteFinanceInvoice($input: DeleteFinanceInvoiceInput!) {
#     deleteFinanceInvoice(input: $input) {
#       ok
#     }
#   }
# '''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of finance orders """
        query = self.orders_query
        order = f.FinanceOrderFactory.create()
        order.save()

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')

        self.assertEqual(
            data['financeOrders']['edges'][0]['node']['account']['id'],
            to_global_id("AccountNode", order.account.id)
        )
        self.assertEqual(data['financeOrders']['edges'][0]['node']['status'], order.status)
        self.assertEqual(data['financeOrders']['edges'][0]['node']['message'], order.message)

    def test_query_permision_denied(self):
        """ Query list of finance orders - check permission denied """
        query = self.orders_query
        order = f.FinanceOrderFactory.create()

        # Create regular user
        user = get_user_model().objects.get(pk=order.account.id)
        executed = execute_test_client_api_query(query, user)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of finance orders with view permission """
        query = self.orders_query
        order = f.FinanceOrderFactory.create()

        # Create regular user
        user = get_user_model().objects.get(pk=order.account.id)
        permission = Permission.objects.get(codename='view_financeorder')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user)
        data = executed.get('data')

        print("################")
        print(data)

        # List all orders
        self.assertEqual(
            data['financeOrders']['edges'][0]['node']['account']['id'],
            to_global_id("AccountNode", order.account.id)
        )

    def test_query_anon_user(self):
        """ Query list of finance orders - anon user """
        query = self.orders_query
        order = f.FinanceOrderFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    #
    # def test_query_one(self):
    #     """ Query one account order as admin """
    #     order = f.FinanceOrderFactory.create()
    #
    #
    #     variables = {
    #         "id": to_global_id("FinanceInvoiceNode", order.id),
    #     }
    #
    #     # Now query single order and check
    #     executed = execute_test_client_api_query(self.order_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     self.assertEqual(
    #         data['financeInvoice']['account']['id'],
    #         to_global_id("AccountNode", order.account.id)
    #     )
    #     self.assertEqual(data['financeInvoice']['orderNumber'], order.order_number)
    #     self.assertEqual(data['financeInvoice']['dateSent'], str(timezone.now().date()))
    #     self.assertEqual(data['financeInvoice']['dateDue'],
    #       str(timezone.now().date() + datetime.timedelta(days=order.finance_order_group.due_after_days))
    #     )
    #     self.assertEqual(data['financeInvoice']['summary'], order.summary)
    #     self.assertEqual(data['financeInvoice']['relationCompany'], order.relation_company)
    #     self.assertEqual(data['financeInvoice']['relationCompanyRegistration'], order.relation_company_registration)
    #     self.assertEqual(data['financeInvoice']['relationCompanyTaxRegistration'], order.relation_company_tax_registration)
    #     self.assertEqual(data['financeInvoice']['relationContactName'], order.relation_contact_name)
    #     self.assertEqual(data['financeInvoice']['relationAddress'], order.relation_address)
    #     self.assertEqual(data['financeInvoice']['relationPostcode'], order.relation_postcode)
    #     self.assertEqual(data['financeInvoice']['relationCity'], order.relation_city)
    #     self.assertEqual(data['financeInvoice']['relationCountry'], order.relation_country)
    #     self.assertEqual(data['financeInvoice']['status'], order.status)
    #
    #
    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one account order """
    #     order = f.FinanceOrderFactory.create()
    #
    #     variables = {
    #         "id": to_global_id("FinanceInvoiceNode", order.id),
    #     }
    #
    #     # Now query single order and check
    #     executed = execute_test_client_api_query(self.order_query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    #
    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """
    #     # Create regular user
    #     order = f.FinanceOrderFactory.create()
    #     user = order.account
    #
    #     variables = {
    #         "id": to_global_id("FinanceInvoiceNode", order.id),
    #     }
    #
    #     # Now query single order and check
    #     executed = execute_test_client_api_query(self.order_query, user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    #
    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """
    #     order = f.FinanceOrderFactory.create()
    #     user = order.account
    #     permission = Permission.objects.get(codename='view_financeorder')
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #
    #     variables = {
    #         "id": to_global_id("FinanceInvoiceNode", order.id),
    #     }
    #
    #     # Now query single order and check
    #     executed = execute_test_client_api_query(self.order_query, user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['financeInvoice']['account']['id'],
    #         to_global_id('AccountNode', order.account.id)
    #     )
    #
    #
    # def test_create_order(self):
    #     """ Create an account order """
    #     query = self.order_create_mutation
    #
    #     account = f.RegularUserFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #
    #     # Get order
    #     rid = get_rid(data['createFinanceInvoice']['financeInvoice']['id'])
    #     order = models.FinanceInvoice.objects.get(pk=rid.id)
    #
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
    #       str(timezone.now().date() + datetime.timedelta(days=order.finance_order_group.due_after_days))
    #     )
    #     self.assertEqual(data['createFinanceInvoice']['financeInvoice']['summary'], variables['input']['summary'])
    #
    #
    # def test_create_order_anon_user(self):
    #     """ Don't allow creating finance orders for non-logged in users """
    #     query = self.order_create_mutation
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
    #
    # def test_create_location_permission_granted(self):
    #     """ Allow creating orders for users with permissions """
    #     query = self.order_create_mutation
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
    #
    # def test_create_order_permission_denied(self):
    #     """ Check create order permission denied error message """
    #     query = self.order_create_mutation
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
    #
    # def test_update_order(self):
    #     """ Update a order """
    #     query = self.order_update_mutation
    #
    #     order = f.FinanceOrderFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', order.id)
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
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['orderNumber'], variables['input']['orderNumber'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateSent'], variables['input']['dateSent'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['dateDue'], variables['input']['dateDue'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['status'], variables['input']['status'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['summary'], variables['input']['summary'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['terms'], variables['input']['terms'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['footer'], variables['input']['footer'])
    #     self.assertEqual(data['updateFinanceInvoice']['financeInvoice']['note'], variables['input']['note'])
    #
    #
    # def test_update_order_anon_user(self):
    #     """ Don't allow updating orders for non-logged in users """
    #     query = self.order_update_mutation
    #     order = f.FinanceOrderFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', order.id)
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
    # def test_update_order_permission_granted(self):
    #     """ Allow updating orders for users with permissions """
    #     query = self.order_update_mutation
    #     order = f.FinanceOrderFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', order.id)
    #
    #     user = order.account
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
    #
    # def test_update_order_permission_denied(self):
    #     """ Check update order permission denied error message """
    #     query = self.order_update_mutation
    #     order = f.FinanceOrderFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', order.id)
    #
    #     user = order.account
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
    # def test_delete_order(self):
    #     """ Delete an account order """
    #     query = self.order_delete_mutation
    #     order = f.FinanceOrderFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', order.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['deleteFinanceInvoice']['ok'], True)
    #
    #
    # def test_delete_order_anon_user(self):
    #     """ Delete order denied for anon user """
    #     query = self.order_delete_mutation
    #     order = f.FinanceOrderFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', order.id)
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
    # def test_delete_order_permission_granted(self):
    #     """ Allow deleting orders for users with permissions """
    #     query = self.order_delete_mutation
    #     order = f.FinanceOrderFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', order.id)
    #
    #     # Give permissions
    #     user = order.account
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
    #
    # def test_delete_order_permission_denied(self):
    #     """ Check delete order permission denied error message """
    #     query = self.order_delete_mutation
    #     order = f.FinanceOrderFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('FinanceInvoiceNode', order.id)
    #
    #     user = order.account
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
