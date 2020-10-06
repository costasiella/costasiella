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


class GQLAccountSubscriptionCredit(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountsubscriptioncredit'
        self.permission_add = 'add_accountsubscriptioncredit'
        self.permission_change = 'change_accountsubscriptioncredit'
        self.permission_delete = 'delete_accountsubscriptioncredit'

        self.variables_create = {
            "input": {
                "mutationType": "ADD",
                "mutationAmount": 1
            }
        }

        self.variables_update = {
            "input": {
                "mutationType": "SUB",
                "mutationAmount": 2
            }
        }

        self.subscription_credits_query = '''
    query AccountSubscriptionCredits($before: String, $after: String, $accountSubscription: ID!) {
      accountSubscriptionCredits(first: 20, before: $before, after: $after, accountSubscription: $accountSubscription) {
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
            mutationType
            mutationAmount
            description
            createdAt
          }
        } 
      }
    }
'''

        self.subscription_credit_query = '''
     query AccountSubscriptionCredit($id: ID!) {
      accountSubscriptionCredit(id:$id) {
        id
        accountSubscription {
          id
        }
        mutationType
        mutationAmount
        description
        createdAt
      }
    }
'''

        self.subscription_credit_create_mutation = ''' 
  mutation CreateAccountSubscriptionCredit($input:CreateAccountSubscriptionCreditInput!) {
    createAccountSubscriptionCredit(input: $input) {
      accountSubscriptionCredit {
        id
        accountSubscription {
          id
        }
        mutationType
        mutationAmount
        description
        createdAt
      }
    }
  }
'''

        self.subscription_credit_update_mutation = '''
  mutation UpdateAccountSubscriptionCredit($input:UpdateAccountSubscriptionCreditInput!) {
    updateAccountSubscriptionCredit(input: $input) {
      accountSubscriptionCredit {
        id
        accountSubscription {
          id
        }
        mutationType
        mutationAmount
        description
        createdAt
      }
    }
  }
'''

        self.subscription_credit_delete_mutation = '''
  mutation DeleteAccountSubscriptionCredit($input: DeleteAccountSubscriptionCreditInput!) {
    deleteAccountSubscriptionCredit(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account subscriptions """
        query = self.subscription_credits_query
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode', subscription_credit.account_subscription.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionCredits']['edges'][0]['node']['accountSubscription']['id'],
            to_global_id("AccountSubscriptionNode", subscription_credit.account_subscription.id)
        )
        self.assertEqual(data['accountSubscriptionCredits']['edges'][0]['node']['mutationType'],
                         subscription_credit.mutation_type)
        self.assertEqual(data['accountSubscriptionCredits']['edges'][0]['node']['mutationAmount'],
                         subscription_credit.mutation_amount)
        self.assertEqual(data['accountSubscriptionCredits']['edges'][0]['node']['description'],
                         subscription_credit.description)

    def test_query_permission_denied(self):
        """ Query list of account subscriptions - check permission denied """
        query = self.subscription_credits_query
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode', subscription_credit.account_subscription.id)
        }

        # Create regular user
        user_id = subscription_credit.account_subscription.account.id
        user = get_user_model().objects.get(pk=user_id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of account subscriptions with view permission """
        query = self.subscription_credits_query
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode', subscription_credit.account_subscription.id)
        }

        # Create regular user
        user_id = subscription_credit.account_subscription.account.id
        user = get_user_model().objects.get(pk=user_id)
        permission = Permission.objects.get(codename='view_accountsubscriptioncredit')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all subscription credit mutations
        self.assertEqual(
            data['accountSubscriptionCredits']['edges'][0]['node']['accountSubscription']['id'],
            to_global_id("AccountSubscriptionNode", subscription_credit.account_subscription.id)
        )

    def test_query_anon_user(self):
        """ Query list of account subscriptions - anon user """
        query = self.subscription_credits_query
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode', subscription_credit.account_subscription.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account subscription credit as admin """
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        variables = {
            "id": to_global_id("AccountSubscriptionCreditNode", subscription_credit.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_credit_query,
                                                 self.admin_user,
                                                 variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionCredit']['id'],
            to_global_id('AccountSubscriptionCreditNode', subscription_credit.id)
        )
        self.assertEqual(data['accountSubscriptionCredit']['mutationType'],
                         subscription_credit.mutation_type)
        self.assertEqual(data['accountSubscriptionCredit']['mutationAmount'],
                         subscription_credit.mutation_amount)
        self.assertEqual(data['accountSubscriptionCredit']['description'],
                         subscription_credit.description)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account subscription """
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        variables = {
            "id": to_global_id("AccountSubscriptionCreditNode", subscription_credit.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_credit_query,
                                                 self.anon_user,
                                                 variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        user = subscription_credit.account_subscription.account
        variables = {
            "id": to_global_id("AccountSubscriptionCreditNode", subscription_credit.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_credit_query,
                                                 user,
                                                 variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        user = subscription_credit.account_subscription.account
        permission = Permission.objects.get(codename='view_accountsubscriptioncredit')
        user.user_permissions.add(permission)
        user.save()

        variables = {
            "id": to_global_id("AccountSubscriptionCreditNode", subscription_credit.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_credit_query,
                                                 user,
                                                 variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionCredit']['id'],
            to_global_id('AccountSubscriptionCreditNode', subscription_credit.id)
        )

    def test_create_subscription_credit(self):
        """ Create an account subscription credit """
        query = self.subscription_credit_create_mutation

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
            data['createAccountSubscriptionCredit']['accountSubscriptionCredit']['accountSubscription']['id'],
            variables['input']['accountSubscription']
        )
        self.assertEqual(
            data['createAccountSubscriptionCredit']['accountSubscriptionCredit']['mutationType'],
            variables['input']['mutationType']
        )
        self.assertEqual(
            data['createAccountSubscriptionCredit']['accountSubscriptionCredit']['mutationAmount'],
            variables['input']['mutationAmount']
        )

    def test_create_subscription_anon_user(self):
        """ Don't allow creating account subscription credit for non-logged in users """
        query = self.subscription_credit_create_mutation

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

    def test_create_subscription_credit_permission_granted(self):
        """ Allow creating subscription credits for users with permissions """
        query = self.subscription_credit_create_mutation

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
            data['createAccountSubscriptionCredit']['accountSubscriptionCredit']['accountSubscription']['id'],
            variables['input']['accountSubscription']
        )

    def test_create_subscription_credit_permission_denied(self):
        """ Check create subscription permission denied error message """
        query = self.subscription_credit_create_mutation

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

    def test_update_subscription_credit(self):
        """ Update a subscription credit """
        query = self.subscription_credit_update_mutation
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', subscription_credit.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateAccountSubscriptionCredit']['accountSubscriptionCredit']['accountSubscription']['id'],
          to_global_id('AccountSubscriptionNode', subscription_credit.account_subscription.id)
        )
        self.assertEqual(
          data['updateAccountSubscriptionCredit']['accountSubscriptionCredit']['mutationType'],
          variables['input']['mutationType']
        )
        self.assertEqual(
          data['updateAccountSubscriptionCredit']['accountSubscriptionCredit']['mutationAmount'],
          variables['input']['mutationAmount']
        )

    def test_update_subscription_credit_anon_user(self):
        """ Don't allow updating subscription credits for non-logged in users """
        query = self.subscription_credit_update_mutation
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', subscription_credit.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_subscription_credit_permission_granted(self):
        """ Allow updating subscriptions for users with permissions """
        query = self.subscription_credit_update_mutation
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', subscription_credit.id)

        user = subscription_credit.account_subscription.account
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
          data['updateAccountSubscriptionCredit']['accountSubscriptionCredit']['accountSubscription']['id'],
          to_global_id('AccountSubscriptionNode', subscription_credit.account_subscription.id)
        )

    def test_update_subscription_credit_permission_denied(self):
        """ Check update subscription permission denied error message """
        query = self.subscription_credit_update_mutation
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', subscription_credit.id)

        user = subscription_credit.account_subscription.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_subscription_credit(self):
        """ Delete an account subscription credit"""
        query = self.subscription_credit_delete_mutation
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', subscription_credit.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        # print(data)
        self.assertEqual(data['deleteAccountSubscriptionCredit']['ok'], True)

    def test_delete_subscription_credit_anon_user(self):
        """ Delete subscription credit denied for anon user """
        query = self.subscription_credit_delete_mutation
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', subscription_credit.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_subscription_credit_permission_granted(self):
        """ Allow deleting subscription credits for users with permissions """
        query = self.subscription_credit_delete_mutation
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', subscription_credit.id)

        # Give permissions
        user = subscription_credit.account_subscription.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountSubscriptionCredit']['ok'], True)

    def test_delete_subscription_credit_permission_denied(self):
        """ Check delete subscription credit permission denied error message """
        query = self.subscription_credit_delete_mutation
        subscription_credit = f.AccountSubscriptionCreditAddFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', subscription_credit.id)

        user = subscription_credit.account_subscription.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

