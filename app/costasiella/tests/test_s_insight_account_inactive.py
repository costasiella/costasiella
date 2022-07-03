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

        self.variables_create = {
            "input": {
                "no_activity_after_date": str(timezone.now().date())
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

    #
    # def test_create_taxrate(self):
    #     """ Create a taxrate """
    #     query = self.taxrate_create_mutation
    #     variables = self.variables_create
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['name'], variables['input']['name'])
    #     self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['archived'], False)
    #     self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['percentage'], variables['input']['percentage'])
    #     self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['rateType'], variables['input']['rateType'])
    #     self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['code'], variables['input']['code'])
    #
    #
    # def test_create_taxrate_anon_user(self):
    #     """ Don't allow creating taxrates for non-logged in users """
    #     query = self.taxrate_create_mutation
    #     variables = self.variables_create
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
    #     """ Allow creating taxrates for users with permissions """
    #     query = self.taxrate_create_mutation
    #     variables = self.variables_create
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
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
    #     self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['name'], variables['input']['name'])
    #     self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['archived'], False)
    #     self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['percentage'], variables['input']['percentage'])
    #     self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['rateType'], variables['input']['rateType'])
    #     self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['code'], variables['input']['code'])
    #
    #
    # def test_create_taxrate_permission_denied(self):
    #     """ Check create taxrate permission denied error message """
    #     query = self.taxrate_create_mutation
    #     variables = self.variables_create
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
    #
    #
    # def test_update_taxrate(self):
    #     """ Update a taxrate """
    #     query = self.taxrate_update_mutation
    #     taxrate = f.FinanceTaxRateFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_taxrate()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['percentage'], variables['input']['percentage'])
    #     self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['rateType'], variables['input']['rateType'])
    #     self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['code'], variables['input']['code'])
    #
    #
    # def test_update_taxrate_anon_user(self):
    #     """ Don't allow updating taxrates for non-logged in users """
    #     query = self.taxrate_update_mutation
    #     taxrate = f.FinanceTaxRateFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_taxrate()
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
    # def test_update_taxrate_permission_granted(self):
    #     """ Allow updating taxrates for users with permissions """
    #     query = self.taxrate_update_mutation
    #     taxrate = f.FinanceTaxRateFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_taxrate()
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
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
    #     self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['percentage'], variables['input']['percentage'])
    #     self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['rateType'], variables['input']['rateType'])
    #     self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['code'], variables['input']['code'])
    #
    #
    # def test_update_taxrate_permission_denied(self):
    #     """ Check update taxrate permission denied error message """
    #     query = self.taxrate_update_mutation
    #     taxrate = f.FinanceTaxRateFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_taxrate()
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
    #
    #
    # def test_archive_taxrate(self):
    #     """ Archive a taxrate """
    #     query = self.taxrate_archive_mutation
    #     taxrate = f.FinanceTaxRateFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_taxrate()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     print(data)
    #     self.assertEqual(data['archiveFinanceTaxRate']['financeTaxRate']['archived'], variables['input']['archived'])
    #
    #
    # def test_archive_taxrate_anon_user(self):
    #     """ Archive taxrate denied for anon user """
    #     query = self.taxrate_archive_mutation
    #     taxrate = f.FinanceTaxRateFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_taxrate()
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
    # def test_archive_taxrate_permission_granted(self):
    #     """ Allow archiving taxrates for users with permissions """
    #     query = self.taxrate_archive_mutation
    #     taxrate = f.FinanceTaxRateFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_taxrate()
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
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
    #     self.assertEqual(data['archiveFinanceTaxRate']['financeTaxRate']['archived'], variables['input']['archived'])
    #
    #
    # def test_archive_taxrate_permission_denied(self):
    #     """ Check archive taxrate permission denied error message """
    #     query = self.taxrate_archive_mutation
    #     taxrate = f.FinanceTaxRateFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_taxrate()
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
    #
