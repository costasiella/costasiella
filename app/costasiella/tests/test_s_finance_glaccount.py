# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema



class GQLFinanceGLAccount(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financeglaccount'
        self.permission_add = 'add_financeglaccount'
        self.permission_change = 'change_financeglaccount'
        self.permission_delete = 'delete_financeglaccount'

        self.variables_create = {
            "input": {
                "name": "New glaccount",
                "code": 8000
            }
        }

        self.variables_update = {
            "input": {
                "name": "Updated glaccount",
                "code": 9000
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.glaccounts_query = '''
  query FinanceGLAccounts($after: String, $before: String, $archived: Boolean) {
    financeGlaccounts(first: 15, before: $before, after: $after, archived: $archived) {
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

        self.glaccount_query = '''
  query FinanceGLAccount($id: ID!) {
    financeGlaccount(id:$id) {
      id
      name
      code
      archived
    }
  }
'''

        self.glaccount_create_mutation = ''' 
  mutation CreateFinanceGLAccount($input:CreateFinanceGLAccountInput!) {
    createFinanceGlaccount(input: $input) {
      financeGlaccount{
        id
        archived
        name
        code
      }
    }
  }
'''

        self.glaccount_update_mutation = '''
  mutation UpdateFinanceGLAccount($input: UpdateFinanceGLAccountInput!) {
    updateFinanceGlaccount(input: $input) {
      financeGlaccount {
        id
        name
        code
      }
    }
  }
'''

        self.glaccount_archive_mutation = '''
  mutation ArchiveFinanceGLAccount($input: ArchiveFinanceGLAccountInput!) {
    archiveFinanceGlaccount(input: $input) {
      financeGlaccount {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def get_node_id_of_first_glaccount(self):
        # query glaccounts to get node id easily
        variables = {
            'archived': False
        }
        executed = execute_test_client_api_query(self.glaccounts_query, self.admin_user, variables=variables)
        data = executed.get('data')
        
        return data['financeGlaccounts']['edges'][0]['node']['id']


    def test_query(self):
        """ Query list of glaccounts """
        query = self.glaccounts_query
        glaccount = f.FinanceGLAccountFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['financeGlaccounts']['edges'][0]['node']['name'], glaccount.name)
        self.assertEqual(data['financeGlaccounts']['edges'][0]['node']['archived'], glaccount.archived)
        self.assertEqual(data['financeGlaccounts']['edges'][0]['node']['code'], glaccount.code)


    def test_query_permission_denied(self):
        """ Query list of glaccounts - check permission denied """
        query = self.glaccounts_query
        glaccount = f.FinanceGLAccountFactory.create()
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of glaccounts with view permission """
        query = self.glaccounts_query
        glaccount = f.FinanceGLAccountFactory.create()
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financeglaccount')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all glaccounts
        self.assertEqual(data['financeGlaccounts']['edges'][0]['node']['name'], glaccount.name)
        self.assertEqual(data['financeGlaccounts']['edges'][0]['node']['archived'], glaccount.archived)
        self.assertEqual(data['financeGlaccounts']['edges'][0]['node']['code'], glaccount.code)


    def test_query_anon_user(self):
        """ Query list of glaccounts - anon user """
        query = self.glaccounts_query
        glaccount = f.FinanceGLAccountFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one glaccount as admin """   
        glaccount = f.FinanceGLAccountFactory.create()

        # First query glaccounts to get node id easily
        node_id = self.get_node_id_of_first_glaccount()

        # Now query single glaccount and check
        executed = execute_test_client_api_query(self.glaccount_query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financeGlaccount']['name'], glaccount.name)
        self.assertEqual(data['financeGlaccount']['archived'], glaccount.archived)
        self.assertEqual(data['financeGlaccount']['code'], glaccount.code)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one glacount """   
        glaccount = f.FinanceGLAccountFactory.create()

        # First query glaccounts to get node id easily
        node_id = self.get_node_id_of_first_glaccount()

        # Now query single glaccount and check
        executed = execute_test_client_api_query(self.glaccount_query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        glaccount = f.FinanceGLAccountFactory.create()

        # First query glaccounts to get node id easily
        node_id = self.get_node_id_of_first_glaccount()

        # Now query single glaccount and check
        executed = execute_test_client_api_query(self.glaccount_query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financeglaccount')
        user.user_permissions.add(permission)
        user.save()
        glaccount = f.FinanceGLAccountFactory.create()

        # First query glaccounts to get node id easily
        node_id = self.get_node_id_of_first_glaccount()

        # Now query single location and check   
        executed = execute_test_client_api_query(self.glaccount_query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financeGlaccount']['name'], glaccount.name)


    def test_create_glaccount(self):
        """ Create a glaccount """
        query = self.glaccount_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createFinanceGlaccount']['financeGlaccount']['name'], variables['input']['name'])
        self.assertEqual(data['createFinanceGlaccount']['financeGlaccount']['archived'], False)
        self.assertEqual(data['createFinanceGlaccount']['financeGlaccount']['code'], variables['input']['code'])


    def test_create_glaccount_anon_user(self):
        """ Don't allow creating glaccounts for non-logged in users """
        query = self.glaccount_create_mutation
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
        """ Allow creating glaccounts for users with permissions """
        query = self.glaccount_create_mutation
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
        self.assertEqual(data['createFinanceGlaccount']['financeGlaccount']['name'], variables['input']['name'])
        self.assertEqual(data['createFinanceGlaccount']['financeGlaccount']['archived'], False)
        self.assertEqual(data['createFinanceGlaccount']['financeGlaccount']['code'], variables['input']['code'])


    def test_create_glaccount_permission_denied(self):
        """ Check create glaccount permission denied error message """
        query = self.glaccount_create_mutation
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


    def test_update_glaccount(self):
        """ Update a glaccount """
        query = self.glaccount_update_mutation
        glaccount = f.FinanceGLAccountFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_glaccount()

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinanceGlaccount']['financeGlaccount']['name'], variables['input']['name'])
        self.assertEqual(data['updateFinanceGlaccount']['financeGlaccount']['code'], variables['input']['code'])


    def test_update_glaccount_anon_user(self):
        """ Don't allow updating glaccounts for non-logged in users """
        query = self.glaccount_update_mutation
        glaccount = f.FinanceGLAccountFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_glaccount()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_glaccount_permission_granted(self):
        """ Allow updating glaccounts for users with permissions """
        query = self.glaccount_update_mutation
        glaccount = f.FinanceGLAccountFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_glaccount()

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
        self.assertEqual(data['updateFinanceGlaccount']['financeGlaccount']['name'], variables['input']['name'])
        self.assertEqual(data['updateFinanceGlaccount']['financeGlaccount']['code'], variables['input']['code'])


    def test_update_glaccount_permission_denied(self):
        """ Check update glaccount permission denied error message """
        query = self.glaccount_update_mutation
        glaccount = f.FinanceGLAccountFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_glaccount()

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


    def test_archive_glaccount(self):
        """ Archive a glaccount """
        query = self.glaccount_archive_mutation
        glaccount = f.FinanceGLAccountFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_glaccount()

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['archiveFinanceGlaccount']['financeGlaccount']['archived'], variables['input']['archived'])


    def test_archive_glaccount_anon_user(self):
        """ Archive glaccount denied for anon user """
        query = self.glaccount_archive_mutation
        glaccount = f.FinanceGLAccountFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_glaccount()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_glaccount_permission_granted(self):
        """ Allow archiving glaccounts for users with permissions """
        query = self.glaccount_archive_mutation
        glaccount = f.FinanceGLAccountFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_glaccount()

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
        self.assertEqual(data['archiveFinanceGlaccount']['financeGlaccount']['archived'], variables['input']['archived'])


    def test_archive_glaccount_permission_denied(self):
        """ Check archive glaccount permission denied error message """
        query = self.glaccount_archive_mutation
        glaccount = f.FinanceGLAccountFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_glaccount()
        
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

