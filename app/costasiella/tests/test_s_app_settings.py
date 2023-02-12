# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser, Permission

from graphql_relay import to_global_id
from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema



class GQLAppSettings(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    fixtures = ['app_settings.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_appsettings'
        self.permission_add = 'add_appsettings'
        self.permission_change = 'change_appsettings'
        self.permission_delete = 'delete_appsettings'

        self.variables_update = {
            "input": {
                "dateFormat": "DD-MM-YYYY",
                "timeFormat" : "12"
            }
        }

        self.appsettings_query = '''
  query AppSettings {
    appSettings(id: "QXBwU2V0dGluZ3NOb2RlOjE=") {
      dateFormat
      timeFormat
      accountSignupEnabled
    }
  }
'''

        self.appsettings_update_mutation = '''
  mutation UpdateAppSettings($input: UpdateAppSettingsInput!) {
    updateAppSettings(input: $input) {
      appSettings {
        id
        dateFormat
        timeFormat
      }
    }
  }
'''


    def tearDown(self):
        # This is run after every test
        pass


    def test_query_one(self):
        """ Query appsettings as admin """   
        # print(to_global_id('AppSettingsNode', 1))

        executed = execute_test_client_api_query(self.appsettings_query, self.admin_user)
        data = executed.get('data')

        self.assertEqual(data['appSettings']['dateFormat'], "YYYY-MM-DD")
        self.assertEqual(data['appSettings']['timeFormat'], "24")
        self.assertTrue(data['appSettings']['accountSignupEnabled'])

    @override_settings(ACCOUNT_ADAPTER=\
                               'costasiella.allauth_adapters.account_adapter_no_signup.AccountAdapterNoSignup')
    def test_query_one_signup_closed(self):
        """ Query appsettings as admin - signup closed """
        # print(to_global_id('AppSettingsNode', 1))

        executed = execute_test_client_api_query(self.appsettings_query, self.admin_user)
        data = executed.get('data')

        self.assertFalse(data['appSettings']['accountSignupEnabled'])


    # query is allowed publicly
    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users """   
    #     executed = execute_test_client_api_query(self.appsettings_query, self.anon_user)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one_permission_regular_user(self):
    #     """ Permission granted when logged in """   
    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     # Now query single appsettings and check
    #     executed = execute_test_client_api_query(self.appsettings_query, user)
    #     data = executed.get('data')
        
    #     self.assertEqual(data['appSettings']['dateFormat'], "YYYY-MM-DD")


    def test_update_appsettings(self):
        """ Update appsettings """
        query = self.appsettings_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateAppSettings']['appSettings']['dateFormat'], variables['input']['dateFormat'])
        self.assertEqual(data['updateAppSettings']['appSettings']['timeFormat'], variables['input']['timeFormat'])


    def test_update_appsettings_anon_user(self):
        """ Don't allow updating appsettingss for non-logged in users """
        query = self.appsettings_update_mutation
        appsettings = f.FinanceCostCenterFactory.create()
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_appsettings_permission_granted(self):
        """ Allow updating appsettingss for users with permissions """
        query = self.appsettings_update_mutation
        appsettings = f.FinanceCostCenterFactory.create()
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
        self.assertEqual(data['updateAppSettings']['appSettings']['dateFormat'], variables['input']['dateFormat'])


    def test_update_appsettings_permission_denied(self):
        """ Check update appsettings permission denied error message """
        query = self.appsettings_update_mutation
        appsettings = f.FinanceCostCenterFactory.create()
        variables = self.variables_update

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
