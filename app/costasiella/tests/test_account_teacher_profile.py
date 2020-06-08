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



class GQLAccountTeacherProfile(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountteacherprofile'
        self.permission_add = 'add_accountteacherprofile'
        self.permission_change = 'change_accountteacherprofile'
        self.permission_delete = 'delete_accountteacherprofile'

        self.variables_update = {
            "input": {
                "classes": False,
                "appointments": False,
                "events": False,
            }
        }

        self.teacher_profiles_query = '''
  query AccountTeacherProfileQuery($id: ID!) {
    accountTeacherProfiles(account:$id) {
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
      teacher
      firstName
      lastName
      email
      phone
      mobile
      isActive
    }
  }
'''


        self.teacher_profile_update_mutation = '''
  mutation UpdateAccountTeacherProfile($input:UpdateAccountTeacherProfileInput!) {
    updateAccountTeacherProfile(input: $input) {
      accountTeacherProfile {
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
        """ Query list of account teacher_profiles """
        query = self.teacher_profiles_query
        teacher_profile = f.TeacherProfileFactory.create()
        variables = {
            'id': to_global_id('AccountNode', teacher_profile.account.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        print(data)

        self.assertEqual(
          data['accountTeacherProfiles']['edges'][0]['node']['account']['id'],
          variables['id']
        )
        self.assertEqual(data['accountTeacherProfiles']['edges'][0]['node']['classes'], teacher_profile.classes)
        self.assertEqual(data['accountTeacherProfiles']['edges'][0]['node']['appointments'], teacher_profile.appointments)
        self.assertEqual(data['accountTeacherProfiles']['edges'][0]['node']['events'], teacher_profile.events)


    def test_query_permission_denied(self):
        """ Query list of account teacher_profiles - check permission denied """
        query = self.teacher_profiles_query
        teacher_profile = f.TeacherProfileFactory.create()
        variables = {
            'id': to_global_id('AccountNode', teacher_profile.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=teacher_profile.account.id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permission_granted(self):
        """ Query list of account teacher_profiles with view permission """
        query = self.teacher_profiles_query
        teacher_profile = f.TeacherProfileFactory.create()
        variables = {
            'id': to_global_id('AccountNode', teacher_profile.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=teacher_profile.account.id)
        permission = Permission.objects.get(codename='view_accountteacherprofile')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all teacher_profiles for this account
        self.assertEqual(
          data['accountTeacherProfiles']['edges'][0]['node']['account']['id'],
          variables['id']
        )


    def test_query_anon_user(self):
        """ Query list of account teacher_profiles - anon user """
        query = self.teacher_profiles_query
        teacher_profile = f.TeacherProfileFactory.create()
        variables = {
            'id': to_global_id('AccountNode', teacher_profile.account.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_teacher_profile(self):
        """ Update a teacher_profile """
        query = self.teacher_profile_update_mutation
        teacher_profile = f.TeacherProfileFactory.create()
        variables = self.variables_update
        variables['input']['account'] = to_global_id('AccountNode', teacher_profile.account.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['updateAccountTeacherProfile']['accountTeacherProfile']['classes'], variables['input']['classes'])
        self.assertEqual(data['updateAccountTeacherProfile']['accountTeacherProfile']['appointments'], variables['input']['appointments'])
        self.assertEqual(data['updateAccountTeacherProfile']['accountTeacherProfile']['events'], variables['input']['events'])


    def test_update_teacher_profile_anon_user(self):
        """ Don't allow updating teacher_profiles for non-logged in users """
        query = self.teacher_profile_update_mutation
        teacher_profile = f.TeacherProfileFactory.create()
        variables = self.variables_update
        variables['input']['account'] = to_global_id('AccountNode', teacher_profile.account.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_teacher_profile_permission_granted(self):
        """ Allow updating teacher_profiles for users with permissions """
        query = self.teacher_profile_update_mutation
        teacher_profile = f.TeacherProfileFactory.create()
        variables = self.variables_update
        variables['input']['account'] = to_global_id('AccountNode', teacher_profile.account.id)

        user = teacher_profile.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateAccountTeacherProfile']['accountTeacherProfile']['classes'], variables['input']['classes'])


    def test_update_teacher_profile_permission_denied(self):
        """ Check update teacher_profile permission denied error message """
        query = self.teacher_profile_update_mutation
        teacher_profile = f.TeacherProfileFactory.create()
        variables = self.variables_update
        variables['input']['account'] = to_global_id('AccountNode', teacher_profile.account.id)

        user = teacher_profile.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

