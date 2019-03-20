# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema



class GQLFinanceGLAccount(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financeglaccount'
        self.permission_add = 'add_financeglaccount'
        self.permission_change = 'change_financeglaccount'
        self.permission_delete = 'delete_financeglaccount'

        self.glaccounts_query = '''
  query FinanceGLAccounts($after: String, $before: String, $archived: Boolean) {
    financeGlaccounts(first: 15, before: $before, after: $after, archived: $archived) {
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

        self.glaccount_query = '''
  query FinanceGLAccount($id: ID!) {
    financeGlaccount(id:$id) {
      id
      name
      code
      archived
    }
  }
'''

        self.glaccount_create_mutation = ''' 
  mutation CreateFinanceGLAccount($input:CreateFinanceGLAccountInput!) {
    createFinanceGlaccount(input: $input) {
      financeGlaccount{
        id
        archived
        name
        code
      }
    }
  }
'''

        self.glaccount_update_mutation = '''
  mutation UpdateFinanceGLAccount($input: UpdateFinanceGLAccountInput!) {
    updateFinanceGlaccount(input: $input) {
      financeGlaccount {
        id
        name
        code
      }
    }
  }
'''

        self.glaccount_archive_mutation = '''
  mutation ArchiveFinanceGLAccount($input: ArchiveFinanceGLAccountInput!) {
    archiveFinanceGlaccount(input: $input) {
      financeGlaccount {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def get_node_id_of_first_glaccount(self):
        # query glaccounts to get node id easily
        variables = {
            'archived': False
        }
        executed = execute_test_client_api_query(self.glaccounts_query, self.admin_user, variables=variables)
        data = executed.get('data')
        
        return data['financeGlaccounts']['edges'][0]['node']['id']


    def test_query(self):
        """ Query list of glaccounts """
        query = self.glacounts_query
        glaccount = f.FinanceGLAccountFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['schoolLocations']['edges'][0]['node']['name'], location.name)
        self.assertEqual(data['schoolLocations']['edges'][0]['node']['archived'], location.archived)
        self.assertEqual(data['schoolLocations']['edges'][0]['node']['displayPublic'], location.display_public)


    # def test_query_permision_denied(self):
    #     """ Query list of locations """
    #     query = self.locations_query
    #     location = f.SchoolLocationFactory.create()
    #     non_public_location = f.SchoolLocationFactory.build()
    #     non_public_location.display_public = False
    #     non_public_location.save()

    #     variables = {
    #         'archived': False
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')

    #     # Public locations only
    #     non_public_found = False
    #     for item in data['schoolLocations']['edges']:
    #         if not item['node']['displayPublic']:
    #             non_public_found = True

    #     self.assertEqual(non_public_found, False)


    # def test_query_permision_granted(self):
    #     """ Query list of locations """
    #     query = self.locations_query
    #     location = f.SchoolLocationFactory.create()
    #     non_public_location = f.SchoolLocationFactory.build()
    #     non_public_location.display_public = False
    #     non_public_location.save()

    #     variables = {
    #         'archived': False
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_schoollocation')
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')

    #     # List all locations, including non public
    #     non_public_found = False
    #     for item in data['schoolLocations']['edges']:
    #         if not item['node']['displayPublic']:
    #             non_public_found = True

    #     # Assert non public locations are listed
    #     self.assertEqual(non_public_found, True)


    # def test_query_anon_user(self):
    #     """ Query list of locations """
    #     query = self.locations_query
    #     location = f.SchoolLocationFactory.create()
    #     variables = {
    #         'archived': False
    #     }

    #     executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one(self):
    #     """ Query one location """   
    #     location = f.SchoolLocationFactory.create()

    #     # First query locations to get node id easily
    #     node_id = self.get_node_id_of_first_location()

    #     # Now query single location and check
    #     query = self.location_query
    #     executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['schoolLocation']['name'], location.name)
    #     self.assertEqual(data['schoolLocation']['archived'], location.archived)
    #     self.assertEqual(data['schoolLocation']['displayPublic'], location.display_public)


    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one location """   
    #     location = f.SchoolLocationFactory.create()

    #     # First query locations to get node id easily
    #     node_id = self.get_node_id_of_first_location()

    #     # Now query single location and check
    #     query = self.location_query
    #     executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     location = f.SchoolLocationFactory.create()

    #     # First query locations to get node id easily
    #     node_id = self.get_node_id_of_first_location()

    #     # Now query single location and check
    #     query = self.location_query
    #     executed = execute_test_client_api_query(query, user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_schoollocation')
    #     user.user_permissions.add(permission)
    #     user.save()
    #     location = f.SchoolLocationFactory.create()

    #     # First query locations to get node id easily
    #     node_id = self.get_node_id_of_first_location()

    #     # Now query single location and check   
    #     query = self.location_query
    #     executed = execute_test_client_api_query(query, user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['schoolLocation']['name'], location.name)


    # def test_create_location(self):
    #     """ Create a location """
    #     query = self.location_create_mutation

    #     variables = {
    #         "input": {
    #             "name": "New location",
    #             "displayPublic": True
    #         }
    #     }

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createSchoolLocation']['schoolLocation']['name'], variables['input']['name'])
    #     self.assertEqual(data['createSchoolLocation']['schoolLocation']['archived'], False)
    #     self.assertEqual(data['createSchoolLocation']['schoolLocation']['displayPublic'], variables['input']['displayPublic'])


    # def test_create_location_anon_user(self):
    #     """ Don't allow creating locations for non-logged in users """
    #     query = self.location_create_mutation

    #     variables = {
    #         "input": {
    #             "name": "New location",
    #             "displayPublic": True
    #         }
    #     }

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_create_location_permission_granted(self):
    #     """ Allow creating locations for users with permissions """
    #     query = self.location_create_mutation

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     variables = {
    #         "input": {
    #             "name": "New location",
    #             "displayPublic": True
    #         }
    #     }

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createSchoolLocation']['schoolLocation']['name'], variables['input']['name'])
    #     self.assertEqual(data['createSchoolLocation']['schoolLocation']['archived'], False)
    #     self.assertEqual(data['createSchoolLocation']['schoolLocation']['displayPublic'], variables['input']['displayPublic'])


    # def test_create_location_permission_denied(self):
    #     """ Check create location permission denied error message """
    #     query = self.location_create_mutation
        
    #     variables = {
    #         "input": {
    #             "name": "New location",
    #             "displayPublic": True
    #         }
    #     }

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


    # def test_update_location(self):
    #     """ Update a location """
    #     query = self.location_update_mutation
    #     location = f.SchoolLocationFactory.create()

    #     variables = {
    #         "input": {
    #             "id": self.get_node_id_of_first_location(),
    #             "name": "Updated name",
    #             "displayPublic": False
    #         }
    #     }

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateSchoolLocation']['schoolLocation']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateSchoolLocation']['schoolLocation']['displayPublic'], variables['input']['displayPublic'])


    # def test_update_location_anon_user(self):
    #     """ Don't allow updating locations for non-logged in users """
    #     query = self.location_update_mutation
    #     location = f.SchoolLocationFactory.create()

    #     variables = {
    #         "input": {
    #             "id": self.get_node_id_of_first_location(),
    #             "name": "Updated name",
    #             "displayPublic": False
    #         }
    #     }

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_location_permission_granted(self):
    #     """ Allow updating locations for users with permissions """
    #     query = self.location_update_mutation

    #     location = f.SchoolLocationFactory.create()
    #     variables = {
    #         "input": {
    #             "id": self.get_node_id_of_first_location(),
    #             "name": "Updated name",
    #             "displayPublic": False
    #         }
    #     }

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
    #     self.assertEqual(data['updateSchoolLocation']['schoolLocation']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateSchoolLocation']['schoolLocation']['displayPublic'], variables['input']['displayPublic'])


    # def test_update_location_permission_denied(self):
    #     """ Check update location permission denied error message """
    #     query = self.location_update_mutation
    #     location = f.SchoolLocationFactory.create()

    #     variables = {
    #         "input": {
    #             "id": self.get_node_id_of_first_location(),
    #             "name": "Updated name",
    #             "displayPublic": False
    #         }
    #     }

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


    # def test_archive_location(self):
    #     """ Archive a location """
    #     query = self.location_archive_mutation
    #     location = f.SchoolLocationFactory.create()

    #     variables = {
    #         "input": {
    #             "id": self.get_node_id_of_first_location(),
    #             "archived": True
    #         }
    #     }

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveSchoolLocation']['schoolLocation']['archived'], variables['input']['archived'])


    # def test_archive_location_anon_user(self):
    #     """ Archive a location """
    #     query = self.location_archive_mutation
    #     location = f.SchoolLocationFactory.create()

    #     variables = {
    #         "input": {
    #             "id": self.get_node_id_of_first_location(),
    #             "archived": True
    #         }
    #     }

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_archive_location_permission_granted(self):
    #     """ Allow archiving locations for users with permissions """
    #     query = self.location_archive_mutation

    #     location = f.SchoolLocationFactory.create()
    #     variables = {
    #         "input": {
    #             "id": self.get_node_id_of_first_location(),
    #             "archived": True
    #         }
    #     }
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
    #     self.assertEqual(data['archiveSchoolLocation']['schoolLocation']['archived'], variables['input']['archived'])


    # def test_archive_location_permission_denied(self):
    #     """ Check archive location permission denied error message """
    #     query = self.location_archive_mutation

    #     location = f.SchoolLocationFactory.create()
    #     variables = {
    #         "input": {
    #             "id": self.get_node_id_of_first_location(),
    #             "archived": True
    #         }
    #     }
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

