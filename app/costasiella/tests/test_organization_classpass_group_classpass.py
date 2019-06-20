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


class GQLOrganizationClasspassGroupClasspass(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.classpass = f.OrganizationClasspassFactory.create()
        self.group = f.OrganizationClasspassGroupFactory.create()
        self.group_classpass = f.OrganizationClasspassGroupClasspassFactory.create()

        self.classpass_id = to_global_id('OrganizationClasspassNode', self.classpass.pk)
        self.group_id = to_global_id('OrganizationClasspassGroupNode', self.group.pk)

        
        self.permission_view = 'view_organizationclasspassgroupclasspass'
        self.permission_add = 'add_organizationclasspassgroupclasspass'
        self.permission_change = 'change_organizationclasspassgroupclasspass'
        self.permission_delete = 'delete_organizationclasspassgroupclasspass'

        self.variables_create = {
            "input": {
                "organizationClasspass": self.classpass_id,
                "organizationClasspassGroup": self.group_id
            }
        }
        

        self.variables_delete = {
            "input": {
                "organizationClasspass": to_global_id('OrganizationClasspassNode', self.group_classpass.organization_classpass.pk),
                "organizationClasspassGroup": to_global_id('OrganizationClasspassGroupNode', self.group_classpass.organization_classpass_group.pk)
            }
        }


        self.classpassgroupclasspass_create_mutation = '''
  mutation AddCardToGroup($input: CreateOrganizationClasspassGroupClasspassInput!) {
    createOrganizationClasspassGroupClasspass(input:$input) {
      organizationClasspassGroupClasspass {
        id
        organizationClasspass {
          id
          name
        }
        organizationClasspassGroup {
          id
          name
        }
      }
    }
  }
'''

        self.classpassgroupclasspass_delete_mutation = '''
  mutation DeleteCardFromGroup($input: DeleteOrganizationClasspassGroupClasspassInput!) {
    deleteOrganizationClasspassGroupClasspass(input:$input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_create_classpassgroupclasspass(self):
        """ Create a classpassgroupclasspass """
        query = self.classpassgroupclasspass_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['createOrganizationClasspassGroupClasspass']['organizationClasspassGroupClasspass']['organizationClasspass']['id'], 
          self.classpass_id
        )
        self.assertEqual(
          data['createOrganizationClasspassGroupClasspass']['organizationClasspassGroupClasspass']['organizationClasspassGroup']['id'], 
          self.group_id
        )


    def test_create_classpassgroupclasspass_anon_user(self):
        """ Create a classpassgroupclasspass with anonymous user, check error message """
        query = self.classpassgroupclasspass_create_mutation

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_classpassgroupclasspass_permission_granted(self):
        """ Create a classpassgroupclasspass with a user having the add permission """
        query = self.classpassgroupclasspass_create_mutation
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
        self.assertEqual(
          data['createOrganizationClasspassGroupClasspass']['organizationClasspassGroupClasspass']['organizationClasspass']['id'], 
          self.classpass_id
        )
        self.assertEqual(
          data['createOrganizationClasspassGroupClasspass']['organizationClasspassGroupClasspass']['organizationClasspassGroup']['id'], 
          self.group_id
        )


    def test_create_classpassgroupclasspass_permission_denied(self):
        """ Create a classpassgroupclasspass with a user not having the add permission """
        query = self.classpassgroupclasspass_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_delete_classpassgroupclasspass(self):
        """ Delete a classpassgroupclasspass """
        query = self.classpassgroupclasspass_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['deleteOrganizationClasspassGroupClasspass']['ok'], True)

        exists = models.OrganizationClasspassGroupClasspass.objects.exists()
        self.assertEqual(exists, False)


    def test_delete_classpassgroupclasspass_anon_user(self):
        """ Delete a classpassgroupclasspass """
        query = self.classpassgroupclasspass_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_delete_classpassgroupclasspass_permission_granted(self):
        """ Allow archiving classpassgroupclasspasss for users with permissions """
        query = self.classpassgroupclasspass_delete_mutation
        variables = self.variables_delete

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
        self.assertEqual(data['deleteOrganizationClasspassGroupClasspass']['ok'], True)

        exists = models.OrganizationClasspassGroupClasspass.objects.exists()
        self.assertEqual(exists, False)


    def test_delete_classpassgroupclasspass_permission_denied(self):
        """ Check delete classpassgroupclasspass permission denied error message """
        query = self.classpassgroupclasspass_delete_mutation
        variables = self.variables_delete

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

