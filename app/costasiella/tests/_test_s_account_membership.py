# from graphql.error.located_error import GraphQLLocatedError
import graphql
import datetime

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


class GQLAccountMembership(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['app_settings.json',
                'finance_invoice_group.json',
                'finance_invoice_group_defaults.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountmembership'
        self.permission_add = 'add_accountmembership'
        self.permission_change = 'change_accountmembership'
        self.permission_delete = 'delete_accountmembership'

        self.variables_create = {
            "input": {
                "dateStart": "2019-01-01",
                "note": "creation note",
            }
        }

        self.variables_update = {
            "input": {
                "dateStart": "2017-01-01",
                "dateEnd": "2020-12-31",
                "note": "Update note",
            }
        }

        self.memberships_query = '''
  query AccountMemberships($after: String, $before: String, $accountId: ID!) {
    accountMemberships(first: 15, before: $before, after: $after, account: $accountId) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationMembership {
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

        self.membership_query = '''
  query AccountMembership($id: ID!, $accountId: ID!, $after: String, $before: String, $archived: Boolean!) {
    accountMembership(id:$id) {
      id
      account {
          id
      }
      organizationMembership {
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
      createdAt
    }
    organizationMemberships(first: 100, before: $before, after: $after, archived: $archived) {
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

        self.membership_create_mutation = ''' 
  mutation CreateAccountMembership($input: CreateAccountMembershipInput!) {
    createAccountMembership(input: $input) {
      accountMembership {
        id
        account {
          id
          firstName
          lastName
          email
        }
        organizationMembership {
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
      }
    }
  }
'''

        self.membership_update_mutation = '''
  mutation UpdateAccountMembership($input: UpdateAccountMembershipInput!) {
    updateAccountMembership(input: $input) {
      accountMembership {
        id
        account {
          id
          firstName
          lastName
          email
        }
        organizationMembership {
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
      }
    }
  }
'''

        self.membership_delete_mutation = '''
  mutation DeleteAccountMembership($input: DeleteAccountMembershipInput!) {
    deleteAccountMembership(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account memberships """
        query = self.memberships_query
        membership = f.AccountMembershipFactory.create()
        variables = {
            'accountId': to_global_id('AccountMembershipNode', membership.account.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountMemberships']['edges'][0]['node']['organizationMembership']['id'], 
            to_global_id("OrganizationMembershipNode", membership.organization_membership.id)
        )
        self.assertEqual(
            data['accountMemberships']['edges'][0]['node']['financePaymentMethod']['id'], 
            to_global_id("FinancePaymentMethodNode", membership.finance_payment_method.id)
        )
        self.assertEqual(data['accountMemberships']['edges'][0]['node']['dateStart'], str(membership.date_start))
        self.assertEqual(data['accountMemberships']['edges'][0]['node']['dateEnd'], str(membership.date_end))
        self.assertEqual(data['accountMemberships']['edges'][0]['node']['note'], membership.note)

    def test_query_permission_denied(self):
        """ Query list of account memberships - check permission denied """
        query = self.memberships_query
        membership = f.AccountMembershipFactory.create()
        variables = {
            'accountId': to_global_id('AccountMembershipNode', membership.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=membership.account.id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of account memberships with view permission """
        query = self.memberships_query
        membership = f.AccountMembershipFactory.create()
        variables = {
            'accountId': to_global_id('AccountMembershipNode', membership.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=membership.account.id)
        permission = Permission.objects.get(codename='view_accountmembership')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all memberships
        self.assertEqual(
            data['accountMemberships']['edges'][0]['node']['organizationMembership']['id'], 
            to_global_id("OrganizationMembershipNode", membership.organization_membership.id)
        )

    def test_query_anon_user(self):
        """ Query list of account memberships - anon user """
        query = self.memberships_query
        membership = f.AccountMembershipFactory.create()
        variables = {
            'accountId': to_global_id('AccountMembershipNode', membership.account.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account membership as admin """   
        membership = f.AccountMembershipFactory.create()
        
        variables = {
            "id": to_global_id("AccountMembershipNode", membership.id),
            "accountId": to_global_id("AccountNode", membership.account.id),
            "archived": False,
        }

        # Now query single membership and check
        executed = execute_test_client_api_query(self.membership_query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountMembership']['account']['id'], 
            to_global_id('AccountNode', membership.account.id)
        )
        self.assertEqual(
            data['accountMembership']['organizationMembership']['id'], 
            to_global_id('OrganizationMembershipNode', membership.organization_membership.id)
        )
        self.assertEqual(
            data['accountMembership']['financePaymentMethod']['id'], 
            to_global_id('FinancePaymentMethodNode', membership.finance_payment_method.id)
        )
        self.assertEqual(data['accountMembership']['dateStart'], str(membership.date_start))
        self.assertEqual(data['accountMembership']['dateEnd'], str(membership.date_end))
        self.assertEqual(data['accountMembership']['note'], membership.note)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account membership """   
        membership = f.AccountMembershipFactory.create()

        variables = {
            "id": to_global_id("AccountMembershipNode", membership.id),
            "accountId": to_global_id("AccountNode", membership.account.id),
            "archived": False,
        }

        # Now query single membership and check
        executed = execute_test_client_api_query(self.membership_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        membership = f.AccountMembershipFactory.create()
        user = membership.account

        variables = {
            "id": to_global_id("AccountMembershipNode", membership.id),
            "accountId": to_global_id("AccountNode", membership.account.id),
            "archived": False,
        }

        # Now query single membership and check
        executed = execute_test_client_api_query(self.membership_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        membership = f.AccountMembershipFactory.create()
        user = membership.account
        permission = Permission.objects.get(codename='view_accountmembership')
        user.user_permissions.add(permission)
        user.save()
        

        variables = {
            "id": to_global_id("AccountMembershipNode", membership.id),
            "accountId": to_global_id("AccountNode", membership.account.id),
            "archived": False,
        }

        # Now query single membership and check   
        executed = execute_test_client_api_query(self.membership_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountMembership']['organizationMembership']['id'], 
            to_global_id('OrganizationMembershipNode', membership.organization_membership.id)
        )

    def test_create_membership(self):
        """ Create an account membership """
        query = self.membership_create_mutation

        account = f.RegularUserFactory.create()
        organization_membership = f.OrganizationMembershipFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationMembership'] = to_global_id('OrganizationMembershipNode',
                                                                    organization_membership.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountMembership']['accountMembership']['account']['id'], 
            variables['input']['account']
        )
        self.assertEqual(
            data['createAccountMembership']['accountMembership']['organizationMembership']['id'], 
            variables['input']['organizationMembership']
        )
        self.assertEqual(
            data['createAccountMembership']['accountMembership']['financePaymentMethod']['id'], 
            variables['input']['financePaymentMethod']
        )
        self.assertEqual(data['createAccountMembership']['accountMembership']['dateStart'],
                         variables['input']['dateStart'])
        self.assertEqual(data['createAccountMembership']['accountMembership']['note'], variables['input']['note'])

        account_membership = models.AccountMembership.objects.all().first()
        finance_invoice = models.FinanceInvoice.objects.all().first()
        self.assertEqual(finance_invoice.summary, organization_membership.name)

        first_invoice_item = finance_invoice.items.all().first()
        self.assertEqual(first_invoice_item.product_name, "Membership")
        self.assertEqual(first_invoice_item.description, organization_membership.name)
        self.assertEqual(int(first_invoice_item.quantity), 1)
        self.assertEqual(first_invoice_item.total, organization_membership.price)
        self.assertEqual(first_invoice_item.account_membership, account_membership)
        self.assertEqual(first_invoice_item.finance_tax_rate, organization_membership.finance_tax_rate)
        self.assertEqual(first_invoice_item.finance_glaccount, organization_membership.finance_glaccount)
        self.assertEqual(first_invoice_item.finance_costcenter, organization_membership.finance_costcenter)

    def test_create_membership_valid_3_days(self):
        """ End date should be set 3 days from start """
        query = self.membership_create_mutation

        account = f.RegularUserFactory.create()
        organization_membership = f.OrganizationMembershipFactory.create()
        organization_membership.validity_unit = 'DAYS'
        organization_membership.validity = 3
        organization_membership.save()

        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationMembership'] = to_global_id('OrganizationMembershipNode',
                                                                    organization_membership.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountMembership']['accountMembership']['dateEnd'], 
            str(datetime.date(2019, 1, 1) + datetime.timedelta(days=2))
        )

    def test_create_membership_valid_2_weeks(self):
        """ End date should be set 2 weeks from start """
        query = self.membership_create_mutation

        account = f.RegularUserFactory.create()
        organization_membership = f.OrganizationMembershipFactory.create()
        organization_membership.validity_unit = 'WEEKS'
        organization_membership.validity = 2
        organization_membership.save()

        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationMembership'] = to_global_id('OrganizationMembershipNode', organization_membership.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountMembership']['accountMembership']['dateEnd'],
            str(datetime.date(2019, 1, 1) + datetime.timedelta(days=13))
        )

    def test_create_membership_valid_2_months(self):
        """ End date should be set 2 weeks from start """
        query = self.membership_create_mutation

        account = f.RegularUserFactory.create()
        organization_membership = f.OrganizationMembershipFactory.create()
        organization_membership.validity_unit = 'MONTHS'
        organization_membership.validity = 2
        organization_membership.save()

        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationMembership'] = to_global_id('OrganizationMembershipNode', organization_membership.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountMembership']['accountMembership']['dateEnd'],
            str(datetime.date(2019, 2, 28))
        )

    def test_create_membership_anon_user(self):
        """ Don't allow creating account memberships for non-logged in users """
        query = self.membership_create_mutation

        account = f.RegularUserFactory.create()
        organization_membership = f.OrganizationMembershipFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationMembership'] = to_global_id('OrganizationMembershipNode', organization_membership.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_membership_permission_granted(self):
        """ Allow creating memberships for users with permissions """
        query = self.membership_create_mutation

        account = f.RegularUserFactory.create()
        organization_membership = f.OrganizationMembershipFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationMembership'] = to_global_id('OrganizationMembershipNode', organization_membership.id)
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
            data['createAccountMembership']['accountMembership']['organizationMembership']['id'],
            variables['input']['organizationMembership']
        )

    def test_create_membership_permission_denied(self):
        """ Check create membership permission denied error message """
        query = self.membership_create_mutation
        account = f.RegularUserFactory.create()
        organization_membership = f.OrganizationMembershipFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationMembership'] = to_global_id('OrganizationMembershipNode', organization_membership.id)
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

    def test_update_membership(self):
        """ Update a membership """
        query = self.membership_update_mutation
        membership = f.AccountMembershipFactory.create()
        organization_membership = f.OrganizationMembershipFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountMembershipNode', membership.id)
        variables['input']['organizationMembership'] = to_global_id('OrganizationMembershipNode', organization_membership.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateAccountMembership']['accountMembership']['organizationMembership']['id'],
          variables['input']['organizationMembership']
        )
        self.assertEqual(
          data['updateAccountMembership']['accountMembership']['financePaymentMethod']['id'],
          variables['input']['financePaymentMethod']
        )
        self.assertEqual(data['updateAccountMembership']['accountMembership']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['updateAccountMembership']['accountMembership']['dateEnd'], variables['input']['dateEnd'])
        self.assertEqual(data['updateAccountMembership']['accountMembership']['note'], variables['input']['note'])

    def test_update_membership_anon_user(self):
        """ Don't allow updating memberships for non-logged in users """
        query = self.membership_update_mutation
        membership = f.AccountMembershipFactory.create()
        organization_membership = f.OrganizationMembershipFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountMembershipNode', membership.id)
        variables['input']['organizationMembership'] = to_global_id('OrganizationMembershipNode', organization_membership.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_membership_permission_granted(self):
        """ Allow updating memberships for users with permissions """
        query = self.membership_update_mutation
        membership = f.AccountMembershipFactory.create()
        organization_membership = f.OrganizationMembershipFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountMembershipNode', membership.id)
        variables['input']['organizationMembership'] = to_global_id('OrganizationMembershipNode', organization_membership.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        user = membership.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateAccountMembership']['accountMembership']['dateStart'], variables['input']['dateStart'])

    def test_update_membership_permission_denied(self):
        """ Check update membership permission denied error message """
        query = self.membership_update_mutation
        membership = f.AccountMembershipFactory.create()
        organization_membership = f.OrganizationMembershipFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountMembershipNode', membership.id)
        variables['input']['organizationMembership'] = to_global_id('OrganizationMembershipNode', organization_membership.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        user = membership.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_membership(self):
        """ Delete an account membership """
        query = self.membership_delete_mutation
        membership = f.AccountMembershipFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('AccountMembershipNode', membership.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountMembership']['ok'], True)

    def test_delete_membership_anon_user(self):
        """ Delete membership denied for anon user """
        query = self.membership_delete_mutation
        membership = f.AccountMembershipFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('AccountMembershipNode', membership.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_membership_permission_granted(self):
        """ Allow deleting memberships for users with permissions """
        query = self.membership_delete_mutation
        membership = f.AccountMembershipFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('AccountMembershipNode', membership.id)

        # Give permissions
        user = membership.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountMembership']['ok'], True)

    def test_delete_membership_permission_denied(self):
        """ Check delete membership permission denied error message """
        query = self.membership_delete_mutation
        membership = f.AccountMembershipFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('AccountMembershipNode', membership.id)

        user = membership.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
