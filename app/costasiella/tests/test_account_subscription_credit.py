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
                "dateStart": "2019-01-01",
                "dateEnd": "2019-12-31",
                "note": "creation note",
                "registrationFeePaid": True
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

        self.subscription_create_mutation = ''' 
  mutation CreateAccountSubscriptionCredit($input:CreateAccountSubscriptionCreditInput!) {
    createAccountSubscriptionCredit(input: $input) {
      accountSubscriptionCredit {
        id
      }
    }
  }
'''

        self.subscription_update_mutation = '''
  mutation UpdateAccountSubscriptionCredit($input:UpdateAccountSubscriptionCreditInput!) {
    updateAccountSubscriptionCredit(input: $input) {
      accountSubscriptionCredit {
        id
      }
    }
  }
'''

        self.subscription_delete_mutation = '''
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
    #
    #
    # def test_query_one(self):
    #     """ Query one account subscription as admin """
    #     subscription = f.AccountSubscriptionFactory.create()
    #
    #     variables = {
    #         "id": to_global_id("AccountSubscriptionNode", subscription.id),
    #         "accountId": to_global_id("AccountNode", subscription.account.id),
    #         "archived": False,
    #     }
    #
    #     # Now query single subscription and check
    #     executed = execute_test_client_api_query(self.subscription_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['accountSubscription']['account']['id'],
    #         to_global_id('AccountNode', subscription.account.id)
    #     )
    #     self.assertEqual(
    #         data['accountSubscription']['organizationSubscription']['id'],
    #         to_global_id('OrganizationSubscriptionNode', subscription.organization_subscription.id)
    #     )
    #     self.assertEqual(
    #         data['accountSubscription']['financePaymentMethod']['id'],
    #         to_global_id('FinancePaymentMethodNode', subscription.finance_payment_method.id)
    #     )
    #     self.assertEqual(data['accountSubscription']['dateStart'], str(subscription.date_start))
    #     self.assertEqual(data['accountSubscription']['dateEnd'], subscription.date_end)
    #     self.assertEqual(data['accountSubscription']['note'], subscription.note)
    #     self.assertEqual(data['accountSubscription']['registrationFeePaid'], subscription.registration_fee_paid)
    #
    #
    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one account subscription """
    #     subscription = f.AccountSubscriptionFactory.create()
    #
    #     variables = {
    #         "id": to_global_id("AccountSubscriptionNode", subscription.id),
    #         "accountId": to_global_id("AccountNode", subscription.account.id),
    #         "archived": False,
    #     }
    #
    #     # Now query single subscription and check
    #     executed = execute_test_client_api_query(self.subscription_query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    #
    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """
    #     # Create regular user
    #     subscription = f.AccountSubscriptionFactory.create()
    #     user = subscription.account
    #
    #     variables = {
    #         "id": to_global_id("AccountSubscriptionNode", subscription.id),
    #         "accountId": to_global_id("AccountNode", subscription.account.id),
    #         "archived": False,
    #     }
    #
    #     # Now query single subscription and check
    #     executed = execute_test_client_api_query(self.subscription_query, user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    #
    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """
    #     subscription = f.AccountSubscriptionFactory.create()
    #     user = subscription.account
    #     permission = Permission.objects.get(codename='view_accountsubscriptioncredit')
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #
    #     variables = {
    #         "id": to_global_id("AccountSubscriptionNode", subscription.id),
    #         "accountId": to_global_id("AccountNode", subscription.account.id),
    #         "archived": False,
    #     }
    #
    #     # Now query single subscription and check
    #     executed = execute_test_client_api_query(self.subscription_query, user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['accountSubscription']['organizationSubscription']['id'],
    #         to_global_id('OrganizationSubscriptionNode', subscription.organization_subscription.id)
    #     )
    #
    #
    # def test_create_subscription(self):
    #     """ Create an account subscription """
    #     query = self.subscription_create_mutation
    #
    #     account = f.RegularUserFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #
    #     self.assertEqual(
    #         data['createAccountSubscription']['accountSubscription']['account']['id'],
    #         variables['input']['account']
    #     )
    #     self.assertEqual(
    #         data['createAccountSubscription']['accountSubscription']['organizationSubscription']['id'],
    #         variables['input']['organizationSubscription']
    #     )
    #     self.assertEqual(
    #         data['createAccountSubscription']['accountSubscription']['financePaymentMethod']['id'],
    #         variables['input']['financePaymentMethod']
    #     )
    #     self.assertEqual(data['createAccountSubscription']['accountSubscription']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['createAccountSubscription']['accountSubscription']['dateEnd'], variables['input']['dateEnd'])
    #     self.assertEqual(data['createAccountSubscription']['accountSubscription']['note'], variables['input']['note'])
    #     self.assertEqual(data['createAccountSubscription']['accountSubscription']['registrationFeePaid'], variables['input']['registrationFeePaid'])
    #
    #
    # def test_create_subscription_anon_user(self):
    #     """ Don't allow creating account subscriptions for non-logged in users """
    #     query = self.subscription_create_mutation
    #
    #     account = f.RegularUserFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)
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
    #     """ Allow creating subscriptions for users with permissions """
    #     query = self.subscription_create_mutation
    #
    #     account = f.RegularUserFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)
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
    #         data['createAccountSubscription']['accountSubscription']['organizationSubscription']['id'],
    #         variables['input']['organizationSubscription']
    #     )
    #
    #
    # def test_create_subscription_permission_denied(self):
    #     """ Check create subscription permission denied error message """
    #     query = self.subscription_create_mutation
    #     account = f.RegularUserFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_create
    #     variables['input']['account'] = to_global_id('AccountNode', account.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)
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
    # def test_update_subscription(self):
    #     """ Update a subscription """
    #     query = self.subscription_update_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #
    #     self.assertEqual(
    #       data['updateAccountSubscription']['accountSubscription']['organizationSubscription']['id'],
    #       variables['input']['organizationSubscription']
    #     )
    #     self.assertEqual(
    #       data['updateAccountSubscription']['accountSubscription']['financePaymentMethod']['id'],
    #       variables['input']['financePaymentMethod']
    #     )
    #     self.assertEqual(data['updateAccountSubscription']['accountSubscription']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['updateAccountSubscription']['accountSubscription']['dateEnd'], variables['input']['dateEnd'])
    #     self.assertEqual(data['updateAccountSubscription']['accountSubscription']['note'], variables['input']['note'])
    #     self.assertEqual(data['updateAccountSubscription']['accountSubscription']['registrationFeePaid'], variables['input']['registrationFeePaid'])
    #
    #
    # def test_update_subscription_anon_user(self):
    #     """ Don't allow updating subscriptions for non-logged in users """
    #     query = self.subscription_update_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)
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
    # def test_update_subscription_permission_granted(self):
    #     """ Allow updating subscriptions for users with permissions """
    #     query = self.subscription_update_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)
    #
    #     user = subscription.account
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
    #     self.assertEqual(data['updateAccountSubscription']['accountSubscription']['dateStart'], variables['input']['dateStart'])
    #
    #
    # def test_update_subscription_permission_denied(self):
    #     """ Check update subscription permission denied error message """
    #     query = self.subscription_update_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     organization_subscription = f.OrganizationSubscriptionFactory.create()
    #     finance_payment_method = f.FinancePaymentMethodFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
    #     variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
    #     variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)
    #
    #     user = subscription.account
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
    # def test_delete_subscription(self):
    #     """ Delete an account subscription """
    #     query = self.subscription_delete_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     print(data)
    #     self.assertEqual(data['deleteAccountSubscription']['ok'], True)
    #
    #
    # def test_delete_subscription_anon_user(self):
    #     """ Delete subscription denied for anon user """
    #     query = self.subscription_delete_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
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
    # def test_delete_subscription_permission_granted(self):
    #     """ Allow deleting subscriptions for users with permissions """
    #     query = self.subscription_delete_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
    #
    #     # Give permissions
    #     user = subscription.account
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
    #     self.assertEqual(data['deleteAccountSubscription']['ok'], True)
    #
    #
    # def test_delete_subscription_permission_denied(self):
    #     """ Check delete subscription permission denied error message """
    #     query = self.subscription_delete_mutation
    #     subscription = f.AccountSubscriptionFactory.create()
    #     variables = {"input":{}}
    #     variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
    #
    #     user = subscription.account
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
