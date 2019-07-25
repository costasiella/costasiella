# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client

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
                "name": "New invoicegroup",
                "code" : "8000"
            }
        }

        self.variables_update = {
            "input": {
                "name": "Updated invoicegroup",
                "code" : "9000"
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.invoicegroups_query = '''
  query FinanceInvoiceGroups($after: String, $before: String, $archived: Boolean) {
    financeInvoiceGroups(first: 15, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id,
          archived,
          name,
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
      name
      code
      archived
    }
  }
'''

        self.invoicegroup_create_mutation = ''' 
  mutation CreateFinanceInvoiceGroup($input:CreateFinanceInvoiceGroupInput!) {
    createFinanceInvoiceGroup(input: $input) {
      financeInvoiceGroup{
        id
        archived
        name
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
        name
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


    def get_node_id_of_first_invoicegroup(self):
        # query invoicegroups to get node id easily
        variables = {
            'archived': False
        }
        executed = execute_test_client_api_query(self.invoicegroups_query, self.admin_user, variables=variables)
        data = executed.get('data')
        
        return data['financeInvoiceGroups']['edges'][0]['node']['id']


    def test_query(self):
        """ Query list of invoicegroups """
        query = self.invoicegroups_query
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['name'], invoicegroup.name)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['archived'], invoicegroup.archived)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['code'], invoicegroup.code)


    def test_query_permision_denied(self):
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


    def test_query_permision_granted(self):
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
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['archived'], invoicegroup.archived)
        self.assertEqual(data['financeInvoiceGroups']['edges'][0]['node']['code'], invoicegroup.code)


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
        node_id = self.get_node_id_of_first_invoicegroup()

        # Now query single invoicegroup and check
        executed = execute_test_client_api_query(self.invoicegroup_query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financeInvoiceGroup']['name'], invoicegroup.name)
        self.assertEqual(data['financeInvoiceGroup']['archived'], invoicegroup.archived)
        self.assertEqual(data['financeInvoiceGroup']['code'], invoicegroup.code)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one glacount """   
        invoicegroup = f.FinanceInvoiceGroupFactory.create()

        # First query invoicegroups to get node id easily
        node_id = self.get_node_id_of_first_invoicegroup()

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
        node_id = self.get_node_id_of_first_invoicegroup()

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
        node_id = self.get_node_id_of_first_invoicegroup()

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
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['name'], variables['input']['name'])
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['archived'], False)
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
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['archived'], False)
        self.assertEqual(data['createFinanceInvoiceGroup']['financeInvoiceGroup']['code'], variables['input']['code'])


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
        variables['input']['id'] = self.get_node_id_of_first_invoicegroup()

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['name'], variables['input']['name'])
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['code'], variables['input']['code'])


    def test_update_invoicegroup_anon_user(self):
        """ Don't allow updating invoicegroups for non-logged in users """
        query = self.invoicegroup_update_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_invoicegroup()

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
        variables['input']['id'] = self.get_node_id_of_first_invoicegroup()

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
        self.assertEqual(data['updateFinanceInvoiceGroup']['financeInvoiceGroup']['code'], variables['input']['code'])


    def test_update_invoicegroup_permission_denied(self):
        """ Check update invoicegroup permission denied error message """
        query = self.invoicegroup_update_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_invoicegroup()

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
        variables['input']['id'] = self.get_node_id_of_first_invoicegroup()

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        print(data)
        self.assertEqual(data['archiveFinanceInvoiceGroup']['financeInvoiceGroup']['archived'], variables['input']['archived'])


    def test_archive_invoicegroup_anon_user(self):
        """ Archive invoicegroup denied for anon user """
        query = self.invoicegroup_archive_mutation
        invoicegroup = f.FinanceInvoiceGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_invoicegroup()

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
        variables['input']['id'] = self.get_node_id_of_first_invoicegroup()

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
        variables['input']['id'] = self.get_node_id_of_first_invoicegroup()
        
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

