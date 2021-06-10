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


class GQLOrganizationClasstype(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationclasstype'
        self.permission_add = 'add_organizationclasstype'
        self.permission_change = 'change_organizationclasstype'
        self.permission_delete = 'delete_organizationclasstype'

        self.classtypes_query = '''
query OrganizationClasstypes($after: String, $before: String, $archived: Boolean) {
  organizationClasstypes(first: 15, before: $before, after: $after, archived: $archived) {
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
query getOrganizationClasstype($id: ID!) {
    organizationClasstype(id:$id) {
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
mutation CreateOrganizationClasstype($input: CreateOrganizationClasstypeInput!) {
  createOrganizationClasstype(input: $input) {
    organizationClasstype {
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
  mutation UpdateOrganizationClasstype($input: UpdateOrganizationClasstypeInput!) {
    updateOrganizationClasstype(input: $input) {
      organizationClasstype {
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
mutation ArchiveOrganizationClasstype($input: ArchiveOrganizationClasstypeInput!) {
    archiveOrganizationClasstype(input: $input) {
        organizationClasstype {
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
        
        return data['organizationClasstypes']['edges'][0]['node']['id']

    def test_query(self):
        """ Query list of classtypes """
        query = self.classtypes_query
        classtype = f.OrganizationClasstypeFactory.create()
        variables = {
            "archived": False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        item = data['organizationClasstypes']['edges'][0]['node']
        self.assertEqual(item['name'], classtype.name)
        self.assertEqual(item['archived'], classtype.archived)
        self.assertEqual(item['description'], classtype.description)
        self.assertEqual(item['displayPublic'], classtype.display_public)


    def test_query_permission_denied(self):
        """ Query list of classtypes as user without permissions """
        query = self.classtypes_query
        classtype = f.OrganizationClasstypeFactory.create()
        non_public_classtype = f.OrganizationClasstypeFactory.build()
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
        for item in data['organizationClasstypes']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)

    def test_query_permission_granted(self):
        """ Query list of classtypes with view permission """
        query = self.classtypes_query
        classtype = f.OrganizationClasstypeFactory.create()
        non_public_classtype = f.OrganizationClasstypeFactory.build()
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
        for item in data['organizationClasstypes']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        # Assert non public classtypes are listed
        self.assertEqual(non_public_found, True)

    def test_query_anon_user_dont_list_archived(self):
        """ Query list of classtypes as anon user """
        query = self.classtypes_query
        classtype = f.OrganizationClasstypeFactory.create()
        classtype.archived = True
        classtype.save()

        variables = {
            'archived': True
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(len(data['organizationClasstypes']['edges']), 0)

    def test_query_anon_user_list_public_and_not_archived(self):
        """ Query list of classtypes as anon user """
        query = self.classtypes_query
        classtype = f.OrganizationClasstypeFactory.create()

        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        data = executed.get('data')

        item = data['organizationClasstypes']['edges'][0]['node']
        self.assertEqual(item['name'], classtype.name)

    def test_query_one(self):
        """ Query one classtype """   
        classtype = f.OrganizationClasstypeFactory.create()

        # First query classtypes to get node id easily
        node_id = self.get_node_id_of_first_classtype()

        # Now query single classtype and check
        query = self.classtype_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationClasstype']['name'], classtype.name)
        self.assertEqual(data['organizationClasstype']['archived'], classtype.archived)
        self.assertEqual(data['organizationClasstype']['description'], classtype.description)
        self.assertEqual(data['organizationClasstype']['displayPublic'], classtype.display_public)
        self.assertEqual(data['organizationClasstype']['urlWebsite'], classtype.url_website)

    def test_query_one_anon_user_allow_current_and_public(self):
        """ Allow permission for anon users Query one classtype """
        query = self.classtype_query
        classtype = f.OrganizationClasstypeFactory.create()
        node_id = self.get_node_id_of_first_classtype()
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        data = executed.get('data')

        self.assertEqual(data['organizationClasstype']['name'], classtype.name)

    def test_query_one_anon_user_dont_list_archived_or_non_public(self):
        """ Deny permission for anon users Query one classtype """
        query = self.classtype_query
        classtype = f.OrganizationClasstypeFactory.create()
        classtype.archived = True
        classtype.save()
        node_id = to_global_id('OrganizationClasstypeNode', classtype.id)
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        data = executed.get('data')

        self.assertEqual(data['organizationClasstype'], None)

    def test_query_one_no_permission_display_public_and_current(self):
        """ Only list public and current when user lacks authorization """
        query = self.classtype_query
        
        user = f.RegularUserFactory.create()
        classtype = f.OrganizationClasstypeFactory.create()
        node_id = to_global_id('OrganizationClasstypeNode', classtype.id)

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')

        self.assertEqual(data['organizationClasstype']['name'], classtype.name)

    def test_query_one_no_permission_dont_list_archived(self):
        """ Only list public and current when user lacks authorization """
        query = self.classtype_query

        user = f.RegularUserFactory.create()
        classtype = f.OrganizationClasstypeFactory.create()
        classtype.archived = True
        classtype.save()
        node_id = to_global_id('OrganizationClasstypeNode', classtype.id)

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')

        self.assertEqual(data['organizationClasstype'], None)

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        query = self.classtype_query
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationclasstype')
        user.user_permissions.add(permission)
        user.save()

        classtype = f.OrganizationClasstypeFactory.create()
        node_id = self.get_node_id_of_first_classtype()

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationClasstype']['name'], classtype.name)


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
        self.assertEqual(data['createOrganizationClasstype']['organizationClasstype']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationClasstype']['organizationClasstype']['archived'], False)
        self.assertEqual(data['createOrganizationClasstype']['organizationClasstype']['description'], variables['input']['description'])
        self.assertEqual(data['createOrganizationClasstype']['organizationClasstype']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['createOrganizationClasstype']['organizationClasstype']['urlWebsite'], variables['input']['urlWebsite'])


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
        self.assertEqual(data['createOrganizationClasstype']['organizationClasstype']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationClasstype']['organizationClasstype']['archived'], False)
        self.assertEqual(data['createOrganizationClasstype']['organizationClasstype']['description'], variables['input']['description'])
        self.assertEqual(data['createOrganizationClasstype']['organizationClasstype']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['createOrganizationClasstype']['organizationClasstype']['urlWebsite'], variables['input']['urlWebsite'])


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
        classtype = f.OrganizationClasstypeFactory.create()

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
        self.assertEqual(data['updateOrganizationClasstype']['organizationClasstype']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationClasstype']['organizationClasstype']['archived'], False)
        self.assertEqual(data['updateOrganizationClasstype']['organizationClasstype']['description'], variables['input']['description'])
        self.assertEqual(data['updateOrganizationClasstype']['organizationClasstype']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['updateOrganizationClasstype']['organizationClasstype']['urlWebsite'], variables['input']['urlWebsite'])


    def test_update_classtype_anon_user(self):
        """ Update a classtype as anonymous user """
        query = self.classtype_update_mutation
        classtype = f.OrganizationClasstypeFactory.create()

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
        classtype = f.OrganizationClasstypeFactory.create()

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
        self.assertEqual(data['updateOrganizationClasstype']['organizationClasstype']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationClasstype']['organizationClasstype']['archived'], False)
        self.assertEqual(data['updateOrganizationClasstype']['organizationClasstype']['description'], variables['input']['description'])
        self.assertEqual(data['updateOrganizationClasstype']['organizationClasstype']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['updateOrganizationClasstype']['organizationClasstype']['urlWebsite'], variables['input']['urlWebsite'])


    def test_update_classtype_permission_denied(self):
        """ Update a classtype as user without permissions """
        query = self.classtype_update_mutation
        classtype = f.OrganizationClasstypeFactory.create()

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
        classtype = f.OrganizationClasstypeFactory.create()

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
        self.assertEqual(data['archiveOrganizationClasstype']['organizationClasstype']['archived'], variables['input']['archived'])


    def test_archive_classtype_anon_user(self):
        """ Archive a classtype """
        query = self.classtype_archive_mutation
        classtype = f.OrganizationClasstypeFactory.create()

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

        classtype = f.OrganizationClasstypeFactory.create()
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
        self.assertEqual(data['archiveOrganizationClasstype']['organizationClasstype']['archived'], variables['input']['archived'])


    def test_archive_classtype_permission_denied(self):
        """ Check archive classtype permission denied error message """
        query = self.classtype_archive_mutation

        classtype = f.OrganizationClasstypeFactory.create()
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


