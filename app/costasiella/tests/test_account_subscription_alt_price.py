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


class GQLAccountSubscriptionAltPrice(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountsubscriptionaltprice'
        self.permission_add = 'add_accountsubscriptionaltprice'
        self.permission_change = 'change_accountsubscriptionaltprice'
        self.permission_delete = 'delete_accountsubscriptionaltprice'

        self.variables_create = {
            "input": {
                "subscriptionYear": 2019,
                "subscriptionMonth": 1,
                "amount": "1",
                "description": "Test description",
                "note": "Test note"
            }
        }

        self.variables_update = {
            "input": {
                "subscriptionYear": 2019,
                "subscriptionMonth": 1,
                "amount": "1",
                "description": "Test description",
                "note": "Test note"
            }
        }

        self.subscription_alt_prices_query = '''
    query AccountSubscriptionAltPrices($before:String, $after:String, $accountSubscription: ID!) {
      accountSubscriptionAltPrices(before: $before, after: $after, accountSubscription:$accountSubscription) {
        pageInfo {
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
        }
        edges {
          node {
            id
            accountSubscription {
              id
            }
            subscriptionYear
            subscriptionMonth
            amount
            amountDisplay
            description
            note
            createdAt
            updatedAt
          }
        }
      }
    }
'''

        self.subscription_alt_price_query = '''
    query AccountSubscriptionAltPrice($id: ID!) {
      accountSubscriptionAltPrice(id:$id) {
        id
        accountSubscription {
          id
        }
        subscriptionYear
        subscriptionMonth
        amount
        description
        note
      }
    }
'''

        self.subscription_alt_price_create_mutation = ''' 
  mutation CreateAccountSubscriptionAltPrice($input:CreateAccountSubscriptionAltPriceInput!) {
    createAccountSubscriptionAltPrice(input: $input) {
      accountSubscriptionAltPrice {
        id
        accountSubscription {
          id 
        }
        subscriptionYear
        subscriptionMonth
        amount
        description
        note
      }
    }
  }
'''

        self.subscription_alt_price_update_mutation = '''
  mutation UpdateAccountSubscriptionAltPrice($input:UpdateAccountSubscriptionAltPriceInput!) {
    updateAccountSubscriptionAltPrice(input: $input) {
      accountSubscriptionAltPrice {
        id
        accountSubscription {
          id 
        }
        subscriptionYear
        subscriptionMonth
        amount
        description
        note
      }
    }
  }
'''

        self.subscription_alt_price_delete_mutation = '''
  mutation DeleteAccountSubscriptionAltPrice($input: DeleteAccountSubscriptionAltPriceInput!) {
    deleteAccountSubscriptionAltPrice(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account subscriptions """
        query = self.subscription_alt_prices_query
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode',
                                                subscription_alt_price.account_subscription.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionAltPrices']['edges'][0]['node']['accountSubscription']['id'],
            to_global_id("AccountSubscriptionNode", subscription_alt_price.account_subscription.id)
        )
        self.assertEqual(data['accountSubscriptionAltPrices']['edges'][0]['node']['subscriptionYear'],
                         subscription_alt_price.subscription_year)
        self.assertEqual(data['accountSubscriptionAltPrices']['edges'][0]['node']['subscriptionMonth'],
                         subscription_alt_price.subscription_month)
        self.assertEqual(data['accountSubscriptionAltPrices']['edges'][0]['node']['amount'],
                         format(subscription_alt_price.amount, ".2f"))
        self.assertEqual(data['accountSubscriptionAltPrices']['edges'][0]['node']['description'],
                         subscription_alt_price.description)
        self.assertEqual(data['accountSubscriptionAltPrices']['edges'][0]['node']['note'],
                         subscription_alt_price.note)

    def test_query_permission_denied(self):
        """ Query list of account subscriptions - check permission denied """
        query = self.subscription_alt_prices_query
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode',
                                                subscription_alt_price.account_subscription.id)
        }

        # Create regular user
        user_id = subscription_alt_price.account_subscription.account.id
        user = get_user_model().objects.get(pk=user_id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of account subscription alt prices with view permission """
        query = self.subscription_alt_prices_query
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode',
                                                subscription_alt_price.account_subscription.id)
        }

        # Create regular user
        user_id = subscription_alt_price.account_subscription.account.id
        user = get_user_model().objects.get(pk=user_id)
        permission = Permission.objects.get(codename='view_accountsubscriptionaltprice')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all subscription alt_price mutations
        self.assertEqual(
            data['accountSubscriptionAltPrices']['edges'][0]['node']['accountSubscription']['id'],
            to_global_id("AccountSubscriptionNode", subscription_alt_price.account_subscription.id)
        )

    def test_query_anon_user(self):
        """ Query list of account subscription alt prices - anon user """
        query = self.subscription_alt_prices_query
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode',
                                                subscription_alt_price.account_subscription.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account subscription alt_price as admin """
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()
        variables = {
            "id": to_global_id("AccountSubscriptionAltPriceNode", subscription_alt_price.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_alt_price_query,
                                                 self.admin_user,
                                                 variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionAltPrice']['id'],
            to_global_id('AccountSubscriptionAltPriceNode', subscription_alt_price.id)
        )
        self.assertEqual(data['accountSubscriptionAltPrice']['subscriptionYear'],
                         subscription_alt_price.subscription_year)
        self.assertEqual(data['accountSubscriptionAltPrice']['subscriptionMonth'],
                         subscription_alt_price.subscription_month)
        self.assertEqual(data['accountSubscriptionAltPrice']['amount'],
                         format(subscription_alt_price.amount, ".2f"))
        self.assertEqual(data['accountSubscriptionAltPrice']['description'],
                         subscription_alt_price.description)
        self.assertEqual(data['accountSubscriptionAltPrice']['note'],
                         subscription_alt_price.note)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account subscription """
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()
        variables = {
            "id": to_global_id("AccountSubscriptionAltPriceNode", subscription_alt_price.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_alt_price_query,
                                                 self.anon_user,
                                                 variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()
        user = subscription_alt_price.account_subscription.account
        variables = {
            "id": to_global_id("AccountSubscriptionAltPriceNode", subscription_alt_price.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_alt_price_query,
                                                 user,
                                                 variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()
        user = subscription_alt_price.account_subscription.account
        permission = Permission.objects.get(codename='view_accountsubscriptionaltprice')
        user.user_permissions.add(permission)
        user.save()

        variables = {
            "id": to_global_id("AccountSubscriptionAltPriceNode", subscription_alt_price.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_alt_price_query,
                                                 user,
                                                 variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionAltPrice']['id'],
            to_global_id('AccountSubscriptionAltPriceNode', subscription_alt_price.id)
        )

    def test_create_subscription_alt_price(self):
        """ Create an account subscription alt_price """
        query = self.subscription_alt_price_create_mutation

        account_subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', account_subscription.id
        )

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountSubscriptionAltPrice']['accountSubscriptionAltPrice']['accountSubscription']['id'],
            variables['input']['accountSubscription']
        )
        self.assertEqual(
            data['createAccountSubscriptionAltPrice']['accountSubscriptionAltPrice']['subscriptionYear'],
            variables['input']['subscriptionYear']
        )
        self.assertEqual(
            data['createAccountSubscriptionAltPrice']['accountSubscriptionAltPrice']['subscriptionMonth'],
            variables['input']['subscriptionMonth']
        )
        self.assertEqual(
            data['createAccountSubscriptionAltPrice']['accountSubscriptionAltPrice']['note'],
            variables['input']['note']
        )
        self.assertEqual(
            data['createAccountSubscriptionAltPrice']['accountSubscriptionAltPrice']['description'],
            variables['input']['description']
        )

    def test_create_subscription_alt_price_permission_denied(self):
        """ Check create subscription permission denied error message """
        query = self.subscription_alt_price_create_mutation

        account_subscription = f.AccountSubscriptionFactory.create()
        account = account_subscription.account
        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', account_subscription.id
        )

        executed = execute_test_client_api_query(
            query,
            account,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_create_subscription_alt_price_permission_granted(self):
        """ Allow creating subscription alt_prices for users with permissions """
        query = self.subscription_alt_price_create_mutation

        account_subscription = f.AccountSubscriptionFactory.create()
        account = account_subscription.account
        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', account_subscription.id
        )

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
            data['createAccountSubscriptionAltPrice']['accountSubscriptionAltPrice']['accountSubscription']['id'],
            variables['input']['accountSubscription']
        )

    def test_create_subscription_alt_price_anon_user(self):
        """ Don't allow creating account subscription alt_price for non-logged in users """
        query = self.subscription_alt_price_create_mutation

        account_subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', account_subscription.id
        )

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_subscription_alt_price(self):
        """ Update a subscription alt_price """
        query = self.subscription_alt_price_update_mutation
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionAltPriceNode', subscription_alt_price.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['updateAccountSubscriptionAltPrice']['accountSubscriptionAltPrice']['accountSubscription']['id'],
            to_global_id('AccountSubscriptionNode', subscription_alt_price.account_subscription.id)
        )
        self.assertEqual(
            data['updateAccountSubscriptionAltPrice']['accountSubscriptionAltPrice']['subscriptionYear'],
            variables['input']['subscriptionYear']
        )
        self.assertEqual(
            data['updateAccountSubscriptionAltPrice']['accountSubscriptionAltPrice']['subscriptionMonth'],
            variables['input']['subscriptionMonth']
        )
        self.assertEqual(
            data['updateAccountSubscriptionAltPrice']['accountSubscriptionAltPrice']['note'],
            variables['input']['note']
        )
        self.assertEqual(
            data['updateAccountSubscriptionAltPrice']['accountSubscriptionAltPrice']['description'],
            variables['input']['description']
        )

    def test_update_subscription_alt_price_anon_user(self):
        """ Don't allow updating subscription alt_prices for non-logged in users """
        query = self.subscription_alt_price_update_mutation
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionAltPriceNode', subscription_alt_price.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_subscription_alt_price_permission_granted(self):
        """ Allow updating subscriptions for users with permissions """
        query = self.subscription_alt_price_update_mutation
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionAltPriceNode', subscription_alt_price.id)

        user = subscription_alt_price.account_subscription.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
          data['updateAccountSubscriptionAltPrice']['accountSubscriptionAltPrice']['accountSubscription']['id'],
          to_global_id('AccountSubscriptionNode', subscription_alt_price.account_subscription.id)
        )

    def test_update_subscription_alt_price_permission_denied(self):
        """ Check update subscription permission denied error message """
        query = self.subscription_alt_price_update_mutation
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionAltPriceNode', subscription_alt_price.id)

        user = subscription_alt_price.account_subscription.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_subscription_alt_price(self):
        """ Delete an account subscription alt_price"""
        query = self.subscription_alt_price_delete_mutation
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionAltPriceNode', subscription_alt_price.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        # print(data)
        self.assertEqual(data['deleteAccountSubscriptionAltPrice']['ok'], True)

    def test_delete_subscription_alt_price_anon_user(self):
        """ Delete subscription alt_price denied for anon user """
        query = self.subscription_alt_price_delete_mutation
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionAltPriceNode', subscription_alt_price.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_subscription_alt_price_permission_granted(self):
        """ Allow deleting subscription alt_prices for users with permissions """
        query = self.subscription_alt_price_delete_mutation
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionAltPriceNode', subscription_alt_price.id)

        # Give permissions
        user = subscription_alt_price.account_subscription.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountSubscriptionAltPrice']['ok'], True)

    def test_delete_subscription_alt_price_permission_denied(self):
        """ Check delete subscription alt_price permission denied error message """
        query = self.subscription_alt_price_delete_mutation
        subscription_alt_price = f.AccountSubscriptionAltPriceFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionAltPriceNode', subscription_alt_price.id)

        user = subscription_alt_price.account_subscription.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
