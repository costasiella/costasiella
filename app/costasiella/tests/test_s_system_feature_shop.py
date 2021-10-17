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
from .. import models
from ..modules.gql_tools import get_rid
from .helpers import execute_test_client_api_query


class GQLSystemFeatureShop(TestCase):
    fixtures = ['system_feature_shop']

    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_systemfeatureshop'
        # self.permission_add = 'add_systemfeatureshop'
        self.permission_change = 'change_systemfeatureshop'
        # self.permission_delete = 'delete_systemfeatureshop'

        self.system_feature_shop = models.SystemFeatureShop.objects.get(id=1)
        
        self.variables_update = {
            "input": {
                "memberships": False,
                "subscriptions": False,
                "classpasses": False,
                "classes": False,
                "events": False,
                "accountDataDownload": False,
            }
        }

        self.settings_query = '''
  query SystemFeatureShop {
    systemFeatureShop(id: "U3lzdGVtRmVhdHVyZVNob3BOb2RlOjE=") {
      memberships
      subscriptions
      classpasses
      classes
      events
      accountDataDownload
    }
  }
'''

        self.setting_update_mutation = '''
  mutation UpdateSystemFeatureShop($input: UpdateSystemFeatureShopInput!) {
    updateSystemFeatureShop(input: $input) {
      systemFeatureShop {
        id
        memberships
        subscriptions
        classpasses
        classes
        events
        accountDataDownload
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query_one(self):
        """ Query shop features asd admin  """
        query = self.settings_query

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')
        item = data['systemFeatureShop']
        self.assertEqual(item['memberships'], self.system_feature_shop.memberships)
        self.assertEqual(item['subscriptions'], self.system_feature_shop.subscriptions)
        self.assertEqual(item['classpasses'], self.system_feature_shop.classpasses)
        self.assertEqual(item['classes'], self.system_feature_shop.classes)
        self.assertEqual(item['events'], self.system_feature_shop.events)
        self.assertEqual(item['accountDataDownload'], self.system_feature_shop.account_data_download)

    def test_query_one_anon_user(self):
        """ Query shop features as anon user """
        query = self.settings_query

        executed = execute_test_client_api_query(query, self.anon_user)
        data = executed.get('data')
        item = data['systemFeatureShop']
        self.assertEqual(item['memberships'], self.system_feature_shop.memberships)
        self.assertEqual(item['subscriptions'], self.system_feature_shop.subscriptions)
        self.assertEqual(item['classpasses'], self.system_feature_shop.classpasses)
        self.assertEqual(item['classes'], self.system_feature_shop.classes)
        self.assertEqual(item['events'], self.system_feature_shop.events)
        self.assertEqual(item['accountDataDownload'], self.system_feature_shop.account_data_download)

    def test_update_setting(self):
        """ Update shop features record """
        query = self.setting_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        # Check return value from schema
        self.assertEqual(data['updateSystemFeatureShop']['systemFeatureShop']['memberships'],
                         variables['input']['memberships'])
        self.assertEqual(data['updateSystemFeatureShop']['systemFeatureShop']['subscriptions'],
                         variables['input']['subscriptions'])
        self.assertEqual(data['updateSystemFeatureShop']['systemFeatureShop']['classpasses'],
                         variables['input']['classpasses'])
        self.assertEqual(data['updateSystemFeatureShop']['systemFeatureShop']['classes'],
                         variables['input']['classes'])
        self.assertEqual(data['updateSystemFeatureShop']['systemFeatureShop']['events'],
                         variables['input']['events'])
        self.assertEqual(data['updateSystemFeatureShop']['systemFeatureShop']['accountDataDownload'],
                         variables['input']['accountDataDownload'])

        # Check db
        features = models.SystemFeatureShop.objects.get(id=1)
        self.assertEqual(features.memberships, variables['input']['memberships'])
        self.assertEqual(features.subscriptions, variables['input']['subscriptions'])
        self.assertEqual(features.classpasses, variables['input']['classpasses'])
        self.assertEqual(features.classes, variables['input']['classes'])
        self.assertEqual(features.events, variables['input']['events'])
        self.assertEqual(features.account_data_download, variables['input']['accountDataDownload'])

    def test_update_shop_features_anon_user(self):
        """ Anon users can't update shop features """
        query = self.setting_update_mutation

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_update
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_shop_features_permission_granted(self):
        """ Update shop features with a user having change permissions """
        query = self.setting_update_mutation
        variables = self.variables_update

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

        self.assertEqual(data['updateSystemFeatureShop']['systemFeatureShop']['memberships'],
                         variables['input']['memberships'])

    def test_update_shop_features_permission_denied(self):
        """ Update shop features with a user not having change permissions  """
        query = self.setting_update_mutation

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_update
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
