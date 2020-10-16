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


class GQLAccountSubscriptionBlock(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountsubscriptionblock'
        self.permission_add = 'add_accountsubscriptionblock'
        self.permission_change = 'change_accountsubscriptionblock'
        self.permission_delete = 'delete_accountsubscriptionblock'

        self.variables_create = {
            "input": {
                "dateStart": "2019-01-01",
                "dateEnd": "2019-01-31",
                "description": "Test description"
            }
        }

        self.variables_update = {
            "input": {
                "dateStart": "2019-01-01",
                "dateEnd": "2019-01-31",
                "description": "Test description"
            }
        }

        self.subscription_blocks_query = '''
    query AccountSubscriptionBlocks($before: String, $after: String, $accountSubscription: ID!) {
      accountSubscriptionBlocks(first: 20, before: $before, after: $after, accountSubscription: $accountSubscription) {
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
            dateStart
            dateEnd
            description
            createdAt
          }
        } 
      }
    }
'''

        self.subscription_block_query = '''
    query AccountSubscriptionBlock($id: ID!) {
      accountSubscriptionBlock(id:$id) {
        id
        accountSubscription {
          id
        }
        dateStart
        dateEnd
        description
      }
    }
'''

        self.subscription_block_create_mutation = ''' 
  mutation CreateAccountSubscriptionBlock($input:CreateAccountSubscriptionBlockInput!) {
    createAccountSubscriptionBlock(input: $input) {
      accountSubscriptionBlock {
        id
        accountSubscription {
          id
        }
        dateStart
        dateEnd
        description
      }
    }
  }
'''

        self.subscription_block_update_mutation = '''
  mutation UpdateAccountSubscriptionBlock($input:UpdateAccountSubscriptionBlockInput!) {
    updateAccountSubscriptionBlock(input: $input) {
      accountSubscriptionBlock {
        id
        accountSubscription {
          id
        }
        dateStart
        dateEnd
        description
      }
    }
  }
'''

        self.subscription_block_delete_mutation = '''
  mutation DeleteAccountSubscriptionBlock($input: DeleteAccountSubscriptionBlockInput!) {
    deleteAccountSubscriptionBlock(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account subscriptions """
        query = self.subscription_blocks_query
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode', subscription_block.account_subscription.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionBlocks']['edges'][0]['node']['accountSubscription']['id'],
            to_global_id("AccountSubscriptionNode", subscription_block.account_subscription.id)
        )
        self.assertEqual(data['accountSubscriptionBlocks']['edges'][0]['node']['dateStart'],
                         subscription_block.date_start)
        self.assertEqual(data['accountSubscriptionBlocks']['edges'][0]['node']['dateEnd'],
                         subscription_block.date_end)
        self.assertEqual(data['accountSubscriptionBlocks']['edges'][0]['node']['description'],
                         subscription_block.description)

    def test_query_permission_denied(self):
        """ Query list of account subscriptions - check permission denied """
        query = self.subscription_blocks_query
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode', subscription_block.account_subscription.id)
        }

        # Create regular user
        user_id = subscription_block.account_subscription.account.id
        user = get_user_model().objects.get(pk=user_id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of account subscriptions with view permission """
        query = self.subscription_blocks_query
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode', subscription_block.account_subscription.id)
        }

        # Create regular user
        user_id = subscription_block.account_subscription.account.id
        user = get_user_model().objects.get(pk=user_id)
        permission = Permission.objects.get(codename='view_accountsubscriptionblock')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all subscription block mutations
        self.assertEqual(
            data['accountSubscriptionBlocks']['edges'][0]['node']['accountSubscription']['id'],
            to_global_id("AccountSubscriptionNode", subscription_block.account_subscription.id)
        )

    def test_query_anon_user(self):
        """ Query list of account subscriptions - anon user """
        query = self.subscription_blocks_query
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode', subscription_block.account_subscription.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account subscription block as admin """
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        variables = {
            "id": to_global_id("AccountSubscriptionBlockNode", subscription_block.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_block_query,
                                                 self.admin_user,
                                                 variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionBlock']['id'],
            to_global_id('AccountSubscriptionBlockNode', subscription_block.id)
        )
        self.assertEqual(data['accountSubscriptionBlock']['dateStart'],
                         subscription_block.date_start)
        self.assertEqual(data['accountSubscriptionBlock']['dateEnd'],
                         subscription_block.date_end)
        self.assertEqual(data['accountSubscriptionBlock']['description'],
                         subscription_block.description)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account subscription """
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        variables = {
            "id": to_global_id("AccountSubscriptionBlockNode", subscription_block.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_block_query,
                                                 self.anon_user,
                                                 variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        user = subscription_block.account_subscription.account
        variables = {
            "id": to_global_id("AccountSubscriptionBlockNode", subscription_block.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_block_query,
                                                 user,
                                                 variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        user = subscription_block.account_subscription.account
        permission = Permission.objects.get(codename='view_accountsubscriptionblock')
        user.user_permissions.add(permission)
        user.save()

        variables = {
            "id": to_global_id("AccountSubscriptionBlockNode", subscription_block.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_block_query,
                                                 user,
                                                 variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionBlock']['id'],
            to_global_id('AccountSubscriptionBlockNode', subscription_block.id)
        )

    def test_create_subscription_block(self):
        """ Create an account subscription block """
        query = self.subscription_block_create_mutation

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
            data['createAccountSubscriptionBlock']['accountSubscriptionBlock']['accountSubscription']['id'],
            variables['input']['accountSubscription']
        )
        self.assertEqual(
            data['createAccountSubscriptionBlock']['accountSubscriptionBlock']['dateStart'],
            variables['input']['dateStart']
        )
        self.assertEqual(
            data['createAccountSubscriptionBlock']['accountSubscriptionBlock']['dateEnd'],
            variables['input']['dateEnd']
        )
        self.assertEqual(
            data['createAccountSubscriptionBlock']['accountSubscriptionBlock']['description'],
            variables['input']['description']
        )

    def test_create_subscription_anon_user(self):
        """ Don't allow creating account subscription block for non-logged in users """
        query = self.subscription_block_create_mutation

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

    def test_create_subscription_block_permission_granted(self):
        """ Allow creating subscription blocks for users with permissions """
        query = self.subscription_block_create_mutation

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
            data['createAccountSubscriptionBlock']['accountSubscriptionBlock']['accountSubscription']['id'],
            variables['input']['accountSubscription']
        )

    def test_create_subscription_block_permission_denied(self):
        """ Check create subscription permission denied error message """
        query = self.subscription_block_create_mutation

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

    def test_update_subscription_block(self):
        """ Update a subscription block """
        query = self.subscription_block_update_mutation
        subscription_block = f.AccountSubscriptionBlockFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionBlockNode', subscription_block.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['updateAccountSubscriptionBlock']['accountSubscriptionBlock']['accountSubscription']['id'],
            to_global_id('AccountSubscriptionNode', subscription_block.account_subscription.id)
        )
        self.assertEqual(
            data['updateAccountSubscriptionBlock']['accountSubscriptionBlock']['dateStart'],
            variables['input']['dateStart']
        )
        self.assertEqual(
            data['updateAccountSubscriptionBlock']['accountSubscriptionBlock']['dateEnd'],
            variables['input']['dateEnd']
        )
        self.assertEqual(
            data['updateAccountSubscriptionBlock']['accountSubscriptionBlock']['description'],
            variables['input']['description']
        )

    def test_update_subscription_block_anon_user(self):
        """ Don't allow updating subscription blocks for non-logged in users """
        query = self.subscription_block_update_mutation
        subscription_block = f.AccountSubscriptionBlockFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionBlockNode', subscription_block.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_subscription_block_permission_granted(self):
        """ Allow updating subscriptions for users with permissions """
        query = self.subscription_block_update_mutation
        subscription_block = f.AccountSubscriptionBlockFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionBlockNode', subscription_block.id)

        user = subscription_block.account_subscription.account
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
          data['updateAccountSubscriptionBlock']['accountSubscriptionBlock']['accountSubscription']['id'],
          to_global_id('AccountSubscriptionNode', subscription_block.account_subscription.id)
        )

    def test_update_subscription_block_permission_denied(self):
        """ Check update subscription permission denied error message """
        query = self.subscription_block_update_mutation
        subscription_block = f.AccountSubscriptionBlockFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionBlockNode', subscription_block.id)

        user = subscription_block.account_subscription.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_subscription_block(self):
        """ Delete an account subscription block"""
        query = self.subscription_block_delete_mutation
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionBlockNode', subscription_block.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        # print(data)
        self.assertEqual(data['deleteAccountSubscriptionBlock']['ok'], True)

    def test_delete_subscription_block_anon_user(self):
        """ Delete subscription block denied for anon user """
        query = self.subscription_block_delete_mutation
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionBlockNode', subscription_block.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_subscription_block_permission_granted(self):
        """ Allow deleting subscription blocks for users with permissions """
        query = self.subscription_block_delete_mutation
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionBlockNode', subscription_block.id)

        # Give permissions
        user = subscription_block.account_subscription.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountSubscriptionBlock']['ok'], True)

    def test_delete_subscription_block_permission_denied(self):
        """ Check delete subscription block permission denied error message """
        query = self.subscription_block_delete_mutation
        subscription_block = f.AccountSubscriptionBlockFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionBlockNode', subscription_block.id)

        user = subscription_block.account_subscription.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
