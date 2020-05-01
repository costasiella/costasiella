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
from ..modules.gql_tools import get_rid
from .. import models
from .. import schema




class GQLOrganizationAppointmentCategory(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationappointmentcategory'
        self.permission_add = 'add_organizationappointmentcategory'
        self.permission_change = 'change_organizationappointmentcategory'
        self.permission_delete = 'delete_organizationappointmentcategory'

        self.appointment_categories_query = '''
  query OrganizationAppointmentCategories($after: String, $before: String, $archived: Boolean) {
    organizationAppointmentCategories(first: 15, before: $before, after: $after, archived: $archived) {
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
          displayPublic,
          name
        }
      }
    }
  }
'''

        self.appointment_category_query = '''
query getOrganizationAppointmentCategory($id: ID!) {
    organizationAppointmentCategory(id:$id) {
      id
      name
      displayPublic
      archived
    }
  }
'''

        self.appointment_category_create_mutation = ''' 
  mutation CreateOrganizationAppointmentCategory($input: CreateOrganizationAppointmentCategoryInput!) {
    createOrganizationAppointmentCategory(input: $input) {
      organizationAppointmentCategory {
        id
        archived
        displayPublic
        name
      }
    }
  }
'''

        self.appointment_category_update_mutation = '''
  mutation UpdateOrganizationAppointmentCategory($input: UpdateOrganizationAppointmentCategoryInput!) {
    updateOrganizationAppointmentCategory(input: $input) {
      organizationAppointmentCategory {
        id
        name
        displayPublic
      }
    }
  }
'''

        self.appointment_category_archive_mutation = '''
  mutation ArchiveOrganizationAppointmentCategory($input: ArchiveOrganizationAppointmentCategoryInput!) {
    archiveOrganizationAppointmentCategory(input: $input) {
      organizationAppointmentCategory {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def get_node_id_of_first_appointment_category(self):
        # query appointment_categories to get node id easily
        variables = {
            'archived': False
        }
        executed = execute_test_client_api_query(self.appointment_categories_query, self.admin_user, variables=variables)
        data = executed.get('data')
        
        return data['organizationAppointmentCategories']['edges'][0]['node']['id']


    def test_query(self):
        """ Query list of appointment_categories """
        query = self.appointment_categories_query
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['organizationAppointmentCategories']['edges'][0]['node']['name'], appointment_category.name)
        self.assertEqual(data['organizationAppointmentCategories']['edges'][0]['node']['archived'], appointment_category.archived)
        self.assertEqual(data['organizationAppointmentCategories']['edges'][0]['node']['displayPublic'], appointment_category.display_public)


    def test_query_permission_denied(self):
        """ Query list of appointment_categories """
        query = self.appointment_categories_query
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()
        non_public_appointment_category = f.OrganizationAppointmentCategoryFactory.build()
        non_public_appointment_category.display_public = False
        non_public_appointment_category.save()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # Public appointment_categories only
        non_public_found = False
        for item in data['organizationAppointmentCategories']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)


    def test_query_permission_granted(self):
        """ Query list of appointment_categories """
        query = self.appointment_categories_query
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()
        non_public_appointment_category = f.OrganizationAppointmentCategoryFactory.build()
        non_public_appointment_category.display_public = False
        non_public_appointment_category.save()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all appointment_categories, including non public
        non_public_found = False
        for item in data['organizationAppointmentCategories']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        # Assert non public appointment_categories are listed
        self.assertEqual(non_public_found, True)


    def test_query_anon_user(self):
        """ Query list of appointment_categories """
        query = self.appointment_categories_query
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one appointment_category """   
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()

        # First query appointment_categories to get node id easily
        node_id = self.get_node_id_of_first_appointment_category()

        # Now query single appointment_category and check
        query = self.appointment_category_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationAppointmentCategory']['name'], appointment_category.name)
        self.assertEqual(data['organizationAppointmentCategory']['archived'], appointment_category.archived)
        self.assertEqual(data['organizationAppointmentCategory']['displayPublic'], appointment_category.display_public)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one appointment_category """   
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()

        # First query appointment_categories to get node id easily
        node_id = self.get_node_id_of_first_appointment_category()

        # Now query single appointment_category and check
        query = self.appointment_category_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()

        # First query appointment_categories to get node id easily
        node_id = self.get_node_id_of_first_appointment_category()

        # Now query single appointment_category and check
        query = self.appointment_category_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()

        # First query appointment_categories to get node id easily
        node_id = self.get_node_id_of_first_appointment_category()

        # Now query single appointment_category and check   
        query = self.appointment_category_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationAppointmentCategory']['name'], appointment_category.name)


    def test_create_appointment_category(self):
        """ Create a appointment_category """
        query = self.appointment_category_create_mutation

        variables = {
            "input": {
                "name": "New appointment_category",
                "displayPublic": True
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationAppointmentCategory']['organizationAppointmentCategory']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationAppointmentCategory']['organizationAppointmentCategory']['archived'], False)
        self.assertEqual(data['createOrganizationAppointmentCategory']['organizationAppointmentCategory']['displayPublic'], variables['input']['displayPublic'])


    def test_create_appointment_category_anon_user(self):
        """ Don't allow creating appointment_categories for non-logged in users """
        query = self.appointment_category_create_mutation

        variables = {
            "input": {
                "name": "New appointment_category",
                "displayPublic": True
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_appointment_category_permission_granted(self):
        """ Allow creating appointment_categories for users with permissions """
        query = self.appointment_category_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        variables = {
            "input": {
                "name": "New appointment_category",
                "displayPublic": True
            }
        }

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationAppointmentCategory']['organizationAppointmentCategory']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationAppointmentCategory']['organizationAppointmentCategory']['archived'], False)
        self.assertEqual(data['createOrganizationAppointmentCategory']['organizationAppointmentCategory']['displayPublic'], variables['input']['displayPublic'])


    def test_create_appointment_category_permission_denied(self):
        """ Check create appointment_category permission denied error message """
        query = self.appointment_category_create_mutation
        
        variables = {
            "input": {
                "name": "New appointment_category",
                "displayPublic": True
            }
        }

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


    def test_update_appointment_category(self):
        """ Update a appointment_category """
        query = self.appointment_category_update_mutation
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_appointment_category(),
                "name": "Updated name",
                "displayPublic": False
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganizationAppointmentCategory']['organizationAppointmentCategory']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationAppointmentCategory']['organizationAppointmentCategory']['displayPublic'], variables['input']['displayPublic'])


    def test_update_appointment_category_anon_user(self):
        """ Don't allow updating appointment_categories for non-logged in users """
        query = self.appointment_category_update_mutation
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_appointment_category(),
                "name": "Updated name",
                "displayPublic": False
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_appointment_category_permission_granted(self):
        """ Allow updating appointment_categories for users with permissions """
        query = self.appointment_category_update_mutation

        appointment_category = f.OrganizationAppointmentCategoryFactory.create()
        variables = {
            "input": {
                "id": self.get_node_id_of_first_appointment_category(),
                "name": "Updated name",
                "displayPublic": False
            }
        }

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
        self.assertEqual(data['updateOrganizationAppointmentCategory']['organizationAppointmentCategory']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationAppointmentCategory']['organizationAppointmentCategory']['displayPublic'], variables['input']['displayPublic'])


    def test_update_appointment_category_permission_denied(self):
        """ Check update appointment_category permission denied error message """
        query = self.appointment_category_update_mutation
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_appointment_category(),
                "name": "Updated name",
                "displayPublic": False
            }
        }

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


    def test_archive_appointment_category(self):
        """ Archive a appointment_category """
        query = self.appointment_category_archive_mutation
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_appointment_category(),
                "archived": True
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationAppointmentCategory']['organizationAppointmentCategory']['archived'], variables['input']['archived'])


    def test_archive_appointment_category_anon_user(self):
        """ Archive a appointment_category """
        query = self.appointment_category_archive_mutation
        appointment_category = f.OrganizationAppointmentCategoryFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_appointment_category(),
                "archived": True
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_appointment_category_permission_granted(self):
        """ Allow archiving appointment_categories for users with permissions """
        query = self.appointment_category_archive_mutation

        appointment_category = f.OrganizationAppointmentCategoryFactory.create()
        variables = {
            "input": {
                "id": self.get_node_id_of_first_appointment_category(),
                "archived": True
            }
        }
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
        self.assertEqual(data['archiveOrganizationAppointmentCategory']['organizationAppointmentCategory']['archived'], variables['input']['archived'])


    def test_archive_appointment_category_permission_denied(self):
        """ Check archive appointment_category permission denied error message """
        query = self.appointment_category_archive_mutation

        appointment_category = f.OrganizationAppointmentCategoryFactory.create()
        variables = {
            "input": {
                "id": self.get_node_id_of_first_appointment_category(),
                "archived": True
            }
        }
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

