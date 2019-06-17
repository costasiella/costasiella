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



class GQLAccountSubscription(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountsubscription'
        self.permission_add = 'add_accountsubscription'
        self.permission_change = 'change_accountsubscription'
        self.permission_delete = 'delete_accountsubscription'

        self.variables_create = {
            "input": {
                "name": "New subscription",
                "code" : "8000"
            }
        }

        self.variables_update = {
            "input": {
                "name": "Updated subscription",
                "code" : "9000"
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.subscriptions_query = '''
  query AccountSubscriptions($after: String, $before: String, $archived: Boolean) {
    accountSubscriptions(first: 15, before: $before, after: $after, archived: $archived) {
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

        self.subscription_query = '''
  query AccountSubscription($id: ID!) {
    accountSubscription(id:$id) {
      id
      name
      code
      archived
    }
  }
'''

        self.subscription_create_mutation = ''' 
  mutation CreateAccountSubscription($input:CreateAccountSubscriptionInput!) {
    createAccountSubscription(input: $input) {
      accountSubscription{
        id
        archived
        name
        code
      }
    }
  }
'''

        self.subscription_update_mutation = '''
  mutation UpdateAccountSubscription($input: UpdateAccountSubscriptionInput!) {
    updateAccountSubscription(input: $input) {
      accountSubscription {
        id
        name
        code
      }
    }
  }
'''

        self.subscription_archive_mutation = '''
  mutation ArchiveAccountSubscription($input: ArchiveAccountSubscriptionInput!) {
    archiveAccountSubscription(input: $input) {
      accountSubscription {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def get_node_id_of_first_subscription(self):
        # query subscriptions to get node id easily
        variables = {
            'archived': False
        }
        executed = execute_test_client_api_query(self.subscriptions_query, self.admin_user, variables=variables)
        data = executed.get('data')
        
        return data['accountSubscriptions']['edges'][0]['node']['id']


    def test_query(self):
        """ Query list of subscriptions """
        query = self.subscriptions_query
        subscription = f.AccountSubscriptionFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['accountSubscriptions']['edges'][0]['node']['name'], subscription.name)
        self.assertEqual(data['accountSubscriptions']['edges'][0]['node']['archived'], subscription.archived)
        self.assertEqual(data['accountSubscriptions']['edges'][0]['node']['code'], subscription.code)


    def test_query_permision_denied(self):
        """ Query list of subscriptions - check permission denied """
        query = self.subscriptions_query
        subscription = f.AccountSubscriptionFactory.create()
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permision_granted(self):
        """ Query list of subscriptions with view permission """
        query = self.subscriptions_query
        subscription = f.AccountSubscriptionFactory.create()
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_accountsubscription')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all subscriptions
        self.assertEqual(data['accountSubscriptions']['edges'][0]['node']['name'], subscription.name)
        self.assertEqual(data['accountSubscriptions']['edges'][0]['node']['archived'], subscription.archived)
        self.assertEqual(data['accountSubscriptions']['edges'][0]['node']['code'], subscription.code)


    def test_query_anon_user(self):
        """ Query list of subscriptions - anon user """
        query = self.subscriptions_query
        subscription = f.AccountSubscriptionFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one subscription as admin """   
        subscription = f.AccountSubscriptionFactory.create()

        # First query subscriptions to get node id easily
        node_id = self.get_node_id_of_first_subscription()

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['accountSubscription']['name'], subscription.name)
        self.assertEqual(data['accountSubscription']['archived'], subscription.archived)
        self.assertEqual(data['accountSubscription']['code'], subscription.code)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one glacount """   
        subscription = f.AccountSubscriptionFactory.create()

        # First query subscriptions to get node id easily
        node_id = self.get_node_id_of_first_subscription()

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        subscription = f.AccountSubscriptionFactory.create()

        # First query subscriptions to get node id easily
        node_id = self.get_node_id_of_first_subscription()

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_accountsubscription')
        user.user_permissions.add(permission)
        user.save()
        subscription = f.AccountSubscriptionFactory.create()

        # First query subscriptions to get node id easily
        node_id = self.get_node_id_of_first_subscription()

        # Now query single location and check   
        executed = execute_test_client_api_query(self.subscription_query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['accountSubscription']['name'], subscription.name)


    def test_create_subscription(self):
        """ Create a subscription """
        query = self.subscription_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['name'], variables['input']['name'])
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['archived'], False)
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['code'], variables['input']['code'])


    def test_create_subscription_anon_user(self):
        """ Don't allow creating subscriptions for non-logged in users """
        query = self.subscription_create_mutation
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
        """ Allow creating subscriptions for users with permissions """
        query = self.subscription_create_mutation
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
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['name'], variables['input']['name'])
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['archived'], False)
        self.assertEqual(data['createAccountSubscription']['accountSubscription']['code'], variables['input']['code'])


    def test_create_subscription_permission_denied(self):
        """ Check create subscription permission denied error message """
        query = self.subscription_create_mutation
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


    def test_update_subscription(self):
        """ Update a subscription """
        query = self.subscription_update_mutation
        subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_subscription()

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateAccountSubscription']['accountSubscription']['name'], variables['input']['name'])
        self.assertEqual(data['updateAccountSubscription']['accountSubscription']['code'], variables['input']['code'])


    def test_update_subscription_anon_user(self):
        """ Don't allow updating subscriptions for non-logged in users """
        query = self.subscription_update_mutation
        subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_subscription()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_subscription_permission_granted(self):
        """ Allow updating subscriptions for users with permissions """
        query = self.subscription_update_mutation
        subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_subscription()

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
        self.assertEqual(data['updateAccountSubscription']['accountSubscription']['name'], variables['input']['name'])
        self.assertEqual(data['updateAccountSubscription']['accountSubscription']['code'], variables['input']['code'])


    def test_update_subscription_permission_denied(self):
        """ Check update subscription permission denied error message """
        query = self.subscription_update_mutation
        subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_subscription()

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


    def test_archive_subscription(self):
        """ Archive a subscription """
        query = self.subscription_archive_mutation
        subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_subscription()

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        print(data)
        self.assertEqual(data['archiveAccountSubscription']['accountSubscription']['archived'], variables['input']['archived'])


    def test_archive_subscription_anon_user(self):
        """ Archive subscription denied for anon user """
        query = self.subscription_archive_mutation
        subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_subscription()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_subscription_permission_granted(self):
        """ Allow archiving subscriptions for users with permissions """
        query = self.subscription_archive_mutation
        subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_subscription()

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
        self.assertEqual(data['archiveAccountSubscription']['accountSubscription']['archived'], variables['input']['archived'])


    def test_archive_subscription_permission_denied(self):
        """ Check archive subscription permission denied error message """
        query = self.subscription_archive_mutation
        subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_subscription()
        
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

