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


class GQLOrganizationSubscriptionGroupSubscription(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.subscription = f.OrganizationSubscriptionFactory.create()
        self.group = f.OrganizationSubscriptionGroupFactory.create()
        self.group_subscription = f.OrganizationSubscriptionGroupSubscriptionFactory.create()

        self.subscription_id = to_global_id('OrganizationSubscriptionNode', self.subscription.pk)
        self.group_id = to_global_id('OrganizationSubscriptionGroupNode', self.group.pk)

        
        self.permission_view = 'view_organizationsubscriptiongroupsubscription'
        self.permission_add = 'add_organizationsubscriptiongroupsubscription'
        self.permission_change = 'change_organizationsubscriptiongroupsubscription'
        self.permission_delete = 'delete_organizationsubscriptiongroupsubscription'

        self.variables_create = {
            "input": {
                "organizationSubscription": self.subscription_id,
                "organizationSubscriptionGroup": self.group_id
            }
        }
        

        self.variables_delete = {
            "input": {
                "organizationSubscription": to_global_id('OrganizationSubscriptionNode', self.group_subscription.organization_subscription.pk),
                "organizationSubscriptionGroup": to_global_id('OrganizationSubscriptionGroupNode', self.group_subscription.organization_subscription_group.pk)
            }
        }


        self.subscriptiongroupsubscription_create_mutation = '''
  mutation AddCardToGroup($input: CreateOrganizationSubscriptionGroupSubscriptionInput!) {
    createOrganizationSubscriptionGroupSubscription(input:$input) {
      organizationSubscriptionGroupSubscription {
        id
        organizationSubscription {
          id
          name
        }
        organizationSubscriptionGroup {
          id
          name
        }
      }
    }
  }
'''

        self.subscriptiongroupsubscription_delete_mutation = '''
  mutation DeleteCardFromGroup($input: DeleteOrganizationSubscriptionGroupSubscriptionInput!) {
    deleteOrganizationSubscriptionGroupSubscription(input:$input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_create_subscriptiongroupsubscription(self):
        """ Create a subscriptiongroupsubscription """
        query = self.subscriptiongroupsubscription_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['createOrganizationSubscriptionGroupSubscription']['organizationSubscriptionGroupSubscription']['organizationSubscription']['id'], 
          self.subscription_id
        )
        self.assertEqual(
          data['createOrganizationSubscriptionGroupSubscription']['organizationSubscriptionGroupSubscription']['organizationSubscriptionGroup']['id'], 
          self.group_id
        )


    def test_create_subscriptiongroupsubscription_anon_user(self):
        """ Create a subscriptiongroupsubscription with anonymous user, check error message """
        query = self.subscriptiongroupsubscription_create_mutation

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_subscriptiongroupsubscription_permission_granted(self):
        """ Create a subscriptiongroupsubscription with a user having the add permission """
        query = self.subscriptiongroupsubscription_create_mutation
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
          data['createOrganizationSubscriptionGroupSubscription']['organizationSubscriptionGroupSubscription']['organizationSubscription']['id'], 
          self.subscription_id
        )
        self.assertEqual(
          data['createOrganizationSubscriptionGroupSubscription']['organizationSubscriptionGroupSubscription']['organizationSubscriptionGroup']['id'], 
          self.group_id
        )


    def test_create_subscriptiongroupsubscription_permission_denied(self):
        """ Create a subscriptiongroupsubscription with a user not having the add permission """
        query = self.subscriptiongroupsubscription_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_delete_subscriptiongroupsubscription(self):
        """ Delete a subscriptiongroupsubscription """
        query = self.subscriptiongroupsubscription_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['deleteOrganizationSubscriptionGroupSubscription']['ok'], True)

        exists = models.OrganizationSubscriptionGroupSubscription.objects.exists()
        self.assertEqual(exists, False)


    def test_delete_subscriptiongroupsubscription_anon_user(self):
        """ Delete a subscriptiongroupsubscription """
        query = self.subscriptiongroupsubscription_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_delete_subscriptiongroupsubscription_permission_granted(self):
        """ Allow archiving subscriptiongroupsubscriptions for users with permissions """
        query = self.subscriptiongroupsubscription_delete_mutation
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
        self.assertEqual(data['deleteOrganizationSubscriptionGroupSubscription']['ok'], True)

        exists = models.OrganizationSubscriptionGroupSubscription.objects.exists()
        self.assertEqual(exists, False)


    def test_delete_subscriptiongroupsubscription_permission_denied(self):
        """ Check delete subscriptiongroupsubscription permission denied error message """
        query = self.subscriptiongroupsubscription_delete_mutation
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

