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



class GQLFinanceQuoteGroup(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financequotegroup'
        self.permission_add = 'add_financequotegroup'
        self.permission_change = 'change_financequotegroup'
        self.permission_delete = 'delete_financequotegroup'

        self.variables_create = {
            "input": {
                "displayPublic": True,
                "name": "New quotegroup",
                "expiresAfterDays": 24,
                "prefix": "INV",
                "prefixYear": False,
                "autoResetPrefixYear": False,
                "terms": "Terms here",
                "footer": "Footer",
                "code": "70"
            }
        }

        self.variables_update = {
            "input": {
                "displayPublic": True,
                "name": "Updated quotegroup",
                "expiresAfterDays": 24,
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

        self.quotegroups_query = '''
  query FinanceQuoteGroupsQuery($archived: Boolean!) {
    financeQuoteGroups(archived: $archived) {
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
          expiresAfterDays
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

        self.quotegroup_query = '''
  query FinanceQuoteGroup($id: ID!) {
    financeQuoteGroup(id:$id) {
      id
      archived
      displayPublic
      name
      nextId
      expiresAfterDays
      prefix
      prefixYear
      autoResetPrefixYear
      terms
      footer
      code
    }
  }
'''

        self.quotegroup_create_mutation = ''' 
  mutation CreateFinanceQuoteGroup($input:CreateFinanceQuoteGroupInput!) {
    createFinanceQuoteGroup(input: $input) {
      financeQuoteGroup{
        id
        archived
        displayPublic
        name
        nextId
        expiresAfterDays
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

        self.quotegroup_update_mutation = '''
  mutation UpdateFinanceQuoteGroup($input: UpdateFinanceQuoteGroupInput!) {
    updateFinanceQuoteGroup(input: $input) {
      financeQuoteGroup {
        id
        archived
        displayPublic
        name
        nextId
        expiresAfterDays
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

        self.quotegroup_archive_mutation = '''
  mutation ArchiveFinanceQuoteGroup($input: ArchiveFinanceQuoteGroupInput!) {
    archiveFinanceQuoteGroup(input: $input) {
      financeQuoteGroup {
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
        """ Query list of quotegroups """
        query = self.quotegroups_query
        quotegroup = f.FinanceQuoteGroupFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['id'], 
            to_global_id('FinanceQuoteGroupNode', quotegroup.id))
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['archived'], quotegroup.archived)
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['displayPublic'], quotegroup.display_public)
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['name'], quotegroup.name)
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['nextId'], quotegroup.next_id)
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['expiresAfterDays'],
                         quotegroup.expires_after_days)
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['prefix'], quotegroup.prefix)
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['prefixYear'], quotegroup.prefix_year)
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['autoResetPrefixYear'],
                         quotegroup.auto_reset_prefix_year)
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['terms'], quotegroup.terms)
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['footer'], quotegroup.footer)
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['code'], quotegroup.code)

    def test_query_permission_denied(self):
        """ Query list of quotegroups - check permission denied """
        query = self.quotegroups_query
        quotegroup = f.FinanceQuoteGroupFactory.create()
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)

        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of quotegroups with view permission """
        query = self.quotegroups_query
        quotegroup = f.FinanceQuoteGroupFactory.create()
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financequotegroup')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all quotegroups
        self.assertEqual(data['financeQuoteGroups']['edges'][0]['node']['name'], quotegroup.name)


    def test_query_anon_user(self):
        """ Query list of quotegroups - anon user """
        query = self.quotegroups_query
        quotegroup = f.FinanceQuoteGroupFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one quotegroup as admin """   
        quotegroup = f.FinanceQuoteGroupFactory.create()

        # First query quotegroups to get node id easily
        node_id = to_global_id('FinanceQuoteGroupNode', quotegroup.id)

        # Now query single quotegroup and check
        executed = execute_test_client_api_query(self.quotegroup_query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')

        self.assertEqual(data['financeQuoteGroup']['name'], quotegroup.name)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one glacount """   
        quotegroup = f.FinanceQuoteGroupFactory.create()

        # First query quotegroups to get node id easily
        node_id = to_global_id('FinanceQuoteGroupNode', quotegroup.id)

        # Now query single quotegroup and check
        executed = execute_test_client_api_query(self.quotegroup_query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        quotegroup = f.FinanceQuoteGroupFactory.create()

        # First query quotegroups to get node id easily
        node_id = to_global_id('FinanceQuoteGroupNode', quotegroup.id)

        # Now query single quotegroup and check
        executed = execute_test_client_api_query(self.quotegroup_query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financequotegroup')
        user.user_permissions.add(permission)
        user.save()
        quotegroup = f.FinanceQuoteGroupFactory.create()

        # First query quotegroups to get node id easily
        node_id = to_global_id('FinanceQuoteGroupNode', quotegroup.id)

        # Now query single location and check   
        executed = execute_test_client_api_query(self.quotegroup_query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financeQuoteGroup']['name'], quotegroup.name)


    def test_create_quotegroup(self):
        """ Create a quotegroup """
        query = self.quotegroup_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['createFinanceQuoteGroup']['financeQuoteGroup']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['createFinanceQuoteGroup']['financeQuoteGroup']['name'], variables['input']['name'])
        self.assertEqual(data['createFinanceQuoteGroup']['financeQuoteGroup']['nextId'], 1)
        self.assertEqual(data['createFinanceQuoteGroup']['financeQuoteGroup']['expiresAfterDays'], variables['input']['expiresAfterDays'])
        self.assertEqual(data['createFinanceQuoteGroup']['financeQuoteGroup']['prefix'], variables['input']['prefix'])
        self.assertEqual(data['createFinanceQuoteGroup']['financeQuoteGroup']['prefixYear'], variables['input']['prefixYear'])
        self.assertEqual(data['createFinanceQuoteGroup']['financeQuoteGroup']['autoResetPrefixYear'], variables['input']['autoResetPrefixYear'])
        self.assertEqual(data['createFinanceQuoteGroup']['financeQuoteGroup']['terms'], variables['input']['terms'])
        self.assertEqual(data['createFinanceQuoteGroup']['financeQuoteGroup']['footer'], variables['input']['footer'])
        self.assertEqual(data['createFinanceQuoteGroup']['financeQuoteGroup']['code'], variables['input']['code'])


    def test_create_quotegroup_anon_user(self):
        """ Don't allow creating quotegroups for non-logged in users """
        query = self.quotegroup_create_mutation
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
        """ Allow creating quotegroups for users with permissions """
        query = self.quotegroup_create_mutation
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
        self.assertEqual(data['createFinanceQuoteGroup']['financeQuoteGroup']['name'], variables['input']['name'])


    def test_create_quotegroup_permission_denied(self):
        """ Check create quotegroup permission denied error message """
        query = self.quotegroup_create_mutation
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


    def test_update_quotegroup(self):
        """ Update a quotegroup """
        query = self.quotegroup_update_mutation
        quotegroup = f.FinanceQuoteGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteGroupNode', quotegroup.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinanceQuoteGroup']['financeQuoteGroup']['id'], variables['input']['id'])
        self.assertEqual(data['updateFinanceQuoteGroup']['financeQuoteGroup']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['updateFinanceQuoteGroup']['financeQuoteGroup']['name'], variables['input']['name'])
        self.assertEqual(data['updateFinanceQuoteGroup']['financeQuoteGroup']['nextId'], 1)
        self.assertEqual(data['updateFinanceQuoteGroup']['financeQuoteGroup']['expiresAfterDays'], variables['input']['expiresAfterDays'])
        self.assertEqual(data['updateFinanceQuoteGroup']['financeQuoteGroup']['prefix'], variables['input']['prefix'])
        self.assertEqual(data['updateFinanceQuoteGroup']['financeQuoteGroup']['prefixYear'], variables['input']['prefixYear'])
        self.assertEqual(data['updateFinanceQuoteGroup']['financeQuoteGroup']['autoResetPrefixYear'], variables['input']['autoResetPrefixYear'])
        self.assertEqual(data['updateFinanceQuoteGroup']['financeQuoteGroup']['terms'], variables['input']['terms'])
        self.assertEqual(data['updateFinanceQuoteGroup']['financeQuoteGroup']['footer'], variables['input']['footer'])
        self.assertEqual(data['updateFinanceQuoteGroup']['financeQuoteGroup']['code'], variables['input']['code'])

    def test_update_quotegroup_anon_user(self):
        """ Don't allow updating quotegroups for non-logged in users """
        query = self.quotegroup_update_mutation
        quotegroup = f.FinanceQuoteGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteGroupNode', quotegroup.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_quotegroup_permission_granted(self):
        """ Allow updating quotegroups for users with permissions """
        query = self.quotegroup_update_mutation
        quotegroup = f.FinanceQuoteGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteGroupNode', quotegroup.id)

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
        self.assertEqual(data['updateFinanceQuoteGroup']['financeQuoteGroup']['name'], variables['input']['name'])


    def test_update_quotegroup_permission_denied(self):
        """ Check update quotegroup permission denied error message """
        query = self.quotegroup_update_mutation
        quotegroup = f.FinanceQuoteGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('FinanceQuoteGroupNode', quotegroup.id)

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


    def test_archive_quotegroup(self):
        """ Archive a quotegroup """
        query = self.quotegroup_archive_mutation
        quotegroup = f.FinanceQuoteGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinanceQuoteGroupNode', quotegroup.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveFinanceQuoteGroup']['financeQuoteGroup']['archived'], variables['input']['archived'])


    def test_archive_quotegroup_anon_user(self):
        """ Archive quotegroup denied for anon user """
        query = self.quotegroup_archive_mutation
        quotegroup = f.FinanceQuoteGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinanceQuoteGroupNode', quotegroup.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_quotegroup_permission_granted(self):
        """ Allow archiving quotegroups for users with permissions """
        query = self.quotegroup_archive_mutation
        quotegroup = f.FinanceQuoteGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinanceQuoteGroupNode', quotegroup.id)

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
        self.assertEqual(data['archiveFinanceQuoteGroup']['financeQuoteGroup']['archived'], variables['input']['archived'])


    def test_archive_quotegroup_permission_denied(self):
        """ Check archive quotegroup permission denied error message """
        query = self.quotegroup_archive_mutation
        quotegroup = f.FinanceQuoteGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('FinanceQuoteGroupNode', quotegroup.id)
        
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

