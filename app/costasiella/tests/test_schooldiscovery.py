# from graphql.error.located_error import GraphQLLocatedError
import graphql

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models


class GQLSchoolDiscovery(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_schoolclasstype'
        self.permission_add = 'add_schoolclasstype'
        self.permission_change = 'change_schoolclasstype'
        self.permission_delete = 'delete_schoolclasstype'
        

        self.classtypes_query = '''
query SchoolClasstypes($after: String, $before: String, $archived: Boolean) {
  schoolClasstypes(first: 15, before: $before, after: $after, archived: $archived) {
    pageInfo {
      startCursor
      endCursor
      hasNextPage
      hasPreviousPage
    }
    edges {
      node {
        id
        archived
        displayPublic
        name
        description
        urlWebsite
      }
    }
  }
}
'''

        self.classtype_query = '''
query getSchoolClasstype($id: ID!) {
    schoolClasstype(id:$id) {
      id
      archived
      name
      description
      displayPublic
      urlWebsite
    }
  }
'''

        self.classtype_create_mutation = '''
mutation CreateSchoolClasstype($input: CreateSchoolClasstypeInput!) {
  createSchoolClasstype(input: $input) {
    schoolClasstype {
      id
      archived
      name
      description
      displayPublic
      urlWebsite
    }
  }
}
'''

        self.classtype_update_mutation = '''
  mutation UpdateSchoolClasstype($input: UpdateSchoolClasstypeInput!) {
    updateSchoolClasstype(input: $input) {
      schoolClasstype {
        id
        archived
        name
        description
        displayPublic
        urlWebsite
      }
    }
  }
'''

        self.classtype_archive_mutation = '''
mutation ArchiveSchoolClasstype($input: ArchiveSchoolClasstypeInput!) {
    archiveSchoolClasstype(input: $input) {
        schoolClasstype {
        id
        archived
        }
    }
}
'''

    def tearDown(self):
        # This is run after every test
        pass


    def get_node_id_of_first_classtype(self):
        # query classtypes to get node id easily
        variables = {
            'archived': False
        }
        executed = execute_test_client_api_query(self.classtypes_query, self.admin_user, variables=variables)
        data = executed.get('data')
        
        return data['schoolClasstypes']['edges'][0]['node']['id']

    def test_query(self):
        """ Query list of classtypes """
        query = self.classtypes_query
        classtype = f.SchoolClasstypeFactory.create()
        variables = {
            "archived": False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        item = data['schoolClasstypes']['edges'][0]['node']
        self.assertEqual(item['name'], classtype.name)
        self.assertEqual(item['archived'], classtype.archived)
        self.assertEqual(item['description'], classtype.description)
        self.assertEqual(item['displayPublic'], classtype.display_public)


    def test_query_permision_denied(self):
        """ Query list of classtypes as user without permissions """
        query = self.classtypes_query
        classtype = f.SchoolClasstypeFactory.create()
        non_public_classtype = f.SchoolClasstypeFactory.build()
        non_public_classtype.display_public = False
        non_public_classtype.save()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # Public classtypes only
        non_public_found = False
        for item in data['schoolClasstypes']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)


    def test_query_permision_granted(self):
        """ Query list of classtypes with view permission """
        query = self.classtypes_query
        classtype = f.SchoolClasstypeFactory.create()
        non_public_classtype = f.SchoolClasstypeFactory.build()
        non_public_classtype.display_public = False
        non_public_classtype.save()

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

        # List all classtypes, including non public
        non_public_found = False
        for item in data['schoolClasstypes']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        # Assert non public classtypes are listed
        self.assertEqual(non_public_found, True)


    def test_query_anon_user(self):
        """ Query list of classtypes as anon user """
        query = self.classtypes_query
        classtype = f.SchoolClasstypeFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one classtype """   
        classtype = f.SchoolClasstypeFactory.create()

        # First query classtypes to get node id easily
        node_id = self.get_node_id_of_first_classtype()

        # Now query single classtype and check
        query = self.classtype_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        print(data)
        self.assertEqual(data['schoolClasstype']['name'], classtype.name)
        self.assertEqual(data['schoolClasstype']['archived'], classtype.archived)
        self.assertEqual(data['schoolClasstype']['description'], classtype.description)
        self.assertEqual(data['schoolClasstype']['displayPublic'], classtype.display_public)
        self.assertEqual(data['schoolClasstype']['urlWebsite'], classtype.url_website)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one classtype """   
        query = self.classtype_query
        classtype = f.SchoolClasstypeFactory.create()
        node_id = self.get_node_id_of_first_classtype()
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        query = self.classtype_query
        
        user = f.RegularUserFactory.create()
        classtype = f.SchoolClasstypeFactory.create()
        node_id = self.get_node_id_of_first_classtype()

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        query = self.classtype_query
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_schoolclasstype')
        user.user_permissions.add(permission)
        user.save()

        classtype = f.SchoolClasstypeFactory.create()
        node_id = self.get_node_id_of_first_classtype()

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['schoolClasstype']['name'], classtype.name)


    def test_create_classtype(self):
        """ Create a classtype """
        query = self.classtype_create_mutation

        variables = {
            "input": {
                "name": "New classtype",
                "description": "Classtype description",
                "displayPublic": True,
                "urlWebsite": "https://www.costasiella.com"
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['name'], variables['input']['name'])
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['archived'], False)
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['description'], variables['input']['description'])
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['urlWebsite'], variables['input']['urlWebsite'])


    def test_create_classtype_anon_user(self):
        """ Create a classtype with anonymous user, check error message """
        query = self.classtype_create_mutation

        variables = {
            "input": {
                "name": "New classtype",
                "description": "Classtype description",
                "displayPublic": True,
                "urlWebsite": "https://www.costasiella.com"
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


    def test_create_classtype_permission_granted(self):
        """ Create a classtype with a user having the add permission """
        query = self.classtype_create_mutation

        variables = {
            "input": {
                "name": "New classtype",
                "description": "Classtype description",
                "displayPublic": True,
                "urlWebsite": "https://www.costasiella.com"
            }
        }

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
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['name'], variables['input']['name'])
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['archived'], False)
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['description'], variables['input']['description'])
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['urlWebsite'], variables['input']['urlWebsite'])


    def test_create_classtype_permission_denied(self):
        """ Create a classtype with a user not having the add permission """
        query = self.classtype_create_mutation

        variables = {
            "input": {
                "name": "New classtype",
                "description": "Classtype description",
                "displayPublic": True,
                "urlWebsite": "https://www.costasiella.com"
            }
        }

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_update_classtype(self):
        """ Update a classtype as admin user """
        query = self.classtype_update_mutation
        classtype = f.SchoolClasstypeFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_classtype(),
                "name": "New classtype",
                "description": "Classtype description",
                "displayPublic": True,
                "urlWebsite": "https://www.costasiella.com"
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateSchoolClasstype']['schoolClasstype']['name'], variables['input']['name'])
        self.assertEqual(data['updateSchoolClasstype']['schoolClasstype']['archived'], False)
        self.assertEqual(data['updateSchoolClasstype']['schoolClasstype']['description'], variables['input']['description'])
        self.assertEqual(data['updateSchoolClasstype']['schoolClasstype']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['updateSchoolClasstype']['schoolClasstype']['urlWebsite'], variables['input']['urlWebsite'])


    def test_update_classtype_anon_user(self):
        """ Update a classtype as anonymous user """
        query = self.classtype_update_mutation
        classtype = f.SchoolClasstypeFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_classtype(),
                "name": "New classtype",
                "description": "Classtype description",
                "displayPublic": True,
                "urlWebsite": "https://www.costasiella.com"
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


    def test_update_classtype_permission_granted(self):
        """ Update a classtype as user with permission """
        query = self.classtype_update_mutation
        classtype = f.SchoolClasstypeFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_classtype(),
                "name": "New classtype",
                "description": "Classtype description",
                "displayPublic": True,
                "urlWebsite": "https://www.costasiella.com"
            }
        }

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
        self.assertEqual(data['updateSchoolClasstype']['schoolClasstype']['name'], variables['input']['name'])
        self.assertEqual(data['updateSchoolClasstype']['schoolClasstype']['archived'], False)
        self.assertEqual(data['updateSchoolClasstype']['schoolClasstype']['description'], variables['input']['description'])
        self.assertEqual(data['updateSchoolClasstype']['schoolClasstype']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['updateSchoolClasstype']['schoolClasstype']['urlWebsite'], variables['input']['urlWebsite'])


    def test_update_classtype_permission_denied(self):
        """ Update a classtype as user without permissions """
        query = self.classtype_update_mutation
        classtype = f.SchoolClasstypeFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_classtype(),
                "name": "New classtype",
                "description": "Classtype description",
                "displayPublic": True,
                "urlWebsite": "https://www.costasiella.com"
            }
        }

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_archive_classtype(self):
        """ Archive a classtype """
        query = self.classtype_archive_mutation
        classtype = f.SchoolClasstypeFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_classtype(),
                "archived": True
            }
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveSchoolClasstype']['schoolClasstype']['archived'], variables['input']['archived'])


    def test_archive_classtype_anon_user(self):
        """ Archive a classtype """
        query = self.classtype_archive_mutation
        classtype = f.SchoolClasstypeFactory.create()

        variables = {
            "input": {
                "id": self.get_node_id_of_first_classtype(),
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


    def test_archive_classtype_permission_granted(self):
        """ Allow archiving classtypes for users with permissions """
        query = self.classtype_archive_mutation

        classtype = f.SchoolClasstypeFactory.create()
        variables = {
            "input": {
                "id": self.get_node_id_of_first_classtype(),
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
        self.assertEqual(data['archiveSchoolClasstype']['schoolClasstype']['archived'], variables['input']['archived'])


    def test_archive_classtype_permission_denied(self):
        """ Check archive classtype permission denied error message """
        query = self.classtype_archive_mutation

        classtype = f.SchoolClasstypeFactory.create()
        variables = {
            "input": {
                "id": self.get_node_id_of_first_classtype(),
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


