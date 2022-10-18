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

        self.permission_view = 'view_systemnotificationaccount'
        self.permission_add = 'add_systemnotificationaccount'
        self.permission_change = 'change_systemnotificationaccount'
        self.permission_delete = 'delete_systemnotificationaccount'

        self.system_notification_account = f.SystemNotificationAccountFactory.create()

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

