# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64
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

        self.account_subscription_credit = f.AccountSubscriptionCreditAttendanceFactory.create()
        self.account_subscription = self.account_subscription_credit.account_subscription

        self.variables_create = {
            "input": {
                "accountSubscription": to_global_id("AccountSubscriptionNode", self.account_subscription.id),
                "description": "test create"
            }
        }

        self.variables_create_multiple = {
            "input": {
                "accountSubscription": to_global_id("AccountSubscriptionNode", self.account_subscription.id),
                "description": "test create",
                "amount": 3,
            }
        }

        self.variables_update = {
            "input": {
                "expiration": "2999-01-01",
                "description": "Test update"
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
            scheduleItemAttendance {
              id
            }
            advance
            reconciled
            expiration
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
        scheduleItemAttendance {
          id
        }
        advance
        reconciled
        expiration
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
        advance
        reconciled
        expiration
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
        advance
        reconciled
        expiration
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
        """ Query list of account subscription credits """
        query = self.subscription_credits_query

        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode',
                                                self.account_subscription_credit.account_subscription.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionCredits']['edges'][0]['node']['accountSubscription']['id'],
            to_global_id("AccountSubscriptionNode", self.account_subscription_credit.account_subscription.id)
        )
        self.assertEqual(
            data['accountSubscriptionCredits']['edges'][0]['node']['scheduleItemAttendance']['id'],
            to_global_id("ScheduleItemAttendanceNode", self.account_subscription_credit.schedule_item_attendance.id)
        )
        self.assertEqual(
            data['accountSubscriptionCredits']['edges'][0]['node']['description'],
            self.account_subscription_credit.description
        )
        self.assertEqual(
            data['accountSubscriptionCredits']['edges'][0]['node']['expiration'],
            str(self.account_subscription_credit.expiration)
        )

    def test_query_anon_user(self):
        """ Query list of account subscription credits - anon user """
        query = self.subscription_credits_query
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode',
                                                self.account_subscription_credit.account_subscription.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_permission_granted(self):
        """ Query list of account subscriptions with view permission """
        query = self.subscription_credits_query
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode',
                                                self.account_subscription_credit.account_subscription.id)
        }

        # Create regular user
        user = self.account_subscription_credit.account_subscription.account
        permission = Permission.objects.get(codename='view_accountsubscriptioncredit')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all subscription credit mutations
        self.assertEqual(
            data['accountSubscriptionCredits']['edges'][0]['node']['accountSubscription']['id'],
            to_global_id("AccountSubscriptionNode", self.account_subscription_credit.account_subscription.id)
        )

    def test_query_permission_own(self):
        """ Query list of account subscription credits - check permission to view own credits """
        query = self.subscription_credits_query
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode',
                                                self.account_subscription_credit.account_subscription.id)
        }

        # Create regular user
        user_id = self.account_subscription_credit.account_subscription.account.id
        user = get_user_model().objects.get(pk=user_id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['accountSubscriptionCredits']['edges'][0]['node']['accountSubscription']['id'],
            to_global_id("AccountSubscriptionNode", self.account_subscription_credit.account_subscription.id)
        )

    def test_query_permission_denied(self):
        """ Query list of account subscription credits - check permission denied """
        query = self.subscription_credits_query
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode',
                                                self.account_subscription_credit.account_subscription.id)
        }

        # Create regular user
        user = f.InstructorFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one(self):
        """ Query one account subscription credit as admin """
        variables = {
            "id": to_global_id("AccountSubscriptionCreditNode", self.account_subscription_credit.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_credit_query,
                                                 self.admin_user,
                                                 variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionCredit']['id'],
            to_global_id('AccountSubscriptionCreditNode', self.account_subscription_credit.id)
        )
        self.assertEqual(
            data['accountSubscriptionCredit']['scheduleItemAttendance']['id'],
            to_global_id('ScheduleItemAttendanceNode', self.account_subscription_credit.schedule_item_attendance.id)
        )
        self.assertEqual(data['accountSubscriptionCredit']['expiration'],
                         str(self.account_subscription_credit.expiration))
        self.assertEqual(data['accountSubscriptionCredit']['description'],
                         self.account_subscription_credit.description)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account subscription """
        variables = {
            "id": to_global_id("AccountSubscriptionCreditNode", self.account_subscription_credit.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_credit_query,
                                                 self.anon_user,
                                                 variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_granted(self):
        """ Query account subscriptions with view permission """
        variables = {
            "id": to_global_id("AccountSubscriptionCreditNode", self.account_subscription_credit.id),
        }

        # Create regular user
        user = self.account_subscription_credit.account_subscription.account
        permission = Permission.objects.get(codename='view_accountsubscriptioncredit')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(self.subscription_credit_query, user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['accountSubscriptionCredit']['id'],
            to_global_id('AccountSubscriptionCreditNode', self.account_subscription_credit.id)
        )

    def test_query_one_permission_own(self):
        """ Permission granted for credits for own subscriptions """
        user = self.account_subscription_credit.account_subscription.account
        variables = {
            "id": to_global_id("AccountSubscriptionCreditNode", self.account_subscription_credit.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_credit_query,
                                                 user,
                                                 variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['accountSubscriptionCredit']['id'],
            to_global_id('AccountSubscriptionCreditNode', self.account_subscription_credit.id)
        )

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        user = f.InstructorFactory.create()
        variables = {
            "id": to_global_id("AccountSubscriptionCreditNode", self.account_subscription_credit.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_credit_query,
                                                 user,
                                                 variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_create_subscription_credit(self):
        """ Create an account subscription credit """
        query = self.subscription_credit_create_mutation

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_create
        )
        data = executed.get('data')

        today = timezone.now().date()
        self.assertEqual(
            data['createAccountSubscriptionCredit']['accountSubscriptionCredit']['accountSubscription']['id'],
            self.variables_create['input']['accountSubscription']
        )
        self.assertEqual(
            data['createAccountSubscriptionCredit']['accountSubscriptionCredit']['expiration'],
            str(today + datetime.timedelta(days=self.account_subscription.organization_subscription.credit_validity))
        )
        self.assertEqual(
            data['createAccountSubscriptionCredit']['accountSubscriptionCredit']['description'],
            self.variables_create['input']['description']
        )

    def test_create_subscription_credit_multiple(self):
        """ Create multiple account subscription credit """
        query = self.subscription_credit_create_mutation

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_create_multiple
        )
        data = executed.get('data')

        count = models.AccountSubscriptionCredit.objects.filter(
            account_subscription=self.account_subscription
        ).count()

        # input amount +1 == count because there is one credit created in setup
        self.assertEqual(
            self.variables_create_multiple['input']['amount'] + 1,
            count,
        )


    def test_create_subscription_anon_user(self):
        """ Don't allow creating account subscription credit for non-logged in users """
        query = self.subscription_credit_create_mutation

        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', self.account_subscription.id
        )

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_subscription_credit_permission_granted(self):
        """ Allow creating subscription credits for users with permissions """
        query = self.subscription_credit_create_mutation

        account = self.account_subscription.account
        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', self.account_subscription.id
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

        account = self.account_subscription.account
        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', self.account_subscription.id
        )

        executed = execute_test_client_api_query(
            query,
            account,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_subscription_credit(self):
        """ Update a subscription credit """
        query = self.subscription_credit_update_mutation

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', self.account_subscription_credit.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateAccountSubscriptionCredit']['accountSubscriptionCredit']['accountSubscription']['id'],
          to_global_id('AccountSubscriptionNode', self.account_subscription_credit.account_subscription.id)
        )
        self.assertEqual(
          data['updateAccountSubscriptionCredit']['accountSubscriptionCredit']['expiration'],
          variables['input']['expiration']
        )
        self.assertEqual(
          data['updateAccountSubscriptionCredit']['accountSubscriptionCredit']['description'],
          variables['input']['description']
        )

    def test_update_subscription_credit_anon_user(self):
        """ Don't allow updating subscription credits for non-logged in users """
        query = self.subscription_credit_update_mutation

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', self.account_subscription_credit.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_subscription_credit_permission_granted(self):
        """ Allow updating subscriptions for users with permissions """
        query = self.subscription_credit_update_mutation

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', self.account_subscription_credit.id)

        user = self.account_subscription_credit.account_subscription.account
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
          to_global_id('AccountSubscriptionNode', self.account_subscription_credit.account_subscription.id)
        )

    def test_update_subscription_credit_permission_denied(self):
        """ Check update subscription permission denied error message """
        query = self.subscription_credit_update_mutation

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', self.account_subscription_credit.id)

        user = self.account_subscription_credit.account_subscription.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_subscription_credit(self):
        """ Delete an account subscription credit"""
        query = self.subscription_credit_delete_mutation
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', self.account_subscription_credit.id)

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
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', self.account_subscription_credit.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_subscription_credit_permission_granted(self):
        """ Allow deleting subscription credits for users with permissions """
        query = self.subscription_credit_delete_mutation
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', self.account_subscription_credit.id)

        # Give permissions
        user = self.account_subscription_credit.account_subscription.account
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
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionCreditNode', self.account_subscription_credit.id)

        user = self.account_subscription_credit.account_subscription.account
        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
