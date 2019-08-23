# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.test import TestCase
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

        self.permission_view = 'view_financeappsettings'
        self.permission_add = 'add_financeappsettings'
        self.permission_change = 'change_financeappsettings'
        self.permission_delete = 'delete_financeappsettings'


        self.variables_update = {
            "input": {
                "name": "Updated appsettings",
                "code" : "9000"
            }
        }

        self.appsettings_query = '''
  query AppSettings($id: ID!) {
    appSettings(id:$id) {
      dateFormat
      timeFormat
    }
  }
'''

        self.appsettings_update_mutation = '''
  mutation UpdateFinanceCostCenter($input: UpdateFinanceCostCenterInput!) {
    updateFinanceCostcenter(input: $input) {
      financeCostcenter {
        id
        name
        code
      }
    }
  }
'''


    def tearDown(self):
        # This is run after every test
        pass


    def test_query_one(self):
        """ Query appsettings as admin """   
        print(to_global_id('AppSettingsNode', 1))

        # # First query appsettingss to get node id easily
        # node_id = self.get_node_id_of_first_appsettings()

        # # Now query single appsettings and check
        # executed = execute_test_client_api_query(self.appsettings_query, self.admin_user, variables={"id": node_id})
        # data = executed.get('data')
        # self.assertEqual(data['financeCostcenter']['name'], appsettings.name)
        # self.assertEqual(data['financeCostcenter']['archived'], appsettings.archived)
        # self.assertEqual(data['financeCostcenter']['code'], appsettings.code)


    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one glacount """   
    #     appsettings = f.FinanceCostCenterFactory.create()

    #     # First query appsettingss to get node id easily
    #     node_id = self.get_node_id_of_first_appsettings()

    #     # Now query single appsettings and check
    #     executed = execute_test_client_api_query(self.appsettings_query, self.anon_user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     appsettings = f.FinanceCostCenterFactory.create()

    #     # First query appsettingss to get node id easily
    #     node_id = self.get_node_id_of_first_appsettings()

    #     # Now query single appsettings and check
    #     executed = execute_test_client_api_query(self.appsettings_query, user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_financeappsettings')
    #     user.user_permissions.add(permission)
    #     user.save()
    #     appsettings = f.FinanceCostCenterFactory.create()

    #     # First query appsettingss to get node id easily
    #     node_id = self.get_node_id_of_first_appsettings()

    #     # Now query single location and check   
    #     executed = execute_test_client_api_query(self.appsettings_query, user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['financeCostcenter']['name'], appsettings.name)


    # def test_create_appsettings(self):
    #     """ Create a appsettings """
    #     query = self.appsettings_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['name'], variables['input']['name'])
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['archived'], False)
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['code'], variables['input']['code'])


    # def test_create_appsettings_anon_user(self):
    #     """ Don't allow creating appsettingss for non-logged in users """
    #     query = self.appsettings_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_create_location_permission_granted(self):
    #     """ Allow creating appsettingss for users with permissions """
    #     query = self.appsettings_create_mutation
    #     variables = self.variables_create

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['name'], variables['input']['name'])
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['archived'], False)
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['code'], variables['input']['code'])


    # def test_create_appsettings_permission_denied(self):
    #     """ Check create appsettings permission denied error message """
    #     query = self.appsettings_create_mutation
    #     variables = self.variables_create

    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_update_appsettings(self):
    #     """ Update a appsettings """
    #     query = self.appsettings_update_mutation
    #     appsettings = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_appsettings()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateFinanceCostcenter']['financeCostcenter']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateFinanceCostcenter']['financeCostcenter']['code'], variables['input']['code'])


    # def test_update_appsettings_anon_user(self):
    #     """ Don't allow updating appsettingss for non-logged in users """
    #     query = self.appsettings_update_mutation
    #     appsettings = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_appsettings()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_appsettings_permission_granted(self):
    #     """ Allow updating appsettingss for users with permissions """
    #     query = self.appsettings_update_mutation
    #     appsettings = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_appsettings()

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateFinanceCostcenter']['financeCostcenter']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateFinanceCostcenter']['financeCostcenter']['code'], variables['input']['code'])


    # def test_update_appsettings_permission_denied(self):
    #     """ Check update appsettings permission denied error message """
    #     query = self.appsettings_update_mutation
    #     appsettings = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_appsettings()

    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_archive_appsettings(self):
    #     """ Archive a appsettings """
    #     query = self.appsettings_archive_mutation
    #     appsettings = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_appsettings()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     print(data)
    #     self.assertEqual(data['archiveFinanceCostcenter']['financeCostcenter']['archived'], variables['input']['archived'])


    # def test_archive_appsettings_anon_user(self):
    #     """ Archive appsettings denied for anon user """
    #     query = self.appsettings_archive_mutation
    #     appsettings = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_appsettings()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_archive_appsettings_permission_granted(self):
    #     """ Allow archiving appsettingss for users with permissions """
    #     query = self.appsettings_archive_mutation
    #     appsettings = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_appsettings()

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveFinanceCostcenter']['financeCostcenter']['archived'], variables['input']['archived'])


    # def test_archive_appsettings_permission_denied(self):
    #     """ Check archive appsettings permission denied error message """
    #     query = self.appsettings_archive_mutation
    #     appsettings = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_appsettings()
        
    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')

