# from graphql.error.located_error import GraphQLLocatedError

from django.utils.translation import gettext as _
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
    fixtures = ['app_settings.json', 'organization.json', 'system_mail_template.json', 'system_notification']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financeorder'
        self.permission_add = 'add_financeorder'
        self.permission_change = 'change_financeorder'
        self.permission_delete = 'delete_financeorder'

        self.variables_create = {
            "input": {
                "message": "Hello world!",
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
  query FinanceOrders($after: String, $before: String, $status: CostasiellaFinanceOrderStatusChoices) {
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

        self.order_query = '''
  query FinanceOrder($id: ID!) {
    financeOrder(id: $id) {
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
      items {
        edges {
          node {
            id
            productName
          }
        }
      }   
    }
  }
'''

        self.order_create_mutation = '''
  mutation CreateFinanceOrder($input: CreateFinanceOrderInput!) {
    createFinanceOrder(input: $input) {
      financeOrder {
        id
        account {
            id
        }
        message
        status
        createdAt
      }
    }
  }
'''
#
#         self.order_update_mutation = '''
#   mutation UpdateFinanceOrder($input: UpdateFinanceOrderInput!) {
#     updateFinanceOrder(input: $input) {
#       financeOrder {
#         id
#         account {
#           id
#           fullName
#         }
#         financeOrderGroup {
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
        self.order_delete_mutation = '''
  mutation DeleteFinanceOrder($input: DeleteFinanceOrderInput!) {
    deleteFinanceOrder(input: $input) {
      ok
    }
  }
'''

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

    def test_query_permission_denied(self):
        """ Query list of finance orders - check permission denied
        A user can query the orders linked to their account, so an error will never be thrown
        But a user shouldn't be able to view orders from other accounts without additional permission
        """
        query = self.orders_query
        order = f.FinanceOrderFactory.create()
        other_user = f.InstructorFactory.create()

        # Query as another use and verify oder is not visible
        user = get_user_model().objects.get(pk=order.account.id)
        executed = execute_test_client_api_query(query, other_user)
        data = executed.get('data')

        for item in data['financeOrders']['edges']:
            node = item['node']
            self.assertNotEqual(node['account']['id'], to_global_id("AccountNode", user.id))

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
    
    def test_query_one(self):
        """ Query one finance order as admin """
        order = f.FinanceOrderFactory.create()
        variables = {
            "id": to_global_id("FinanceOrderNode", order.id),
        }

        # Now query single order and check
        executed = execute_test_client_api_query(self.order_query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['financeOrder']['account']['id'],
            to_global_id("AccountNode", order.account.id)
        )
        self.assertEqual(data['financeOrder']['message'], order.message)
        self.assertEqual(data['financeOrder']['status'], order.status)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one finance order """
        order = f.FinanceOrderFactory.create()

        variables = {
            "id": to_global_id("FinanceOrderNode", order.id),
        }

        # Now query single order and check
        executed = execute_test_client_api_query(self.order_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_granted_own_account(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        order = f.FinanceOrderFactory.create()
        user = order.account

        variables = {
            "id": to_global_id("FinanceOrderNode", order.id),
        }

        # Now query single order and check
        executed = execute_test_client_api_query(self.order_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['financeOrder']['account']['id'],
            to_global_id('AccountNode', order.account.id)
        )

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        order = f.FinanceOrderFactory.create()
        user = order.account
        permission = Permission.objects.get(codename='view_financeorder')
        user.user_permissions.add(permission)
        user.save()

        variables = {
            "id": to_global_id("FinanceOrderNode", order.id),
        }
        # Now query single order and check
        executed = execute_test_client_api_query(self.order_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['financeOrder']['account']['id'],
            to_global_id('AccountNode', order.account.id)
        )

    def test_query_one_permission_denied_other_account(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        order = f.FinanceOrderFactory.create()
        user = f.Instructor2Factory.create()

        variables = {
            "id": to_global_id("FinanceOrderNode", order.id),
        }

        # Now query single order and check
        executed = execute_test_client_api_query(self.order_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_create_order_free_classpass(self):
        """ Create finance order with free class pass"""
        query = self.order_create_mutation

        terms_and_conditions = f.OrganizationDocumentFactory.create()
        privacy_policy = f.OrganizationDocumentPrivacyPolicyFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create(
            price=0,
            finance_tax_rate=None
        )
        variables = self.variables_create
        variables['input']['organizationClasspass'] = to_global_id(
            'OrganizationClasspassNode', organization_classpass.id
        )

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        # Get order
        rid = get_rid(data['createFinanceOrder']['financeOrder']['id'])
        order = models.FinanceOrder.objects.get(pk=rid.id)

        self.assertEqual(
            data['createFinanceOrder']['financeOrder']['account']['id'],
            to_global_id('AccountNode', self.admin_user.pk)
        )

        # Verify that classpass item was added to the order
        first_item = order.items.first()
        self.assertEqual(first_item.product_name, "Class pass")
        self.assertEqual(first_item.total, organization_classpass.price)
        self.assertEqual(first_item.description, organization_classpass.name)
        self.assertEqual(first_item.quantity, 1)

        # Verify that the order was delivered
        self.assertEqual(order.status, "DELIVERED")

        qs_account_classpass = models.AccountClasspass.objects.filter(
            account=self.admin_user,
            organization_classpass=organization_classpass
        )
        self.assertEqual(qs_account_classpass.exists(), True)

    def test_create_order_classpass(self):
        """ Create finance order with class pass"""
        query = self.order_create_mutation

        terms_and_conditions = f.OrganizationDocumentFactory.create()
        privacy_policy = f.OrganizationDocumentPrivacyPolicyFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_create
        variables['input']['organizationClasspass'] = to_global_id(
            'OrganizationClasspassNode', organization_classpass.id
        )

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        # Get order
        rid = get_rid(data['createFinanceOrder']['financeOrder']['id'])
        order = models.FinanceOrder.objects.get(pk=rid.id)

        self.assertEqual(
            data['createFinanceOrder']['financeOrder']['account']['id'],
            to_global_id('AccountNode', self.admin_user.pk)
        )
        self.assertEqual(data['createFinanceOrder']['financeOrder']['message'], variables['input']['message'])
        self.assertEqual(data['createFinanceOrder']['financeOrder']['status'], 'AWAITING_PAYMENT')

        # Verify that classpass item was added to the order
        first_item = order.items.first()
        self.assertEqual(first_item.product_name, "Class pass")
        self.assertEqual(first_item.price, organization_classpass.price)
        self.assertEqual(first_item.total, organization_classpass.price)
        self.assertEqual(first_item.description, organization_classpass.name)
        self.assertEqual(first_item.quantity, 1)
        self.assertEqual(first_item.finance_tax_rate, organization_classpass.finance_tax_rate)

        # Verify that accepted documents have been added to the account placing the order
        qs_terms = models.AccountAcceptedDocument.objects.filter(
            account=self.admin_user,
            document=terms_and_conditions
        )
        self.assertEqual(qs_terms.exists(), True)
        qs_privacy = models.AccountAcceptedDocument.objects.filter(
            account=self.admin_user,
            document=privacy_policy
        )
        self.assertEqual(qs_privacy.exists(), True)

    def test_create_order_classpass_trial_over_limit_shouldnt_work(self):
        """ Don't create an order for a trial pass if the customer is over the trial limit """
        query = self.order_create_mutation

        account_classpass = f.AccountClasspassFactory.create()
        account = account_classpass.account
        organization_classpass = account_classpass.organization_classpass
        organization_classpass.trial_pass = True
        organization_classpass.save()

        setting = models.SystemSetting(
            setting="workflow_trial_pass_limit",
            value="1"
        )
        setting.save()

        organization_classpass = account_classpass.organization_classpass
        variables = self.variables_create
        variables['input']['organizationClasspass'] = to_global_id(
            'OrganizationClasspassNode', organization_classpass.id
        )

        executed = execute_test_client_api_query(
            query,
            account,
            variables=variables
        )
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], "Unable to create order: Trial limit reached.")

    def test_create_order_anon_user(self):
        """ Don't allow creating finance orders for non-logged in users """
        query = self.order_create_mutation

        organization_classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_create
        variables['input']['organizationClasspass'] = to_global_id(
            'OrganizationClasspassNode', organization_classpass.id
        )

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_order_permission_granted(self):
        """ Allow creating orders for users with permissions """
        query = self.order_create_mutation

        organization_classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_create
        variables['input']['organizationClasspass'] = to_global_id(
            'OrganizationClasspassNode', organization_classpass.id
        )

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
            data['createFinanceOrder']['financeOrder']['account']['id'],
            to_global_id('AccountNode', user.pk)
        )

    # All logged in users can create orders for their account.

    # def test_create_order_permission_denied(self):
    #     """ Check create order permission denied error message """
    #     query = self.order_create_mutation
    #
    #     organization_classpass = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_create
    #     variables['input']['organizationClasspass'] = to_global_id(
    #         'OrganizationClasspassNode', organization_classpass.id
    #     )
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


    # def test_update_order(self):
    #     """ Update a order """
    #     query = self.order_update_mutation
    #
    #     order = f.FinanceOrderFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceOrderNode', order.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #
    #     data = executed.get('data')
    #
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['relationCompany'], variables['input']['relationCompany'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['relationCompanyRegistration'], variables['input']['relationCompanyRegistration'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['relationContactName'], variables['input']['relationContactName'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['relationAddress'], variables['input']['relationAddress'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['relationPostcode'], variables['input']['relationPostcode'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['relationCity'], variables['input']['relationCity'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['relationCountry'], variables['input']['relationCountry'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['orderNumber'], variables['input']['orderNumber'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['dateSent'], variables['input']['dateSent'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['dateDue'], variables['input']['dateDue'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['status'], variables['input']['status'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['summary'], variables['input']['summary'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['terms'], variables['input']['terms'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['footer'], variables['input']['footer'])
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['note'], variables['input']['note'])
    #
    #
    # def test_update_order_anon_user(self):
    #     """ Don't allow updating orders for non-logged in users """
    #     query = self.order_update_mutation
    #     order = f.FinanceOrderFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceOrderNode', order.id)
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
    #     variables['input']['id'] = to_global_id('FinanceOrderNode', order.id)
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
    #     self.assertEqual(data['updateFinanceOrder']['financeOrder']['dateSent'], variables['input']['dateSent'])
    #
    #
    # def test_update_order_permission_denied(self):
    #     """ Check update order permission denied error message """
    #     query = self.order_update_mutation
    #     order = f.FinanceOrderFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('FinanceOrderNode', order.id)
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

    def test_delete_order(self):
        """ Delete an finance order """
        query = self.order_delete_mutation
        order = f.FinanceOrderFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('FinanceOrderNode', order.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceOrder']['ok'], True)

    def test_delete_order_anon_user(self):
        """ Delete order denied for anon user """
        query = self.order_delete_mutation
        order = f.FinanceOrderFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('FinanceOrderNode', order.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_order_permission_granted(self):
        """ Allow deleting orders for users with permissions """
        query = self.order_delete_mutation
        order = f.FinanceOrderFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('FinanceOrderNode', order.id)

        # Give permissions
        user = order.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteFinanceOrder']['ok'], True)

    def test_delete_order_permission_denied(self):
        """ Check delete order permission denied error message """
        query = self.order_delete_mutation
        order = f.FinanceOrderFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('FinanceOrderNode', order.id)

        user = order.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
