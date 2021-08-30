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


class GQLOrganizationLanguage(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationlanguage'
        self.permission_add = 'add_organizationlanguage'
        self.permission_change = 'change_organizationlanguage'
        self.permission_delete = 'delete_organizationlanguage'

        self.variables_create = {
            "input": {
                "name": "New language",
            }
        }
        
        self.variables_update = {
            "input": {
                "name": "Updated language",
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.languages_query = '''
query OrganizationLanguages($after: String, $before: String, $archived: Boolean) {
  organizationLanguages(first: 15, before: $before, after: $after, archived: $archived) {
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
        name
      }
    }
  }
}
'''

        self.language_query = '''
query getOrganizationLanguage($id: ID!) {
    organizationLanguage(id:$id) {
      id
      archived
      name
    }
  }
'''

        self.language_create_mutation = '''
mutation CreateOrganizationLanguage($input: CreateOrganizationLanguageInput!) {
  createOrganizationLanguage(input: $input) {
    organizationLanguage {
      id
      archived
      name
    }
  }
}
'''

        self.language_update_mutation = '''
  mutation UpdateOrganizationLanguage($input: UpdateOrganizationLanguageInput!) {
    updateOrganizationLanguage(input: $input) {
      organizationLanguage {
        id
        archived
        name
      }
    }
  }
'''

        self.language_archive_mutation = '''
mutation ArchiveOrganizationLanguage($input: ArchiveOrganizationLanguageInput!) {
    archiveOrganizationLanguage(input: $input) {
        organizationLanguage {
        id
        archived
        }
    }
}
'''

    def tearDown(self):
        # This is run after every test
        pass

    def get_node_id_of_first_language(self):
        # query languages to get node id easily
        variables = {
            'archived': False
        }
        executed = execute_test_client_api_query(self.languages_query, self.admin_user, variables=variables)
        data = executed.get('data')
        
        return data['organizationLanguages']['edges'][0]['node']['id']

    def test_query(self):
        """ Query list of languages """
        query = self.languages_query
        language = f.OrganizationLanguageFactory.create()
        variables = {
            "archived": False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        item = data['organizationLanguages']['edges'][0]['node']
        self.assertEqual(item['name'], language.name)

    def test_query_permission_denied(self):
        """ Query list of languages as user without permissions (Archived shouldn't be listed) """
        query = self.languages_query
        language = f.OrganizationLanguageFactory.create()
        language.archived = True
        language.save()

        variables = {
            'archived': True
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of languages with view permission """
        query = self.languages_query
        language = f.OrganizationLanguageFactory.create()
        non_public_language = f.OrganizationLanguageFactory.build()
        non_public_language.display_public = False
        non_public_language.save()

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
        item = data['organizationLanguages']['edges'][0]['node']
        self.assertEqual(item['name'], language.name)

    def test_query_anon_user(self):
        """ Query list of languages as anon user - archived shouldn't be visible"""
        query = self.languages_query
        language = f.OrganizationLanguageFactory.create()
        language.archived = True
        language.save()

        variables = {
            'archived': True
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one language """   
        language = f.OrganizationLanguageFactory.create()

        # First query languages to get node id easily
        node_id = self.get_node_id_of_first_language()

        # Now query single language and check
        query = self.language_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLanguage']['name'], language.name)
        self.assertEqual(data['organizationLanguage']['archived'], language.archived)

    def test_query_one_anon_user(self):
        """ Deny permission to view archived languages for anon users Query one language """
        query = self.language_query
        language = f.OrganizationLanguageFactory.create()
        language.archived = True
        language.save()
        node_id = to_global_id("OrganizationLanguageNode", language.id)
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLanguage'], None)

    def test_query_one_archived_without_permission(self):
        """ None returned when user lacks authorization to view archived languages """
        query = self.language_query
        
        user = f.RegularUserFactory.create()
        language = f.OrganizationLanguageFactory.create()
        language.archived = True
        language.save()
        node_id = to_global_id("OrganizationLanguageNode", language.id)

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLanguage'], None)

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        query = self.language_query
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationlanguage')
        user.user_permissions.add(permission)
        user.save()

        language = f.OrganizationLanguageFactory.create()
        node_id = self.get_node_id_of_first_language()

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLanguage']['name'], language.name)

    def test_create_language(self):
        """ Create a language """
        query = self.language_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationLanguage']['organizationLanguage']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationLanguage']['organizationLanguage']['archived'], False)


    def test_create_language_anon_user(self):
        """ Create a language with anonymous user, check error message """
        query = self.language_create_mutation

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_language_permission_granted(self):
        """ Create a language with a user having the add permission """
        query = self.language_create_mutation
        variables = self.variables_create

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
        self.assertEqual(data['createOrganizationLanguage']['organizationLanguage']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationLanguage']['organizationLanguage']['archived'], False)


    def test_create_language_permission_denied(self):
        """ Create a language with a user not having the add permission """
        query = self.language_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_update_language(self):
        """ Update a language as admin user """
        query = self.language_update_mutation
        language = f.OrganizationLanguageFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_language()


        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganizationLanguage']['organizationLanguage']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationLanguage']['organizationLanguage']['archived'], False)


    def test_update_language_anon_user(self):
        """ Update a language as anonymous user """
        query = self.language_update_mutation
        language = f.OrganizationLanguageFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_language()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_language_permission_granted(self):
        """ Update a language as user with permission """
        query = self.language_update_mutation
        language = f.OrganizationLanguageFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_language()

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
        self.assertEqual(data['updateOrganizationLanguage']['organizationLanguage']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationLanguage']['organizationLanguage']['archived'], False)


    def test_update_language_permission_denied(self):
        """ Update a language as user without permissions """
        query = self.language_update_mutation
        language = f.OrganizationLanguageFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_language()

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_archive_language(self):
        """ Archive a language """
        query = self.language_archive_mutation
        language = f.OrganizationLanguageFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_language()

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationLanguage']['organizationLanguage']['archived'], variables['input']['archived'])


    def test_archive_language_anon_user(self):
        """ Archive a language """
        query = self.language_archive_mutation
        language = f.OrganizationLanguageFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_language()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_language_permission_granted(self):
        """ Allow archiving languages for users with permissions """
        query = self.language_archive_mutation
        language = f.OrganizationLanguageFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_language()

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
        self.assertEqual(data['archiveOrganizationLanguage']['organizationLanguage']['archived'], variables['input']['archived'])


    def test_archive_language_permission_denied(self):
        """ Check archive language permission denied error message """
        query = self.language_archive_mutation
        language = f.OrganizationLanguageFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_language()

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


