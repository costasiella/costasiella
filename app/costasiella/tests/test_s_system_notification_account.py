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


class GQLSystemNotificationAccount(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_account = 'view_account'
        self.permission_view_systemnotification = 'view_systemnotification'
        self.permission_view = 'view_systemnotificationaccount'
        self.permission_add = 'add_systemnotificationaccount'
        self.permission_change = 'change_systemnotificationaccount'
        self.permission_delete = 'delete_systemnotificationaccount'

        self.system_notification_account = f.SystemNotificationAccountFactory.create()

        self.variables_query_one = {
            "id": to_global_id("SystemNotificationAccountNode", self.system_notification_account.id)
        }

        self.variables_create = {
            "input": {
                "account": to_global_id("AccountNode", self.system_notification_account.account.id),
                "systemNotification": to_global_id(
                    "SystemNotificationNode", self.system_notification_account.system_notification.id)
            }
        }

        self.variables_delete_id = {
            "input": {
                "id": to_global_id("SystemNotificationAccountNode", self.system_notification_account.id)
            }
        }

        self.variables_delete_account_and_notification = {
            "input": {
                "account": to_global_id("AccountNode", self.system_notification_account.account.id),
                "systemNotification": to_global_id(
                    "SystemNotificationNode", self.system_notification_account.system_notification.id)
            }
        }

        self.system_notification_accounts_query = '''
  query systemNotificationAccounts($after: String, $before: String) {
    systemNotificationAccounts(first: 15, before: $before, after: $after) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          account {
            id
          }
          systemNotification {
            id
          }
        }
      }
    }
  }
'''
        self.system_notification_account_query = '''
  query systemNotificationAccount($id: ID!) {
    systemNotificationAccount(id: $id) {
      id
      account {
        id
      }
      systemNotification {
        id
      }
    }
  }
'''

        self.system_notification_account_create_mutation = ''' 
  mutation CreateSystemNotificationAccount($input:CreateSystemNotificationAccountInput!) {
    createSystemNotificationAccount(input:$input) {
      systemNotificationAccount {
        id
        account {
          id
        }
        systemNotification {
          id
        }
      }
    }
  }
'''

        self.system_notification_account_delete_mutation = ''' 
  mutation DeleteSystemNotificationAccount($input:DeleteSystemNotificationAccountInput!) {
    deleteSystemNotificationAccount(input:$input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of system notification accounts """
        query = self.system_notification_accounts_query

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')
        item = data['systemNotificationAccounts']['edges'][0]['node']
        self.assertEqual(item['account']['id'], to_global_id(
            "AccountNode", self.system_notification_account.account.id
        ))
        self.assertEqual(item['systemNotification']['id'], to_global_id(
            "SystemNotificationNode",
            self.system_notification_account.system_notification.id)
        )

    def test_query_permission_granted(self):
        """ Query list of system notification accounts with user having view permission"""
        query = self.system_notification_accounts_query
        # Create regular user
        user = self.system_notification_account.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        # View account permission
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        # View system notification permission
        permission = Permission.objects.get(codename=self.permission_view_systemnotification)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user)
        data = executed.get('data')
        item = data['systemNotificationAccounts']['edges'][0]['node']
        self.assertEqual(item['account']['id'], to_global_id(
            "AccountNode", self.system_notification_account.account.id
        ))

    def test_query_permission_denied(self):
        """ Query list of system notification accounts as user without view permission"""
        query = self.system_notification_accounts_query
        # Create regular user
        user = self.system_notification_account.account

        executed = execute_test_client_api_query(query, user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_anon_user(self):
        """ Query list of system notification accounts as anon user - deleted shouldn't be visible"""
        query = self.system_notification_accounts_query

        executed = execute_test_client_api_query(query, self.anon_user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query system notification account """
        query = self.system_notification_account_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_one)
        data = executed.get('data')
        self.assertEqual(data['systemNotificationAccount']['account']['id'], to_global_id(
            "AccountNode", self.system_notification_account.account.id
        ))
        self.assertEqual(data['systemNotificationAccount']['systemNotification']['id'], to_global_id(
            "SystemNotificationNode",
            self.system_notification_account.system_notification.id)
        )

    def test_query_one_permission_granted(self):
        """ Query system notification account with user having view permission"""
        query = self.system_notification_account_query
        # Create regular user
        user = self.system_notification_account.account
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        # View account permission
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        # View system notification permission
        permission = Permission.objects.get(codename=self.permission_view_systemnotification)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query_one)
        data = executed.get('data')
        self.assertEqual(data['systemNotificationAccount']['account']['id'], to_global_id(
            "AccountNode", self.system_notification_account.account.id
        ))

    def test_query_one_permission_denied(self):
        """ Query system notification account as user without view permission"""
        query = self.system_notification_accounts_query
        # Create regular user
        user = self.system_notification_account.account

        executed = execute_test_client_api_query(query, user, variables=self.variables_query_one)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_anon_user(self):
        """ Query system notification account as anon user - deleted shouldn't be visible"""
        query = self.system_notification_account_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_one)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_system_notification_account(self):
        """ Create a system notification account """
        query = self.system_notification_account_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createSystemNotificationAccount']['systemNotificationAccount']['account']['id'],
                         variables['input']['account'])
        self.assertEqual(
            data['createSystemNotificationAccount']['systemNotificationAccount']['systemNotification']['id'],
            variables['input']['systemNotification']
        )

    def test_create_system_notification_account_anon_user(self):
        """ Create a system notification account """
        query = self.system_notification_account_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_system_notification_account_permission_granted(self):
        """ Create a system notification account """
        query = self.system_notification_account_create_mutation
        variables = self.variables_create

        # Create regular user
        user = self.system_notification_account.account
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        # View account permission
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        # View system notification permission
        permission = Permission.objects.get(codename=self.permission_view_systemnotification)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createSystemNotificationAccount']['systemNotificationAccount']['account']['id'],
                         variables['input']['account'])

    def test_create_system_notification_account_permission_denied(self):
        """ Create a system notification account permission denied """
        query = self.system_notification_account_create_mutation
        variables = self.variables_create

        # Create regular user
        user = self.system_notification_account.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_system_notification_account_using_id(self):
        """ Delete system notification account using an id """
        query = self.system_notification_account_delete_mutation

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_delete_id
        )
        data = executed.get('data')
        self.assertEqual(data['deleteSystemNotificationAccount']['ok'], True)

    def test_delete_system_notification_account_using_account_and_notification(self):
        """ Delete system notification account using an id """
        query = self.system_notification_account_delete_mutation

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=self.variables_delete_account_and_notification
        )
        data = executed.get('data')
        self.assertEqual(data['deleteSystemNotificationAccount']['ok'], True)

    def test_delete_system_notification_account_anon_user(self):
        """ Delete system notification account using an id """
        query = self.system_notification_account_delete_mutation

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_delete_id
        )

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_system_notification_account_permission_granted(self):
        """ Delete system notification account using an id - permission granted """
        query = self.system_notification_account_delete_mutation

        # Give permissions
        user = self.system_notification_account.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        # View account permission
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_delete_id
        )
        data = executed.get('data')
        self.assertEqual(data['deleteSystemNotificationAccount']['ok'], True)

    def test_delete_system_notification_account_permission_denied(self):
        """ Check delete system notification account permission denied error message """
        query = self.system_notification_account_delete_mutation

        user = self.system_notification_account.account
        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_delete_id
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
