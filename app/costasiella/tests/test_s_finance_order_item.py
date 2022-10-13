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


class GQLFinanceOrderItem(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['app_settings.json', 'system_mail_template.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financeorderitem'
        self.permission_add = 'add_financeorderitem'
        self.permission_change = 'change_financeorderitem'
        self.permission_delete = 'delete_financeorderitem'

        self.finance_tax_rate = f.FinanceTaxRateFactory.create()
        self.finance_glaccount = f.FinanceGLAccountFactory.create()
        self.finance_costcenter = f.FinanceCostCenterFactory.create()

        self.order_items_query = '''
    query FinanceOrderItems($financeOrder: ID!) {
      financeOrderItems(financeOrder: $financeOrder) {
        pageInfo {
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
        }
        edges {
          node {
            id
            financeOrder {
              id
            }
            organizationClasspass {
              id
            }
            productName
            description
            quantity
            price
            subtotal
            tax
            total
            financeTaxRate {
              id
            }
            financeGlaccount {
              id
            }
            financeCostcenter {
              id
            }
          }
        }
      }
    }
'''

        self.order_item_query = '''
  query FinanceOrderItem($id: ID!) {
    financeOrderItem(id:$id) {
      id
      financeOrder {
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

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account order items """
        query = self.order_items_query
        order_item = f.FinanceOrderItemClasspassFactory.create()

        variables = {
          "financeOrder": to_global_id('FinanceOrderItemNode', order_item.finance_order.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['financeOrderItems']['edges'][0]['node']['id'],
          to_global_id('FinanceOrderItemNode', order_item.id)
        )
        self.assertEqual(
          data['financeOrderItems']['edges'][0]['node']['financeOrder']['id'],
          to_global_id('FinanceOrderNode', order_item.finance_order.id)
        )
        self.assertEqual(data['financeOrderItems']['edges'][0]['node']['productName'], order_item.product_name)
        self.assertEqual(data['financeOrderItems']['edges'][0]['node']['description'], order_item.description)
        self.assertEqual(data['financeOrderItems']['edges'][0]['node']['quantity'],
                         format(order_item.quantity, ".2f"))
        self.assertEqual(data['financeOrderItems']['edges'][0]['node']['price'],
                         format(order_item.price, ".2f"))
        self.assertEqual(data['financeOrderItems']['edges'][0]['node']['financeTaxRate']['id'],
                         to_global_id('FinanceTaxRateNode', order_item.finance_tax_rate.id))
        self.assertEqual(data['financeOrderItems']['edges'][0]['node']['subtotal'],
                         format(order_item.subtotal, ".2f"))
        self.assertEqual(data['financeOrderItems']['edges'][0]['node']['tax'],
                         format(order_item.tax, ".2f"))
        self.assertEqual(data['financeOrderItems']['edges'][0]['node']['total'],
                         format(order_item.total, ".2f"))
        self.assertEqual(data['financeOrderItems']['edges'][0]['node']['financeGlaccount']['id'],
                         to_global_id('FinanceGLAccountNode', order_item.finance_glaccount.id))
        self.assertEqual(data['financeOrderItems']['edges'][0]['node']['financeCostcenter']['id'],
                         to_global_id('FinanceCostCenterNode', order_item.finance_costcenter.id))

    def test_query_permission_denied(self):
        """ Query list of account order items - check permission denied """
        query = self.order_items_query
        order_item = f.FinanceOrderItemClasspassFactory.create()

        variables = {
            "financeOrder": to_global_id('FinanceOrderItemNode', order_item.finance_order.pk)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=order_item.finance_order.account.id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of account order items with view permission """
        query = self.order_items_query
        order_item = f.FinanceOrderItemClasspassFactory.create()

        variables = {
            "financeOrder": to_global_id('FinanceOrderItemNode', order_item.finance_order.pk)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=order_item.finance_order.account.id)
        permission = Permission.objects.get(codename='view_financeorderitem')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List selected order items
        self.assertEqual(
            data['financeOrderItems']['edges'][0]['node']['id'],
            to_global_id('FinanceOrderItemNode', order_item.id)
        )

    def test_query_anon_user(self):
        """ Query list of account order items - anon user """
        query = self.order_items_query
        order_item = f.FinanceOrderItemClasspassFactory.create()

        variables = {
            "financeOrder": to_global_id('FinanceOrderItemNode', order_item.finance_order.pk)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # def test_query_one(self):
    #     """ Query one account order item as admin """   
    #     order_item = f.FinanceOrderItemClasspassFactory.create()
    #     
    #     variables = {
    #         "id": to_global_id("FinanceOrderItemNode", order_item.id),
    #     }
    # 
    #     # Now query single order and check
    #     executed = execute_test_client_api_query(self.order_item_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    # 
    #     self.assertEqual(
    #         data['financeOrderItem']['id'],
    #         to_global_id('FinanceOrderItemNode', order_item.id)
    #     )
    # 
    # 
    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one account order """   
    #     order_item = f.FinanceOrderItemClasspassFactory.create()
    #     
    #     variables = {
    #         "id": to_global_id("FinanceOrderItemNode", order_item.id),
    #     }
    # 
    #     # Now query single order and check
    #     executed = execute_test_client_api_query(self.order_item_query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # 
    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     order_item = f.FinanceOrderItemClasspassFactory.create()
    #     user = order_item.finance_order.account
    # 
    #     variables = {
    #         "id": to_global_id("FinanceOrderItemNode", order_item.id),
    #     }
    # 
    #     # Now query single order and check
    #     executed = execute_test_client_api_query(self.order_item_query, user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    # 
    # 
    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     order_item = f.FinanceOrderItemClasspassFactory.create()
    #     user = order_item.finance_order.account
    #     permission = Permission.objects.get(codename='view_financeorderitem')
    #     user.user_permissions.add(permission)
    #     user.save()
    #     
    #     variables = {
    #         "id": to_global_id("FinanceOrderItemNode", order_item.id),
    #     }
    # 
    #     # Now query single order and check   
    #     executed = execute_test_client_api_query(self.order_item_query, user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['financeOrderItem']['id'],
    #         to_global_id('FinanceOrderItemNode', order_item.id)
    #     )
