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


class GQLOrganizationClasspassGroup(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationclasspassgroup'
        self.permission_add = 'add_organizationclasspassgroup'
        self.permission_change = 'change_organizationclasspassgroup'
        self.permission_delete = 'delete_organizationclasspassgroup'

        self.variables_create = {
            "input": {
                "name": "New classpassgroup",
                "description": "Classpass group description"
            }
        }
        
        self.variables_update = {
            "input": {
                "name": "Updated classpassgroup",
                "description": "Updated description for group"
            }
        }

        self.variable_delete = {
            "input": {}
        }

        self.classpassgroups_query = '''
query OrganizationClasspassGroups($after: String, $before: String) {
  organizationClasspassGroups(first: 15, before: $before, after: $after) {
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
      }
    }
  }
}
'''

        self.classpassgroup_query = '''
query getOrganizationClasspassGroup($id: ID!) {
    organizationClasspassGroup(id:$id) {
      id
      name
      description
    }
  }
'''

        self.classpassgroup_create_mutation = '''
mutation CreateOrganizationClasspassGroup($input: CreateOrganizationClasspassGroupInput!) {
  createOrganizationClasspassGroup(input: $input) {
    organizationClasspassGroup {
      id
      name
      description
    }
  }
}
'''

        self.classpassgroup_update_mutation = '''
  mutation UpdateOrganizationClasspassGroup($input: UpdateOrganizationClasspassGroupInput!) {
    updateOrganizationClasspassGroup(input: $input) {
      organizationClasspassGroup {
        id
        name
        description
      }
    }
  }
'''

        self.classpassgroup_delete_mutation = '''
mutation DeleteOrganizationClasspassGroup($input: DeleteOrganizationClasspassGroupInput!) {
    deleteOrganizationClasspassGroup(input: $input) {
        ok
    }
}
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of classpassgroups """
        query = self.classpassgroups_query
        classpassgroup = f.OrganizationClasspassGroupFactory.create()

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')
        item = data['organizationClasspassGroups']['edges'][0]['node']
        self.assertEqual(item['name'], classpassgroup.name)
        self.assertEqual(item['description'], classpassgroup.description)

    def test_query_permission_denied(self):
        """ Query list of classpassgroups as user without permissions """
        query = self.classpassgroups_query
        classpassgroup = f.OrganizationClasspassGroupFactory.create()

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of classpassgroups with view permission """
        query = self.classpassgroups_query
        classpassgroup = f.OrganizationClasspassGroupFactory.create()

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user)
        data = executed.get('data')
        item = data['organizationClasspassGroups']['edges'][0]['node']
        self.assertEqual(item['name'], classpassgroup.name)

    def test_query_anon_user(self):
        """ Query list of classpassgroups as anon user """
        query = self.classpassgroups_query
        classpassgroup = f.OrganizationClasspassGroupFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one classpassgroup """   
        classpassgroup = f.OrganizationClasspassGroupFactory.create()

        # First query classpassgroups to get node id easily
        node_id = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)

        # Now query single classpassgroup and check
        query = self.classpassgroup_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationClasspassGroup']['name'], classpassgroup.name)
        self.assertEqual(data['organizationClasspassGroup']['description'], classpassgroup.description)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one classpassgroup """   
        query = self.classpassgroup_query
        classpassgroup = f.OrganizationClasspassGroupFactory.create()
        node_id = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        query = self.classpassgroup_query
        
        user = f.RegularUserFactory.create()
        classpassgroup = f.OrganizationClasspassGroupFactory.create()
        node_id = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        query = self.classpassgroup_query
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationclasspassgroup')
        user.user_permissions.add(permission)
        user.save()

        classpassgroup = f.OrganizationClasspassGroupFactory.create()
        node_id = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationClasspassGroup']['name'], classpassgroup.name)

    def test_create_classpassgroup(self):
        """ Create a classpassgroup """
        query = self.classpassgroup_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationClasspassGroup']['organizationClasspassGroup']['name'],
                         variables['input']['name'])
        self.assertEqual(data['createOrganizationClasspassGroup']['organizationClasspassGroup']['description'],
                         variables['input']['description'])

    def test_create_classpassgroup_add_to_schedule_item(self):
        """ Is the classpass group added to all schedule items on creation? """
        schedule_item = f.SchedulePublicWeeklyClassFactory.create()

        query = self.classpassgroup_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationClasspassGroup']['organizationClasspassGroup']['name'],
                         variables['input']['name'])
        self.assertEqual(data['createOrganizationClasspassGroup']['organizationClasspassGroup']['description'],
                         variables['input']['description'])

        schedule_item_organization_classpass_group = models.ScheduleItemOrganizationClasspassGroup.objects.all().first()
        self.assertEqual(
            to_global_id("OrganizationClasspassGroupNode",
                         schedule_item_organization_classpass_group.organization_classpass_group.id),
            data['createOrganizationClasspassGroup']['organizationClasspassGroup']['id']
        )
        self.assertEqual(schedule_item_organization_classpass_group.shop_book, False)
        self.assertEqual(schedule_item_organization_classpass_group.attend, False)

    def test_create_classpassgroup_anon_user(self):
        """ Create a classpassgroup with anonymous user, check error message """
        query = self.classpassgroup_create_mutation

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_classpassgroup_permission_granted(self):
        """ Create a classpassgroup with a user having the add permission """
        query = self.classpassgroup_create_mutation
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
        self.assertEqual(data['createOrganizationClasspassGroup']['organizationClasspassGroup']['name'],
                         variables['input']['name'])

    def test_create_classpassgroup_permission_denied(self):
        """ Create a classpassgroup with a user not having the add permission """
        query = self.classpassgroup_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_classpassgroup(self):
        """ Update a classpassgroup as admin user """
        query = self.classpassgroup_update_mutation
        classpassgroup = f.OrganizationClasspassGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganizationClasspassGroup']['organizationClasspassGroup']['name'],
                         variables['input']['name'])
        self.assertEqual(data['updateOrganizationClasspassGroup']['organizationClasspassGroup']['description'],
                         variables['input']['description'])

    def test_update_classpassgroup_anon_user(self):
        """ Update a classpassgroup as anonymous user """
        query = self.classpassgroup_update_mutation
        classpassgroup = f.OrganizationClasspassGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_classpassgroup_permission_granted(self):
        """ Update a classpassgroup as user with permission """
        query = self.classpassgroup_update_mutation
        classpassgroup = f.OrganizationClasspassGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)

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
        self.assertEqual(data['updateOrganizationClasspassGroup']['organizationClasspassGroup']['name'],
                         variables['input']['name'])

    def test_update_classpassgroup_permission_denied(self):
        """ Update a classpassgroup as user without permissions """
        query = self.classpassgroup_update_mutation
        classpassgroup = f.OrganizationClasspassGroupFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_delete_classpassgroup(self):
        """ Delete a classpassgroup """
        query = self.classpassgroup_delete_mutation
        classpassgroup = f.OrganizationClasspassGroupFactory.create()
        variables = self.variable_delete
        variables['input']['id'] = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteOrganizationClasspassGroup']['ok'], True)

    def test_delete_classpassgroup_remove_from_schedule_item_class(self):
        """ Does deleting a classpassgroup remove it from a schedule item """
        query = self.classpassgroup_delete_mutation
        schedule_item_classpassgroup = f.ScheduleItemOrganizationClasspassGroupAllowFactory.create()
        classpassgroup = schedule_item_classpassgroup.organization_classpass_group
        variables = self.variable_delete
        variables['input']['id'] = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteOrganizationClasspassGroup']['ok'], True)

        self.assertEqual(models.ScheduleItemOrganizationClasspassGroup.objects.filter(
            id=schedule_item_classpassgroup.id).exists(),
            False
        )

    def test_delete_classpassgroup_anon_user(self):
        """ Delete a classpassgroup """
        query = self.classpassgroup_delete_mutation
        classpassgroup = f.OrganizationClasspassGroupFactory.create()
        variables = self.variable_delete
        variables['input']['id'] = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_classpassgroup_permission_granted(self):
        """ Allow deleting classpassgroups for users with permissions """
        query = self.classpassgroup_delete_mutation
        classpassgroup = f.OrganizationClasspassGroupFactory.create()
        variables = self.variable_delete
        variables['input']['id'] = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)

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
        self.assertEqual(data['deleteOrganizationClasspassGroup']['ok'], True)

    def test_delete_classpassgroup_permission_denied(self):
        """ Check delete classpassgroup permission denied error message """
        query = self.classpassgroup_delete_mutation
        classpassgroup = f.OrganizationClasspassGroupFactory.create()
        variables = self.variable_delete
        variables['input']['id'] = to_global_id("OrganizationClasspassGroupNode", classpassgroup.pk)

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
