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


class GQLSchoolClasstype(TestCase):
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
query SchoolClasstypes($archived: Boolean!) {
  schoolClasstypes(archived: $archived) {
    id
    name
    archived
    displayPublic
    description
  }
}
        '''

        self.classtype_create_mutation = '''
mutation CreateSchoolClasstype($name: String!, $description:String, $displayPublic: Boolean!, $link:String) {
  createSchoolClasstype(name: $name, description: $description, displayPublic: $displayPublic, link:$link) {
    schoolClasstype {
      id
      archived
      name
      description
      displayPublic
      link
    }
  }
}
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of classtypes """
        query = self.classtypes_query
        classtype = f.SchoolClasstypeFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['schoolClasstypes'][0]['name'], classtype.name)
        self.assertEqual(data['schoolClasstypes'][0]['archived'], classtype.archived)
        self.assertEqual(data['schoolClasstypes'][0]['description'], classtype.description)
        self.assertEqual(data['schoolClasstypes'][0]['displayPublic'], classtype.display_public)


    def test_query_permision_denied(self):
        """ Query list of classtypes """
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
        for l in data['schoolClasstypes']:
            if not l['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)


    def test_query_permision_granted(self):
        """ Query list of classtypes """
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

        # List all locations, including non public
        non_public_found = False
        for l in data['schoolClasstypes']:
            if not l['displayPublic']:
                non_public_found = True

        # Assert non public locations are listed
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


#     def test_query_one(self):
#         """ Query one location """   
#         query = '''
# query getSchoolLocation($id: ID!) {
#     schoolLocation(id:$id) {
#       id
#       name
#       displayPublic
#       archived
#     }
#   }
#         '''
#         location = SchoolLocationFactory.create()
#         executed = execute_test_client_api_query(query, self.admin_user, variables={"id": location.id})
#         data = executed.get('data')
#         self.assertEqual(data['schoolLocation']['name'], location.name)
#         self.assertEqual(data['schoolLocation']['archived'], location.archived)
#         self.assertEqual(data['schoolLocation']['displayPublic'], location.display_public)


#     def test_query_one_anon_user(self):
#         """ Deny permission for anon users Query one location """   
#         query = '''
# query getSchoolLocation($id: ID!) {
#     schoolLocation(id:$id) {
#       id
#       name
#       displayPublic
#       archived
#     }
#   }
#         '''
#         location = SchoolLocationFactory.create()
#         executed = execute_test_client_api_query(query, self.anon_user, variables={"id": location.id})
#         errors = executed.get('errors')
#         self.assertEqual(errors[0]['message'], 'Not logged in!')


#     def test_query_one_permission_denied(self):
#         """ Permission denied message when user lacks authorization """   
#         query = '''
# query getSchoolLocation($id: ID!) {
#     schoolLocation(id:$id) {
#       id
#       name
#       displayPublic
#       archived
#     }
#   }
#         '''
#         # Create regular user
#         user = RegularUserFactory.create()
#         location = SchoolLocationFactory.create()

#         executed = execute_test_client_api_query(query, user, variables={"id": location.id})
#         errors = executed.get('errors')
#         self.assertEqual(errors[0]['message'], 'Permission denied!')


#     def test_query_one_permission_granted(self):
#         """ Respond with data when user has permission """   
#         query = '''
# query getSchoolLocation($id: ID!) {
#     schoolLocation(id:$id) {
#       id
#       name
#       displayPublic
#       archived
#     }
#   }
#         '''
#         # Create regular user
#         user = RegularUserFactory.create()
#         permission = Permission.objects.get(codename='view_schoollocation')
#         user.user_permissions.add(permission)
#         user.save()

#         location = SchoolLocationFactory.create()

#         executed = execute_test_client_api_query(query, user, variables={"id": location.id})
#         data = executed.get('data')
#         self.assertEqual(data['schoolLocation']['name'], location.name)


    def test_create_classtype(self):
        """ Create a classtype """
        query = self.classtype_create_mutation

        variables = {
            "name": "New location",
            "description": "Classtype description",
            "displayPublic": True,
            "link": "https://www.costasiella.com"
        }

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['name'], variables['name'])
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['archived'], False)
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['description'], variables['description'])
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['displayPublic'], variables['displayPublic'])
        self.assertEqual(data['createSchoolClasstype']['schoolClasstype']['link'], variables['link'])


    def test_create_classtype_anon_user(self):
        """ Create a classtype with anonymous user, check error message """
        query = self.classtype_create_mutation

        variables = {
            "name": "New location",
            "description": "Classtype description",
            "displayPublic": True,
            "link": "https://www.costasiella.com"
        }

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

#     def test_update_location(self):
#         """ Update a location """
#         query = '''
# mutation UpdateSchoolLocation($id: ID!, $name: String!, $displayPublic:Boolean!) {
#     updateSchoolLocation(id: $id, name: $name, displayPublic: $displayPublic) {
#         schoolLocation {
#         id
#         archived
#         name
#         displayPublic
#         }
#     }
# }
#         '''
#         location = SchoolLocationFactory.create()

#         variables = {
#             "id": location.id,
#             "name": "Updated name",
#             "displayPublic": False
#         }

#         executed = execute_test_client_api_query(
#             query, 
#             self.admin_user, 
#             variables=variables
#         )
#         data = executed.get('data')
#         self.assertEqual(data['updateSchoolLocation']['schoolLocation']['name'], variables['name'])
#         self.assertEqual(data['updateSchoolLocation']['schoolLocation']['archived'], False)
#         self.assertEqual(data['updateSchoolLocation']['schoolLocation']['displayPublic'], variables['displayPublic'])


#     def test_archive_location(self):
#         """ Archive a location """
#         query = '''
# mutation ArchiveSchoolLocation($id: ID!, $archived: Boolean!) {
#     archiveSchoolLocation(id: $id, archived: $archived) {
#         schoolLocation {
#         id
#         archived
#         }
#     }
# }
#         '''
#         location = SchoolLocationFactory.create()

#         variables = {
#             "id": location.id,
#             "archived": True
#         }

#         executed = execute_test_client_api_query(
#             query, 
#             self.admin_user, 
#             variables=variables
#         )
#         data = executed.get('data')
#         self.assertEqual(data['archiveSchoolLocation']['schoolLocation']['archived'], variables['archived'])
