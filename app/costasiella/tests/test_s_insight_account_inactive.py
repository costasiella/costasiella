# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils import timezone

from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema


class GQLInsightAccountInactive(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_insightaccountinactive'
        self.permission_add = 'add_insightaccountinactive'
        self.permission_change = 'change_insightaccountinactive'
        self.permission_delete = 'delete_insightaccountinactive'
        self.permission_delete_accounts = 'delete_insightaccountinactiveaccount'

        self.variables_create = {
            "input": {
                "noActivityAfterDate": str(timezone.now().date())
            }
        }

        self.variables_delete = {
            "input": {}
        }

        self.insight_accounts_inactives_query = '''
  query InsightAccountInactives {
    insightAccountInactives(first: 100) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          noActivityAfterDate 
          countInactiveAccounts
          countDeletedInactiveAccounts
          createdAt
        }
      }
    }
  }
'''

        self.insight_accounts_inactive_query = '''
  query InsightAccountInactive($id: ID!) {
    insightAccountInactive(id: $id) {
      id
      noActivityAfterDate
      countInactiveAccounts
      countDeletedInactiveAccounts
      createdAt
      accounts {
        edges {
          node {
            account {
              id
              fullName
              email
            }
          }
        }
      }
    }
  }
'''

        self.insight_accounts_inactive_create_mutation = ''' 
  mutation CreateInsightAccountInactive($input: CreateInsightAccountInactiveInput!) {
    createInsightAccountInactive(input: $input) {
      insightAccountInactive {
        id
        noActivityAfterDate
        countInactiveAccounts
        countDeletedInactiveAccounts
      }
    }
  }
'''

        self.insight_accounts_inactive_delete_mutation = '''
  mutation deleteInsightAccountInactive($input: DeleteInsightAccountInactiveInput!) {
    deleteInsightAccountInactive(input: $input){
      ok
    }
  }
'''

        self.insight_accounts_inactive_accounts_delete_mutation = '''
  mutation deleteInsightAccountInactiveAccounts($input: DeleteInsightAccountInactiveAccountsInput!) {
    deleteInsightAccountInactiveAccounts(input: $input){
      ok
    }
  } 
  
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of insight_account_inactives """
        query = self.insight_accounts_inactives_query
        insight_accounts_inactive = f.InsightAccountInactiveFactory.create()

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')
        self.assertEqual(data['insightAccountInactives']['edges'][0]['node']['id'],
                         to_global_id('InsightAccountInactiveNode', insight_accounts_inactive.id))
        self.assertEqual(data['insightAccountInactives']['edges'][0]['node']['countInactiveAccounts'], 0)
        self.assertEqual(data['insightAccountInactives']['edges'][0]['node']['countDeletedInactiveAccounts'], 0)
        self.assertEqual(data['insightAccountInactives']['edges'][0]['node']['noActivityAfterDate'],
                         str(timezone.now().date()))

    def test_query_anon_user(self):
        """ Query list of insight_account_inactives - anon user """
        query = self.insight_accounts_inactives_query
        insight_accounts_inactive = f.InsightAccountInactiveFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_permission_granted(self):
        """ Query list of insight inactive accounts with view permission """
        query = self.insight_accounts_inactives_query
        insight_accounts_inactive = f.InsightAccountInactiveFactory.create()

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user)
        data = executed.get('data')

        # Check if data is returned
        self.assertEqual(data['insightAccountInactives']['edges'][0]['node']['id'],
                         to_global_id('InsightAccountInactiveNode', insight_accounts_inactive.id))

    def test_query_permission_denied(self):
        """ Query list of insight inactive accounts - check permission denied """
        query = self.insight_accounts_inactives_query
        insight_accounts_inactive = f.InsightAccountInactiveFactory.create()

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one(self):
        """ Query one insight_accounts_inactive as admin """
        query = self.insight_accounts_inactive_query
        insight_accounts_inactive = f.InsightAccountInactiveFactory.create()

        node_id = to_global_id("InsightAccountInactiveNode", insight_accounts_inactive.id)

        # Now query single list of inactive accounts and check
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['insightAccountInactive']['id'], node_id)
        self.assertEqual(data['insightAccountInactive']['countInactiveAccounts'],
                         insight_accounts_inactive.count_inactive_accounts)
        self.assertEqual(data['insightAccountInactive']['countDeletedInactiveAccounts'],
                         insight_accounts_inactive.count_deleted_inactive_accounts)
        self.assertEqual(data['insightAccountInactive']['noActivityAfterDate'],
                         str(insight_accounts_inactive.no_activity_after_date))

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one insight accounts inactive """
        query = self.insight_accounts_inactive_query
        insight_accounts_inactive = f.InsightAccountInactiveFactory.create()

        node_id = to_global_id("InsightAccountInactiveNode", insight_accounts_inactive.id)

        # Now query single taxrate and check
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        query = self.insight_accounts_inactive_query
        insight_accounts_inactive = f.InsightAccountInactiveFactory.create()

        node_id = to_global_id("InsightAccountInactiveNode", insight_accounts_inactive.id)
        user = f.RegularUserFactory.create()

        # Now query single taxrate and check
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        query = self.insight_accounts_inactive_query
        insight_accounts_inactive = f.InsightAccountInactiveFactory.create()

        node_id = to_global_id("InsightAccountInactiveNode", insight_accounts_inactive.id)

        # grant permissions to user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        # Now query single location and check
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['insightAccountInactive']['id'], node_id)

    def test_create_insight_accounts_inactive(self):
        """ Create a insight accounts inactive list """
        query = self.insight_accounts_inactive_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createInsightAccountInactive']['insightAccountInactive']['noActivityAfterDate'],
                         variables['input']['noActivityAfterDate'])

    def test_create_insight_accounts_inactive_anon_user(self):
        """ Don't allow creating list of inactive users for non-logged in users """
        query = self.insight_accounts_inactive_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_insight_accounts_inactive_permission_granted(self):
        """ Allow creating list of inactive accounts for users with permissions """
        query = self.insight_accounts_inactive_create_mutation
        variables = self.variables_create

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
        self.assertEqual(data['createInsightAccountInactive']['insightAccountInactive']['noActivityAfterDate'],
                         variables['input']['noActivityAfterDate'])

    def test_create_insight_accounts_inactive_permission_denied(self):
        """ Check create taxrate permission denied error message """
        query = self.insight_accounts_inactive_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_insight_accounts_inactive(self):
        """ Delete list of inactive accounts (only list, not the accounts) """
        query = self.insight_accounts_inactive_delete_mutation
        insight_accounts_inactive = f.InsightAccountInactiveFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("InsightAccountsInactiveNode", insight_accounts_inactive.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteInsightAccountInactive']['ok'], True)

    def test_delete_insight_accounts_inactive_anon_user(self):
        """ Delete list of inactive accounts (only list, not accounts) - denied for anon user """
        query = self.insight_accounts_inactive_delete_mutation
        insight_accounts_inactive = f.InsightAccountInactiveFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("InsightAccountsInactiveNode", insight_accounts_inactive.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_insight_accounts_inactive_permission_granted(self):
        """ Allow Delete list of inactive accounts (only list, not accounts) for users with permissions """
        query = self.insight_accounts_inactive_delete_mutation
        insight_accounts_inactive = f.InsightAccountInactiveFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("InsightAccountsInactiveNode", insight_accounts_inactive.id)

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteInsightAccountInactive']['ok'], True)

    def test_delete_insight_accounts_inactive_permission_denied(self):
        """ Delete list of inactive accounts (only list, not accounts) - permission denied error message """
        query = self.insight_accounts_inactive_delete_mutation
        insight_accounts_inactive = f.InsightAccountInactiveFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("InsightAccountsInactiveNode", insight_accounts_inactive.id)

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_insight_accounts_inactive_accounts(self):
        """ Delete list of inactive accounts (not list, the accounts) """
        query = self.insight_accounts_inactive_accounts_delete_mutation
        insight_accounts_inactive_account = f.InsightAccountInactiveAccountFactory.create()
        insight_accounts_inactive_account_2 = f.InsightAccountInactiveAccountFactory.create(
            account=f.Instructor2Factory.create(),
            insight_account_inactive=f.InsightAccountInactiveFactory()
        )
        insight_accounts_inactive = insight_accounts_inactive_account.insight_account_inactive
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("InsightAccountsInactiveNode", insight_accounts_inactive.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteInsightAccountInactiveAccounts']['ok'], True)

        # Assert that the second account (instructor2) still exists and no
        # accounts from other lists have been removed
        account_2 = insight_accounts_inactive_account_2.account
        qs = models.Account.objects.filter(id=account_2.id)
        self.assertEqual(qs.exists(), True)

    def test_delete_insight_accounts_inactive_accounts_anon_user(self):
        """ Delete list of inactive accounts (not list, the accounts) - Not allowed for anon users """
        query = self.insight_accounts_inactive_accounts_delete_mutation
        insight_accounts_inactive_account = f.InsightAccountInactiveAccountFactory.create()
        insight_accounts_inactive = insight_accounts_inactive_account.insight_account_inactive
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("InsightAccountsInactiveNode", insight_accounts_inactive.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_insight_accounts_inactive_accounts_permission_granted(self):
        """ Delete list of inactive accounts (not list, the accounts) - Permission granted """
        query = self.insight_accounts_inactive_accounts_delete_mutation
        insight_accounts_inactive_account = f.InsightAccountInactiveAccountFactory.create()
        insight_accounts_inactive = insight_accounts_inactive_account.insight_account_inactive
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("InsightAccountsInactiveNode", insight_accounts_inactive.id)

        # Create regular user
        user = insight_accounts_inactive_account.account
        permission = Permission.objects.get(codename=self.permission_delete_accounts)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteInsightAccountInactiveAccounts']['ok'], True)

    def test_delete_insight_accounts_inactive_accounts_permission_denied(self):
        """ Delete list of inactive accounts (not list, the accounts) - Permission denied """
        query = self.insight_accounts_inactive_accounts_delete_mutation
        insight_accounts_inactive_account = f.InsightAccountInactiveAccountFactory.create()
        insight_accounts_inactive = insight_accounts_inactive_account.insight_account_inactive
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("InsightAccountsInactiveNode", insight_accounts_inactive.id)

        # Create regular user
        user = insight_accounts_inactive_account.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
