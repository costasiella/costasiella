# from graphql.error.located_error import GraphQLLocatedError
import graphql

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models


class GQLSystemMailChimpList(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_systemmailchimplist'
        self.permission_add = 'add_systemmailchimplist'
        self.permission_change = 'change_systemmailchimplist'
        self.permission_delete = 'delete_systemmailchimplist'

        self.variables_create = {
            "input": {
                "name": "Special offers",
                "frequency": "Weekly",
                "description": "Our weekly promotions",
                "mailchimpListId": "ab45djb1"
            }
        }
        
        self.variables_update = {
            "input": {
                "name": "Special offers - updated",
                "frequency": "Weekly",
                "description": "Our weekly promotions",
                "mailchimpListId": "ab45djb1"
            }
        }

        self.variables_delete = {
            "input": {}
        }

        self.mailchimp_lists_query = '''
  query systemMailchimpLists($after: String, $before: String) {
    systemMailchimpLists(first: 15, before: $before, after: $after) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          name
          description
          frequency
          mailchimpListId
        }
      }
    }
  }
'''

        self.mailchimp_list_query = '''
  query SystemMailchimpList($id: ID!) {
    systemMailchimpList(id:$id) {
      id
      name
      description
      frequency
      mailchimpListId
    }
  }
'''

        self.mailchimp_list_create_mutation = '''
  mutation CreateSystemMailChimpList($input:CreateSystemMailChimpListInput!) {
    createSystemMailchimpList(input: $input) {
      systemMailchimpList{
        id
        name
        frequency
        description
        mailchimpListId
      }
    }
  }
'''

        self.mailchimp_list_update_mutation = '''
  mutation UpdateSystemMailChimpList($input:UpdateSystemMailChimpListInput!) {
    updateSystemMailchimpList(input: $input) {
      systemMailchimpList{
        id
        name    
        frequency
        description
        mailchimpListId
      }
    }
  }
'''

        self.mailchimp_list_delete_mutation = '''
mutation DeleteSystemMailChimpList($input: DeleteSystemMailChimpListInput!) {
  deleteSystemMailchimpList(input: $input) {
    ok
  }
}
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of mailchimp_lists """
        query = self.mailchimp_lists_query
        mailchimp_list = f.SystemMailChimpListFactory.create()

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')
        item = data['systemMailchimpLists']['edges'][0]['node']
        self.assertEqual(item['name'], mailchimp_list.name)
        self.assertEqual(item['frequency'], mailchimp_list.frequency)
        self.assertEqual(item['description'], mailchimp_list.description)
        self.assertEqual(item['mailchimpListId'], mailchimp_list.mailchimp_list_id)

    def test_query_anon_user(self):
        """ Query list of mailchimp_lists as anon user - deleted shouldn't be visible"""
        query = self.mailchimp_lists_query
        mailchimp_list = f.SystemMailChimpListFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one mailchimp_list """
        mailchimp_list = f.SystemMailChimpListFactory.create()

        # First query mailchimp_lists to get node id easily
        node_id = to_global_id('SystemMailChimpListNode', mailchimp_list.id)

        # Now query single mailchimp_list and check
        query = self.mailchimp_list_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['systemMailchimpList']['name'], mailchimp_list.name)
        self.assertEqual(data['systemMailchimpList']['frequency'], mailchimp_list.frequency)
        self.assertEqual(data['systemMailchimpList']['description'], mailchimp_list.description)
        self.assertEqual(data['systemMailchimpList']['mailchimpListId'], mailchimp_list.mailchimp_list_id)

    def test_query_one_anon_user(self):
        """ Deny permission to view deleted mailchimp_lists for anon users Query one mailchimp_list """
        query = self.mailchimp_list_query
        mailchimp_list = f.SystemMailChimpListFactory.create()

        node_id = to_global_id("SystemMailChimpListNode", mailchimp_list.id)
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_mailchimp_list(self):
        """ Create a mailchimp_list """
        query = self.mailchimp_list_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createSystemMailchimpList']['systemMailchimpList']['name'],
                         variables['input']['name'])
        self.assertEqual(data['createSystemMailchimpList']['systemMailchimpList']['frequency'],
                         variables['input']['frequency'])
        self.assertEqual(data['createSystemMailchimpList']['systemMailchimpList']['description'],
                         variables['input']['description'])
        self.assertEqual(data['createSystemMailchimpList']['systemMailchimpList']['mailchimpListId'],
                         variables['input']['mailchimpListId'])

    def test_create_mailchimp_list_anon_user(self):
        """ Create a mailchimp_list with anonymous user, check error message """
        query = self.mailchimp_list_create_mutation

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_mailchimp_list_permission_granted(self):
        """ Create a mailchimp_list with a user having the add permission """
        query = self.mailchimp_list_create_mutation
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
        self.assertEqual(data['createSystemMailchimpList']['systemMailchimpList']['name'],
                         variables['input']['name'])

    def test_create_mailchimp_list_permission_denied(self):
        """ Create a mailchimp_list with a user not having the add permission """
        query = self.mailchimp_list_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_mailchimp_list(self):
        """ Update a mailchimp_list as admin user """
        query = self.mailchimp_list_update_mutation
        mailchimp_list = f.SystemMailChimpListFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("SystemMailChimpNode", mailchimp_list.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateSystemMailchimpList']['systemMailchimpList']['name'],
                         variables['input']['name'])
        self.assertEqual(data['updateSystemMailchimpList']['systemMailchimpList']['frequency'],
                         variables['input']['frequency'])
        self.assertEqual(data['updateSystemMailchimpList']['systemMailchimpList']['description'],
                         variables['input']['description'])
        self.assertEqual(data['updateSystemMailchimpList']['systemMailchimpList']['mailchimpListId'],
                         variables['input']['mailchimpListId'])

    def test_update_mailchimp_list_anon_user(self):
        """ Update a mailchimp_list as anonymous user """
        query = self.mailchimp_list_update_mutation
        mailchimp_list = f.SystemMailChimpListFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("SystemMailChimpNode", mailchimp_list.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_mailchimp_list_permission_granted(self):
        """ Update a mailchimp_list as user with permission """
        query = self.mailchimp_list_update_mutation
        mailchimp_list = f.SystemMailChimpListFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("SystemMailChimpNode", mailchimp_list.id)

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
        self.assertEqual(data['updateSystemMailchimpList']['systemMailchimpList']['name'],
                         variables['input']['name'])

    def test_update_mailchimp_list_permission_denied(self):
        """ Update a mailchimp_list as user without permissions """
        query = self.mailchimp_list_update_mutation
        mailchimp_list = f.SystemMailChimpListFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("SystemMailChimpNode", mailchimp_list.id)

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_mailchimp_list(self):
        """ Archive a mailchimp_list """
        query = self.mailchimp_list_delete_mutation
        mailchimp_list = f.SystemMailChimpListFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("SystemMailChimpNode", mailchimp_list.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteSystemMailchimpList']['ok'], True)

    def test_delete_mailchimp_list_anon_user(self):
        """ Archive a mailchimp_list """
        query = self.mailchimp_list_delete_mutation
        mailchimp_list = f.SystemMailChimpListFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("SystemMailChimpNode", mailchimp_list.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_mailchimp_list_permission_granted(self):
        """ Allow archiving mailchimp_lists for users with permissions """
        query = self.mailchimp_list_delete_mutation
        mailchimp_list = f.SystemMailChimpListFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("SystemMailChimpNode", mailchimp_list.id)

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
        self.assertEqual(data['deleteSystemMailchimpList']['ok'], True)

    def test_delete_mailchimp_list_permission_denied(self):
        """ Check delete mailchimp_list permission denied error message """
        query = self.mailchimp_list_delete_mutation
        mailchimp_list = f.SystemMailChimpListFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("SystemMailChimpNode", mailchimp_list.id)

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
