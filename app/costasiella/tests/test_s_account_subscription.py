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
from ..dudes import SystemSettingDude
from .. import models
from .. import schema


class GQLAccountSubscription(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['app_settings.json',
                'finance_invoice_group.json',
                'finance_invoice_group_defaults.json',
                'finance_payment_methods.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountsubscription'
        self.permission_add = 'add_accountsubscription'
        self.permission_change = 'change_accountsubscription'
        self.permission_delete = 'delete_accountsubscription'

        self.variables_create = {
            "input": {
                "dateStart": "2025-01-01",
                "dateEnd": "2025-12-31",
                "note": "creation note"
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

        self.subscriptions_query = '''
  query AccountSubscriptions($after: String, $before: String, $accountId: ID!) {
    accountSubscriptions(first: 15, before: $before, after: $after, account: $accountId) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          account {
            id
          }
          organizationSubscription {
            id
            name
          }
          financePaymentMethod {
            id
            name
          }
          dateStart
          dateEnd
          note
          registrationFeePaid
          createdAt
        }
      }
    }
    account(id:$accountId) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
'''

        self.subscriptions_query_accounts_with_empty_keynumber = '''
query AccountSubscriptions($after: String, $before: String) {
    accountSubscriptions(first: 25, before: $before, after: $after, account_KeyNumber_Isempty: true) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationSubscription {
            id
            name
            unlimited
          }
          financePaymentMethod {
            id
            name
          }
          dateStart
          dateEnd
          creditTotal
          registrationFeePaid
          account {
            id
            fullName
            keyNumber            
          }
          createdAt
        }
      }
    }
  }
'''

        self.subscription_query = '''
  query AccountSubscription($id: ID!, $accountId: ID!, $after: String, $before: String, $archived: Boolean!) {
    accountSubscription(id:$id) {
      id
      account {
          id
      }
      organizationSubscription {
        id
        name
      }
      financePaymentMethod {
        id
        name
      }
      dateStart
      dateEnd
      note
      registrationFeePaid
      createdAt
    }
    organizationSubscriptions(first: 100, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          name
        }
      }
    }
    financePaymentMethods(first: 100, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          name
          code
        }
      }
    }
    account(id:$accountId) {
      id
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
'''

        self.subscription_create_mutation = ''' 
  mutation CreateAccountSubscription($input: CreateAccountSubscriptionInput!) {
    createAccountSubscription(input: $input) {
      accountSubscription {
        id
        account {
          id
          firstName
          lastName
          email
        }
        organizationSubscription {
          id
          name
        }
        financePaymentMethod {
          id
          name
        }
        dateStart
        dateEnd
        note
        registrationFeePaid        
      }
    }
  }
'''

        # Same as regular subscription, but without financePaymentMethod field
        self.subscription_create_mutation_shop_direct_debit = ''' 
  mutation CreateAccountSubscription($input: CreateAccountSubscriptionInput!) {
    createAccountSubscription(input: $input) {
      accountSubscription {
        id
        account {
          id
          firstName
          lastName
          email
        }
        organizationSubscription {
          id
          name
        }
        dateStart
        dateEnd
        note
        registrationFeePaid        
      }
    }
  }
'''

        self.subscription_update_mutation = '''
  mutation UpdateAccountSubscription($input: UpdateAccountSubscriptionInput!) {
    updateAccountSubscription(input: $input) {
      accountSubscription {
        id
        account {
          id
          firstName
          lastName
          email
        }
        organizationSubscription {
          id
          name
        }
        financePaymentMethod {
          id
          name
        }
        dateStart
        dateEnd
        note
        registrationFeePaid        
      }
    }
  }
'''

        self.subscription_delete_mutation = '''
  mutation DeleteAccountSubscription($input: DeleteAccountSubscriptionInput!) {
    deleteAccountSubscription(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account subscriptions """
        query = self.subscriptions_query
        subscription = f.AccountSubscriptionFactory.create()
        variables = {
            'accountId': to_global_id('AccountNode', subscription.account.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptions']['edges'][0]['node']['organizationSubscription']['id'],
            to_global_id("OrganizationSubscriptionNode", subscription.organization_subscription.id)
        )
        self.assertEqual(
            data['accountSubscriptions']['edges'][0]['node']['financePaymentMethod']['id'],
            to_global_id("FinancePaymentMethodNode", subscription.finance_payment_method.id)
        )
        self.assertEqual(data['accountSubscriptions']['edges'][0]['node']['dateStart'], str(subscription.date_start))
        self.assertEqual(data['accountSubscriptions']['edges'][0]['node']['dateEnd'], subscription.date_end) # Factory is set to None so no string conversion required
        self.assertEqual(data['accountSubscriptions']['edges'][0]['node']['note'], subscription.note)
        self.assertEqual(data['accountSubscriptions']['edges'][0]['node']['registrationFeePaid'], subscription.registration_fee_paid)

    def test_query_accounts_with_empty_keynumber(self):
        """ Query list of account subscriptions - test isempty filter for account keynumber """

        # Ensure a key number is set, so any previous data doesn't show for the upcoming test
        models.Account.objects.filter(key_number="").update(key_number="stuff here")

        query = self.subscriptions_query_accounts_with_empty_keynumber
        subscription = f.AccountSubscriptionFactory.create()

        # Ensure account shows up
        account = subscription.account
        account.key_number = ""
        account.save()

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptions']['edges'][0]['node']['account']['keyNumber'],
            ""
        )

    def test_query_accounts_with_empty_keynumber(self):
        """ Check that no accounts are found with empty key numbers """

        query = self.subscriptions_query_accounts_with_empty_keynumber
        subscription = f.AccountSubscriptionFactory.create()

        # Ensure a key number is set, so any previous data doesn't show for the upcoming test
        models.Account.objects.filter(key_number="").update(key_number="stuff here")

        executed = execute_test_client_api_query(query, self.admin_user)

        data = executed.get('data')

        # Check that no subscriptions are returned
        self.assertEqual(len(data['accountSubscriptions']['edges']), 0)

    def test_query_permission_denied(self):
        """ Query list of account subscriptions - check permission denied """
        query = self.subscriptions_query
        subscription = f.AccountSubscriptionFactory.create()
        variables = {
            'accountId': to_global_id('AccountNode', subscription.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=subscription.account.id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        for subscription_node in data['accountSubscriptions']['edges']:
            self.assertEqual(subscription_node['node']['account']['id'], variables['accountId'])

    def test_query_permission_granted(self):
        """ Query list of account subscriptions with view permission """
        query = self.subscriptions_query
        subscription = f.AccountSubscriptionFactory.create()
        variables = {
            'accountId': to_global_id('AccountSubscriptionNode', subscription.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=subscription.account.id)
        permission = Permission.objects.get(codename='view_accountsubscription')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all subscriptions
        self.assertEqual(
            data['accountSubscriptions']['edges'][0]['node']['organizationSubscription']['id'],
            to_global_id("OrganizationSubscriptionNode", subscription.organization_subscription.id)
        )

    def test_query_anon_user(self):
        """ Query list of account subscriptions - anon user """
        query = self.subscriptions_query
        subscription = f.AccountSubscriptionFactory.create()
        variables = {
            'accountId': to_global_id('AccountSubscriptionNode', subscription.account.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account subscription as admin """
        subscription = f.AccountSubscriptionFactory.create()

        variables = {
            "id": to_global_id("AccountSubscriptionNode", subscription.id),
            "accountId": to_global_id("AccountNode", subscription.account.id),
            "archived": False,
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscription']['account']['id'],
            to_global_id('AccountNode', subscription.account.id)
        )
        self.assertEqual(
            data['accountSubscription']['organizationSubscription']['id'],
            to_global_id('OrganizationSubscriptionNode', subscription.organization_subscription.id)
        )
        self.assertEqual(
            data['accountSubscription']['financePaymentMethod']['id'],
            to_global_id('FinancePaymentMethodNode', subscription.finance_payment_method.id)
        )
        self.assertEqual(data['accountSubscription']['dateStart'], str(subscription.date_start))
        self.assertEqual(data['accountSubscription']['dateEnd'], subscription.date_end)
        self.assertEqual(data['accountSubscription']['note'], subscription.note)
        self.assertEqual(data['accountSubscription']['registrationFeePaid'], subscription.registration_fee_paid)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account subscription """
        subscription = f.AccountSubscriptionFactory.create()

        variables = {
            "id": to_global_id("AccountSubscriptionNode", subscription.id),
            "accountId": to_global_id("AccountNode", subscription.account.id),
            "archived": False,
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        subscription = f.AccountSubscriptionFactory.create()
        user = subscription.account

        variables = {
            "id": to_global_id("AccountSubscriptionNode", subscription.id),
            "accountId": to_global_id("AccountNode", subscription.account.id),
            "archived": False,
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        subscription = f.AccountSubscriptionFactory.create()
        user = subscription.account
        permission = Permission.objects.get(codename='view_accountsubscription')
        user.user_permissions.add(permission)
        user.save()


        variables = {
            "id": to_global_id("AccountSubscriptionNode", subscription.id),
            "accountId": to_global_id("AccountNode", subscription.account.id),
            "archived": False,
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscription']['organizationSubscription']['id'],
            to_global_id('OrganizationSubscriptionNode', subscription.organization_subscription.id)
        )

    def test_create_subscription(self):
        """ Create an account subscription """
        query = self.subscription_create_mutation

        account = f.RegularUserFactory.create()
        organization_subscription_price = f.OrganizationSubscriptionPriceFactory.create()
        organization_subscription = organization_subscription_price.organization_subscription
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountSubscription']['accountSubscription']['account']['id'],
            variables['input']['account']
        )
        self.assertEqual(
            data['createAccountSubscription']['accountSubscription']['organizationSubscription']['id'],
            variables['input']['organizationSubscription']
        )
        self.assertEqual(
            data['createAccountSubscription']['accountSubscription']['financePaymentMethod']['id'],
            variables['input']['financePaymentMethod']
        )
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['dateEnd'], variables['input']['dateEnd'])
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['note'], variables['input']['note'])

    def test_create_subscription_anon_user(self):
        """ Don't allow creating account subscriptions for non-logged in users """
        query = self.subscription_create_mutation

        account = f.RegularUserFactory.create()
        organization_subscription = f.OrganizationSubscriptionFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_subscription_permission_granted(self):
        """ Allow creating subscriptions for users with permissions """
        query = self.subscription_create_mutation

        account = f.RegularUserFactory.create()
        organization_subscription_price = f.OrganizationSubscriptionPriceFactory.create()
        organization_subscription = organization_subscription_price.organization_subscription
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

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
            data['createAccountSubscription']['accountSubscription']['organizationSubscription']['id'],
            variables['input']['organizationSubscription']
        )

    def test_create_subscription_user_shop_direct_debit(self):
        """ Allow users to create subscriptions for their own account """
        system_settings_dude = SystemSettingDude()
        system_settings_dude.set(
            "workflow_shop_subscription_payment_method",
            "DIRECTDEBIT"
        )

        finance_payment_method = models.FinancePaymentMethod.objects.get(id=103)

        query = self.subscription_create_mutation_shop_direct_debit

        account_bank_account = f.AccountBankAccountFactory.create()
        account = account_bank_account.account
        organization_subscription_price = f.OrganizationSubscriptionPriceFactory.create()
        organization_subscription = organization_subscription_price.organization_subscription
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode',
                                                                      organization_subscription.id)
        executed = execute_test_client_api_query(
            query,
            account,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountSubscription']['accountSubscription']['organizationSubscription']['id'],
            variables['input']['organizationSubscription']
        )
        latest_account_subscription = models.AccountSubscription.objects.latest('id')

        self.assertEqual(latest_account_subscription.finance_payment_method.id, 103)

        # Check a mandate was created
        self.assertEqual(
            models.AccountBankAccountMandate.objects.filter(account_bank_account=account_bank_account).exists(),
            True
        )

        # Check invoice item was created
        self.assertEqual(
            models.FinanceInvoiceItem.objects.filter(
                account_subscription=latest_account_subscription,
                subscription_year=latest_account_subscription.date_start.year,
                subscription_month=latest_account_subscription.date_start.month,
            ).exists(),
            True
        )

    def test_create_subscription_user_shop_direct_debit_cant_start_in_past(self):
        """ Allow users to create subscriptions for their own account """
        system_settings_dude = SystemSettingDude()
        system_settings_dude.set(
            "workflow_shop_subscription_payment_method",
            "DIRECTDEBIT"
        )

        query = self.subscription_create_mutation

        account = f.RegularUserFactory.create()
        organization_subscription = f.OrganizationSubscriptionFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode',
                                                                      organization_subscription.id)
        variables['input']['dateStart'] = '2019-01-01'

        executed = execute_test_client_api_query(
            query,
            account,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], "Subscription can't start in the past")

    def test_create_subscription_user_shop_direct_debit_cant_create_for_other_user(self):
        """ Allow users to create subscriptions for their own account, not others """
        system_settings_dude = SystemSettingDude()
        system_settings_dude.set(
            "workflow_shop_subscription_payment_method",
            "DIRECTDEBIT"
        )

        query = self.subscription_create_mutation

        account = f.RegularUserFactory.create()
        instructor = f.InstructorFactory.create()
        organization_subscription = f.OrganizationSubscriptionFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode',
                                                                      organization_subscription.id)

        executed = execute_test_client_api_query(
            query,
            instructor,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], "Permission denied!")

    def test_create_subscription_permission_denied(self):
        """ Check create subscription permission denied error message """
        system_settings_dude = SystemSettingDude()
        system_settings_dude.set(
            "workflow_shop_subscription_payment_method",
            "MOLLIE"
        )

        query = self.subscription_create_mutation
        account = f.RegularUserFactory.create()
        organization_subscription = f.OrganizationSubscriptionFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

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

    def test_update_subscription(self):
        """ Update a subscription """
        query = self.subscription_update_mutation
        subscription = f.AccountSubscriptionFactory.create()
        organization_subscription = f.OrganizationSubscriptionFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
        variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateAccountSubscription']['accountSubscription']['organizationSubscription']['id'],
          variables['input']['organizationSubscription']
        )
        self.assertEqual(
          data['updateAccountSubscription']['accountSubscription']['financePaymentMethod']['id'],
          variables['input']['financePaymentMethod']
        )
        self.assertEqual(data['updateAccountSubscription']['accountSubscription']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['updateAccountSubscription']['accountSubscription']['dateEnd'], variables['input']['dateEnd'])
        self.assertEqual(data['updateAccountSubscription']['accountSubscription']['note'], variables['input']['note'])
        self.assertEqual(data['updateAccountSubscription']['accountSubscription']['registrationFeePaid'], variables['input']['registrationFeePaid'])

    def test_update_subscription_anon_user(self):
        """ Don't allow updating subscriptions for non-logged in users """
        query = self.subscription_update_mutation
        subscription = f.AccountSubscriptionFactory.create()
        organization_subscription = f.OrganizationSubscriptionFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
        variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_subscription_permission_granted(self):
        """ Allow updating subscriptions for users with permissions """
        query = self.subscription_update_mutation
        subscription = f.AccountSubscriptionFactory.create()
        organization_subscription = f.OrganizationSubscriptionFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
        variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        user = subscription.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateAccountSubscription']['accountSubscription']['dateStart'], variables['input']['dateStart'])

    def test_update_subscription_permission_denied(self):
        """ Check update subscription permission denied error message """
        query = self.subscription_update_mutation
        subscription = f.AccountSubscriptionFactory.create()
        organization_subscription = f.OrganizationSubscriptionFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)
        variables['input']['organizationSubscription'] = to_global_id('OrganizationSubscriptionNode', organization_subscription.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        user = subscription.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_subscription(self):
        """ Delete an account subscription """
        query = self.subscription_delete_mutation
        subscription = f.AccountSubscriptionFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['deleteAccountSubscription']['ok'], True)

    def test_delete_subscription_anon_user(self):
        """ Delete subscription denied for anon user """
        query = self.subscription_delete_mutation
        subscription = f.AccountSubscriptionFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_subscription_permission_granted(self):
        """ Allow deleting subscriptions for users with permissions """
        query = self.subscription_delete_mutation
        subscription = f.AccountSubscriptionFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)

        # Give permissions
        user = subscription.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountSubscription']['ok'], True)

    def test_delete_subscription_permission_denied(self):
        """ Check delete subscription permission denied error message """
        query = self.subscription_delete_mutation
        subscription = f.AccountSubscriptionFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('AccountSubscriptionNode', subscription.id)

        user = subscription.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
