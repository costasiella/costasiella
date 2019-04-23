# from graphql.error.located_error import GraphQLLocatedError
import graphql

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models

from graphql_relay import to_global_id


class GQLOrganizationSubscriptionGroup(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationsubscriptiongroup'
        self.permission_add = 'add_organizationsubscriptiongroup'
        self.permission_change = 'change_organizationsubscriptiongroup'
        self.permission_delete = 'delete_organizationsubscriptiongroup'

        self.variables_create = {
            "input": {
                "name": "New subscriptiongroup",
            }
        }
        
        self.variables_update = {
            "input": {
                "name": "Updated subscriptiongroup",
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }


        self.subscriptiongroups_query = '''
query OrganizationSubscriptionGroups($after: String, $before: String, $archived: Boolean) {
  organizationSubscriptionGroups(first: 15, before: $before, after: $after, archived: $archived) {
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
}
'''

        self.subscriptiongroup_query = '''
query getOrganizationSubscriptionGroup($id: ID!) {
    organizationSubscriptionGroup(id:$id) {
      id
      archived
      name
    }
  }
'''

        self.subscriptiongroup_create_mutation = '''
mutation CreateOrganizationSubscriptionGroup($input: CreateOrganizationSubscriptionGroupInput!) {
  createOrganizationSubscriptionGroup(input: $input) {
    organizationSubscriptionGroup {
      id
      archived
      name
    }
  }
}
'''

        self.subscriptiongroup_update_mutation = '''
  mutation UpdateOrganizationSubscriptionGroup($input: UpdateOrganizationSubscriptionGroupInput!) {
    updateOrganizationSubscriptionGroup(input: $input) {
      organizationSubscriptionGroup {
        id
        archived
        name
      }
    }
  }
'''

        self.subscriptiongroup_archive_mutation = '''
mutation ArchiveOrganizationSubscriptionGroup($input: ArchiveOrganizationSubscriptionGroupInput!) {
    archiveOrganizationSubscriptionGroup(input: $input) {
        organizationSubscriptionGroup {
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
        """ Query list of subscriptiongroups """
        query = self.subscriptiongroups_query
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        variables = {
            "archived": False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        item = data['organizationSubscriptionGroups']['edges'][0]['node']
        self.assertEqual(item['name'], subscriptiongroup.name)



    def test_query_permision_denied(self):
        """ Query list of subscriptiongroups as user without permissions """
        query = self.subscriptiongroups_query
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permision_granted(self):
        """ Query list of subscriptiongroups with view permission """
        query = self.subscriptiongroups_query
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')
        item = data['organizationSubscriptionGroups']['edges'][0]['node']
        self.assertEqual(item['name'], subscriptiongroup.name)


    def test_query_anon_user(self):
        """ Query list of subscriptiongroups as anon user """
        query = self.subscriptiongroups_query
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one subscriptiongroup """   
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()

        # First query subscriptiongroups to get node id easily
        node_id = to_global_id("OrganizationSubscriptionGroupNode", subscriptiongroup.pk)

        # Now query single subscriptiongroup and check
        query = self.subscriptiongroup_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        print(data)
        self.assertEqual(data['organizationSubscriptionGroup']['name'], subscriptiongroup.name)
        self.assertEqual(data['organizationSubscriptionGroup']['archived'], subscriptiongroup.archived)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one subscriptiongroup """   
        query = self.subscriptiongroup_query
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        node_id = to_global_id("OrganizationSubscriptionGroupNode", subscriptiongroup.pk)
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        query = self.subscriptiongroup_query
        
        user = f.RegularUserFactory.create()
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        node_id = to_global_id("OrganizationSubscriptionGroupNode", subscriptiongroup.pk)

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        query = self.subscriptiongroup_query
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationsubscriptiongroup')
        user.user_permissions.add(permission)
        user.save()

        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        node_id = to_global_id("OrganizationSubscriptionGroupNode", subscriptiongroup.pk)

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationSubscriptionGroup']['name'], subscriptiongroup.name)


    def test_create_subscriptiongroup(self):
        """ Create a subscriptiongroup """
        query = self.subscriptiongroup_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationSubscriptionGroup']['organizationSubscriptionGroup']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationSubscriptionGroup']['organizationSubscriptionGroup']['archived'], False)


    def test_create_subscriptiongroup_anon_user(self):
        """ Create a subscriptiongroup with anonymous user, check error message """
        query = self.subscriptiongroup_create_mutation

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_subscriptiongroup_permission_granted(self):
        """ Create a subscriptiongroup with a user having the add permission """
        query = self.subscriptiongroup_create_mutation
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
        self.assertEqual(data['createOrganizationSubscriptionGroup']['organizationSubscriptionGroup']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationSubscriptionGroup']['organizationSubscriptionGroup']['archived'], False)


    def test_create_subscriptiongroup_permission_denied(self):
        """ Create a subscriptiongroup with a user not having the add permission """
        query = self.subscriptiongroup_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_update_subscriptiongroup(self):
        """ Update a subscriptiongroup as admin user """
        query = self.subscriptiongroup_update_mutation
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationSubscriptionGroupNode", subscriptiongroup.pk)
        

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganizationSubscriptionGroup']['organizationSubscriptionGroup']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationSubscriptionGroup']['organizationSubscriptionGroup']['archived'], False)


    def test_update_subscriptiongroup_anon_user(self):
        """ Update a subscriptiongroup as anonymous user """
        query = self.subscriptiongroup_update_mutation
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationSubscriptionGroupNode", subscriptiongroup.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_subscriptiongroup_permission_granted(self):
        """ Update a subscriptiongroup as user with permission """
        query = self.subscriptiongroup_update_mutation
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationSubscriptionGroupNode", subscriptiongroup.pk)

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
        self.assertEqual(data['updateOrganizationSubscriptionGroup']['organizationSubscriptionGroup']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationSubscriptionGroup']['organizationSubscriptionGroup']['archived'], False)


    def test_update_subscriptiongroup_permission_denied(self):
        """ Update a subscriptiongroup as user without permissions """
        query = self.subscriptiongroup_update_mutation
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationSubscriptionGroupNode", subscriptiongroup.pk)

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_archive_subscriptiongroup(self):
        """ Archive a subscriptiongroup """
        query = self.subscriptiongroup_archive_mutation
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationSubscriptionGroupNode", subscriptiongroup.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationSubscriptionGroup']['organizationSubscriptionGroup']['archived'], variables['input']['archived'])


    def test_archive_subscriptiongroup_anon_user(self):
        """ Archive a subscriptiongroup """
        query = self.subscriptiongroup_archive_mutation
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationSubscriptionGroupNode", subscriptiongroup.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_subscriptiongroup_permission_granted(self):
        """ Allow archiving subscriptiongroups for users with permissions """
        query = self.subscriptiongroup_archive_mutation
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationSubscriptionGroupNode", subscriptiongroup.pk)

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
        self.assertEqual(data['archiveOrganizationSubscriptionGroup']['organizationSubscriptionGroup']['archived'], variables['input']['archived'])


    def test_archive_subscriptiongroup_permission_denied(self):
        """ Check archive subscriptiongroup permission denied error message """
        query = self.subscriptiongroup_archive_mutation
        subscriptiongroup = f.OrganizationSubscriptionGroupFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationSubscriptionGroupNode", subscriptiongroup.pk)

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


