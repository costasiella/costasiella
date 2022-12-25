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


class GQLSystemNotification(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['system_mail_template.json', 'system_notification.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_systemmailtemplate = 'view_systemmailtemplate'
        self.permission_view = 'view_systemnotification'
        self.permission_add = 'add_systemnotification'
        self.permission_change = 'change_systemnotification'
        self.permission_delete = 'delete_systemnotification'

        self.system_notification = models.SystemNotification.objects.get(id=10000)

        self.system_notifications_query = '''
  query systemNotifications($after: String, $before: String) {
    systemNotifications(first: 15, before: $before, after: $after) {
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
          systemMailTemplate {
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
        """ Query list of system notifications """
        query = self.system_notifications_query

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')
        item = data['systemNotifications']['edges'][0]['node']
        self.assertEqual(item['name'], self.system_notification.name)
        self.assertEqual(item['systemMailTemplate']['id'], to_global_id(
            "SystemMailTemplateNode",
            self.system_notification.system_mail_template.id)
        )

    def test_query_permission_granted(self):
        """ Query list of system notifications with user having view permission"""
        query = self.system_notifications_query
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        # System mail template permission
        permission = Permission.objects.get(codename=self.permission_view_systemmailtemplate)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user)
        data = executed.get('data')
        item = data['systemNotifications']['edges'][0]['node']
        self.assertEqual(item['name'], self.system_notification.name)

    def test_query_permission_denied(self):
        """ Query list of system notifications as user without view permission"""
        query = self.system_notifications_query
        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(query, user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_anon_user(self):
        """ Query list of system notifications as anon user - deleted shouldn't be visible"""
        query = self.system_notifications_query

        executed = execute_test_client_api_query(query, self.anon_user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
