# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser, Permission

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema



class GQLAccountInstructorProfile(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountinstructorprofile'
        self.permission_add = 'add_accountinstructorprofile'
        self.permission_change = 'change_accountinstructorprofile'
        self.permission_delete = 'delete_accountinstructorprofile'

        self.variables_update = {
            "input": {
                "classes": False,
                "appointments": False,
                "events": False,
            }
        }

        self.instructor_profiles_query = '''
  query AccountInstructorProfileQuery($id: ID!) {
    accountInstructorProfiles(account:$id) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          account {
            id
          }
          classes
          appointments
          events
          role
          education
          bio
          urlBio
          urlWebsite   
        }
      }
    }
    account(id:$id) {
      id
      instructor
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
'''


        self.instructor_profile_update_mutation = '''
  mutation UpdateAccountInstructorProfile($input:UpdateAccountInstructorProfileInput!) {
    updateAccountInstructorProfile(input: $input) {
      accountInstructorProfile {
        account {
          id
        }
        classes
        appointments
        events
      }
    }
  }
'''


    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of account instructor_profiles """
        query = self.instructor_profiles_query
        instructor_profile = f.InstructorProfileFactory.create()
        variables = {
            'id': to_global_id('AccountNode', instructor_profile.account.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['accountInstructorProfiles']['edges'][0]['node']['account']['id'],
          variables['id']
        )
        self.assertEqual(data['accountInstructorProfiles']['edges'][0]['node']['classes'], instructor_profile.classes)
        self.assertEqual(data['accountInstructorProfiles']['edges'][0]['node']['appointments'], instructor_profile.appointments)
        self.assertEqual(data['accountInstructorProfiles']['edges'][0]['node']['events'], instructor_profile.events)


    def test_query_permission_denied(self):
        """ Query list of account instructor_profiles - check permission denied """
        query = self.instructor_profiles_query
        instructor_profile = f.InstructorProfileFactory.create()
        variables = {
            'id': to_global_id('AccountNode', instructor_profile.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=instructor_profile.account.id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permission_granted(self):
        """ Query list of account instructor_profiles with view permission """
        query = self.instructor_profiles_query
        instructor_profile = f.InstructorProfileFactory.create()
        variables = {
            'id': to_global_id('AccountNode', instructor_profile.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=instructor_profile.account.id)
        permission = Permission.objects.get(codename='view_accountinstructorprofile')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all instructor_profiles for this account
        self.assertEqual(
          data['accountInstructorProfiles']['edges'][0]['node']['account']['id'],
          variables['id']
        )


    def test_query_anon_user(self):
        """ Query list of account instructor_profiles - anon user """
        query = self.instructor_profiles_query
        instructor_profile = f.InstructorProfileFactory.create()
        variables = {
            'id': to_global_id('AccountNode', instructor_profile.account.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_instructor_profile(self):
        """ Update a instructor_profile """
        query = self.instructor_profile_update_mutation
        instructor_profile = f.InstructorProfileFactory.create()
        variables = self.variables_update
        variables['input']['account'] = to_global_id('AccountNode', instructor_profile.account.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['updateAccountInstructorProfile']['accountInstructorProfile']['classes'], variables['input']['classes'])
        self.assertEqual(data['updateAccountInstructorProfile']['accountInstructorProfile']['appointments'], variables['input']['appointments'])
        self.assertEqual(data['updateAccountInstructorProfile']['accountInstructorProfile']['events'], variables['input']['events'])


    def test_update_instructor_profile_anon_user(self):
        """ Don't allow updating instructor_profiles for non-logged in users """
        query = self.instructor_profile_update_mutation
        instructor_profile = f.InstructorProfileFactory.create()
        variables = self.variables_update
        variables['input']['account'] = to_global_id('AccountNode', instructor_profile.account.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_instructor_profile_permission_granted(self):
        """ Allow updating instructor_profiles for users with permissions """
        query = self.instructor_profile_update_mutation
        instructor_profile = f.InstructorProfileFactory.create()
        variables = self.variables_update
        variables['input']['account'] = to_global_id('AccountNode', instructor_profile.account.id)

        user = instructor_profile.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateAccountInstructorProfile']['accountInstructorProfile']['classes'], variables['input']['classes'])


    def test_update_instructor_profile_permission_denied(self):
        """ Check update instructor_profile permission denied error message """
        query = self.instructor_profile_update_mutation
        instructor_profile = f.InstructorProfileFactory.create()
        variables = self.variables_update
        variables['input']['account'] = to_global_id('AccountNode', instructor_profile.account.id)

        user = instructor_profile.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

