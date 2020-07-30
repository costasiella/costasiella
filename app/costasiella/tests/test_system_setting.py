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


class GQLSystemSetting(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_systemsetting'
        self.permission_add = 'add_systemsetting'
        self.permission_change = 'change_systemsetting'
        self.permission_delete = 'delete_systemsetting'
        
        self.variables_update = {
            "input": {
                "setting": "finance_currency",
                "value": "USD",
            }
        }


        self.settings_query = '''
  query SystemSettings($setting: String!) {
    systemSettings(setting: $setting) {
      edges {
        node {
          id
          setting
          value
        }
      }
    }
  }
'''

        self.setting_update_mutation = '''
  mutation UpdateSystemSetting($input: UpdateSystemSettingInput!) {
    updateSystemSetting(input: $input) {
      systemSetting {
        id
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    # def get_node_id_of_first_level(self):
    #     # query settings to get node id easily
    #     variables = {
    #         'archived': False
    #     }
    #     executed = execute_test_client_api_query(self.settings_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #
    #     return data['organizationsettings']['edges'][0]['node']['id']

    def test_query(self):
        """ Query list of settings """
        query = self.settings_query
        setting = f.SystemSettingFinanceCurrencyFactory.create()
        variables = {
            "setting": "finance_currency"
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        item = data['systemSettings']['edges'][0]['node']
        self.assertEqual(item['setting'], setting.setting)
        self.assertEqual(item['value'], setting.value)

    def test_query_permission_denied(self):
        """ Query list of settings as user without permissions """
        query = self.settings_query
        setting = f.SystemSettingFinanceCurrencyFactory.create()
        variables = {
            "setting": "finance_currency"
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of settings with view permission """
        query = self.settings_query
        setting = f.SystemSettingFinanceCurrencyFactory.create()
        variables = {
            "setting": "finance_currency"
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')
        item = data['systemSettings']['edges'][0]['node']
        self.assertEqual(item['setting'], setting.setting)


    def test_query_anon_user(self):
        """ Query list of settings as anon user """
        query = self.settings_query
        setting = f.SystemSettingFinanceCurrencyFactory.create()
        variables = {
            "setting": "finance_currency"
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    # def test_create_level(self):
    #     """ Create a level """
    #     query = self.level_create_mutation
    #     variables = self.variables_create
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createOrganizationLevel']['organizationLevel']['name'], variables['input']['name'])
    #     self.assertEqual(data['createOrganizationLevel']['organizationLevel']['archived'], False)
    #
    #
    # def test_create_level_anon_user(self):
    #     """ Create a level with anonymous user, check error message """
    #     query = self.level_create_mutation
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=self.variables_create
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    #
    # def test_create_level_permission_granted(self):
    #     """ Create a level with a user having the add permission """
    #     query = self.level_create_mutation
    #     variables = self.variables_create
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createOrganizationLevel']['organizationLevel']['name'], variables['input']['name'])
    #     self.assertEqual(data['createOrganizationLevel']['organizationLevel']['archived'], False)
    #
    #
    # def test_create_level_permission_denied(self):
    #     """ Create a level with a user not having the add permission """
    #     query = self.level_create_mutation
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=self.variables_create
    #     )
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    #
    # def test_update_level(self):
    #     """ Update a level as admin user """
    #     query = self.level_update_mutation
    #     level = f.OrganizationLevelFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_level()
    #
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateOrganizationLevel']['organizationLevel']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateOrganizationLevel']['organizationLevel']['archived'], False)
    #
    #
    # def test_update_level_anon_user(self):
    #     """ Update a level as anonymous user """
    #     query = self.level_update_mutation
    #     level = f.OrganizationLevelFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_level()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    #
    # def test_update_level_permission_granted(self):
    #     """ Update a level as user with permission """
    #     query = self.level_update_mutation
    #     level = f.OrganizationLevelFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_level()
    #
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateOrganizationLevel']['organizationLevel']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateOrganizationLevel']['organizationLevel']['archived'], False)
    #
    #
    # def test_update_level_permission_denied(self):
    #     """ Update a level as user without permissions """
    #     query = self.level_update_mutation
    #     level = f.OrganizationLevelFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_level()
    #
    #     user = f.RegularUserFactory.create()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    #
    # def test_archive_level(self):
    #     """ Archive a level """
    #     query = self.level_archive_mutation
    #     level = f.OrganizationLevelFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_level()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveOrganizationLevel']['organizationLevel']['archived'], variables['input']['archived'])
    #
    #
    # def test_archive_level_anon_user(self):
    #     """ Archive a level """
    #     query = self.level_archive_mutation
    #     level = f.OrganizationLevelFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_level()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    #
    #
    # def test_archive_level_permission_granted(self):
    #     """ Allow archiving settings for users with permissions """
    #     query = self.level_archive_mutation
    #     level = f.OrganizationLevelFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_level()
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveOrganizationLevel']['organizationLevel']['archived'], variables['input']['archived'])
    #
    #
    # def test_archive_level_permission_denied(self):
    #     """ Check archive level permission denied error message """
    #     query = self.level_archive_mutation
    #     level = f.OrganizationLevelFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_level()
    #
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    #
    #
