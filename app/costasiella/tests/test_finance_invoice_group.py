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



class GQLFinanceInvoiceGroup(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financeinvoicegroup'
        self.permission_add = 'add_financeinvoicegroup'
        self.permission_change = 'change_financeinvoicegroup'
        self.permission_delete = 'delete_financeinvoicegroup'

        self.variables_create = {
            "input": {
                "displayPublic": True,
                "name": "New invoicegroup",
                "dueAfterDays": 24,
                "prefix": "INV",
                "prefixYear": False,
                "autoResetPrefixYear": False,
                "terms": "Terms here",
                "footer": "Footer",
                "code" : "70"
            }
        }

        self.variables_update = {
            "input": {
                "displayPublic": True,
                "name": "Updated invoicegroup",
                "dueAfterDays": 24,
                "prefix": "INV",
                "prefixYear": False,
                "autoResetPrefixYear": False,
                "terms": "Terms here",
                "footer": "Footer",
                "code" : "70"
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.invoicegroups_query = '''
  query FinanceInvoiceGroupsQuery($archived: Boolean!) {
    financeInvoiceGroups(archived: $archived) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          archived
          displayPublic
          name
          nextId
          dueAfterDays
          prefix
          prefixYear
          autoResetPrefixYear
          terms
          footer
          code
        }
      }
    }
  }
'''

        self.invoicegroup_query = '''
  query FinanceInvoiceGroup($id: ID!) {
    financeInvoiceGroup(id:$id) {
      id
      archived
      displayPublic
      name
      nextId
      dueAfterDays
      prefix
      prefixYear
      autoResetPrefixYear
      terms
      footer
      code
    }
  }
'''

        self.invoicegroup_create_mutation = ''' 
  mutation CreateFinanceInvoiceGroup($input:CreateFinanceInvoiceGroupInput!) {
    createFinanceInvoiceGroup(input: $input) {
      financeInvoiceGroup{
        id
        archived
        displayPublic
        name
        nextId
        dueAfterDays
        prefix
        prefixYear
        autoResetPrefixYear
        terms
        footer
        code
      }
    }
  }
'''

        self.invoicegroup_update_mutation = '''
  mutation UpdateFinanceInvoiceGroup($input: UpdateFinanceInvoiceGroupInput!) {
    updateFinanceInvoiceGroup(input: $input) {
      financeInvoiceGroup {
        id
        archived
        displayPublic
        name
        nextId
        dueAfterDays
        prefix
        prefixYear
        autoResetPrefixYear
        terms
        footer
        code
      }
    }
  }
'''

        self.invoicegroup_archive_mutation = '''
  mutation ArchiveFinanceInvoiceGroup($input: ArchiveFinanceInvoiceGroupInput!) {
    archiveFinanceInvoiceGroup(input: $input) {
      financeInvoiceGroup {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of invoicegroups """
        query = self.invoicegroups_query
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['id'], 
            to_global_id('FinanceInvoiceGroupNode', invoicegroup.id))
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['archived'], invoicegroup.archived)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['displayPublic'], invoicegroup.display_public)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['name'], invoicegroup.name)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['nextId'], invoicegroup.next_id)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['dueAfterDays'], invoicegroup.due_after_days)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['prefix'], invoicegroup.prefix)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['prefixYear'], invoicegroup.prefix_year)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['autoResetPrefixYear'], invoicegroup.auto_reset_prefix_year)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['terms'], invoicegroup.terms)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['footer'], invoicegroup.footer)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['code'], invoicegroup.code)


    def test_query_permission_denied(self):
        """ Query list of invoicegroups - check permission denied """
        query = self.invoicegroups_query
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)

        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permission_granted(self):
        """ Query list of invoicegroups with view permission """
        query = self.invoicegroups_query
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financeinvoicegroup')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all invoicegroups
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['name'], invoicegroup.name)


    def test_query_anon_user(self):
        """ Query list of invoicegroups - anon user """
        query = self.invoicegroups_query
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one invoicegroup as admin """   
        invoicegroup = f.FinanceInvoiceGroupFactory.create()

        # First query invoicegroups to get node id easily
        node_id = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        # Now query single invoicegroup and check
        executed = execute_test_client_api_query(self.invoicegroup_query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')

        self.assertEqual(data['financeInvoiceGroup']['name'], invoicegroup.name)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one glacount """   
        invoicegroup = f.FinanceInvoiceGroupFactory.create()

        # First query invoicegroups to get node id easily
        node_id = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        # Now query single invoicegroup and check
        executed = execute_test_client_api_query(self.invoicegroup_query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        invoicegroup = f.FinanceInvoiceGroupFactory.create()

        # First query invoicegroups to get node id easily
        node_id = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        # Now query single invoicegroup and check
        executed = execute_test_client_api_query(self.invoicegroup_query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financeinvoicegroup')
        user.user_permissions.add(permission)
        user.save()
        invoicegroup = f.FinanceInvoiceGroupFactory.create()

        # First query invoicegroups to get node id easily
        node_id = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        # Now query single location and check   
        executed = execute_test_client_api_query(self.invoicegroup_query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financeInvoiceGroup']['name'], invoicegroup.name)


    def test_create_invoicegroup(self):
        """ Create a invoicegroup """
        query = self.invoicegroup_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['name'], variables['input']['name'])
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['nextId'], 1)
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['dueAfterDays'], variables['input']['dueAfterDays'])
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['prefix'], variables['input']['prefix'])
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['prefixYear'], variables['input']['prefixYear'])
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['autoResetPrefixYear'], variables['input']['autoResetPrefixYear'])
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['terms'], variables['input']['terms'])
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['footer'], variables['input']['footer'])
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['code'], variables['input']['code'])


    def test_create_invoicegroup_anon_user(self):
        """ Don't allow creating invoicegroups for non-logged in users """
        query = self.invoicegroup_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_location_permission_granted(self):
        """ Allow creating invoicegroups for users with permissions """
        query = self.invoicegroup_create_mutation
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
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['name'], variables['input']['name'])


    def test_create_invoicegroup_permission_denied(self):
        """ Check create invoicegroup permission denied error message """
        query = self.invoicegroup_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_update_invoicegroup(self):
        """ Update a invoicegroup """
        query = self.invoicegroup_update_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['id'], variables['input']['id'])
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['name'], variables['input']['name'])
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['nextId'], 1)
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['dueAfterDays'], variables['input']['dueAfterDays'])
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['prefix'], variables['input']['prefix'])
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['prefixYear'], variables['input']['prefixYear'])
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['autoResetPrefixYear'], variables['input']['autoResetPrefixYear'])
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['terms'], variables['input']['terms'])
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['footer'], variables['input']['footer'])
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['code'], variables['input']['code'])

    def test_update_invoicegroup_anon_user(self):
        """ Don't allow updating invoicegroups for non-logged in users """
        query = self.invoicegroup_update_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_invoicegroup_permission_granted(self):
        """ Allow updating invoicegroups for users with permissions """
        query = self.invoicegroup_update_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['name'], variables['input']['name'])


    def test_update_invoicegroup_permission_denied(self):
        """ Check update invoicegroup permission denied error message """
        query = self.invoicegroup_update_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_archive_invoicegroup(self):
        """ Archive a invoicegroup """
        query = self.invoicegroup_archive_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveFinanceInvoiceGroup']['financeInvoiceGroup']['archived'], variables['input']['archived'])


    def test_archive_invoicegroup_anon_user(self):
        """ Archive invoicegroup denied for anon user """
        query = self.invoicegroup_archive_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_invoicegroup_permission_granted(self):
        """ Allow archiving invoicegroups for users with permissions """
        query = self.invoicegroup_archive_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)

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
        self.assertEqual(data['archiveFinanceInvoiceGroup']['financeInvoiceGroup']['archived'], variables['input']['archived'])


    def test_archive_invoicegroup_permission_denied(self):
        """ Check archive invoicegroup permission denied error message """
        query = self.invoicegroup_archive_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinanceInvoiceGroupNode', invoicegroup.id)
        
        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

