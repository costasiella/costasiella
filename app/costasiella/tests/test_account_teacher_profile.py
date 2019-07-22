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

        self.teacher_profile_query = '''
  query AccountTeacherProfile($id: ID!, $accountId: ID!, $after: String, $before: String, $archived: Boolean!) {
    accountTeacherProfile(id:$id) {
      id
      account {
          id
      }
      organizationTeacherProfile {
        id
        name
      }
      financePaymentMethod {
        id
        name
      }
      dateStart
      dateEnd
      note
      registrationFeePaid
      createdAt
    }
    organizationTeacherProfiles(first: 100, before: $before, after: $after, archived: $archived) {
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
    financePaymentMethods(first: 100, before: $before, after: $after, archived: $archived) {
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
          code
        }
      }
    }
    account(id:$accountId) {
      id
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
  mutation UpdateAccountTeacherProfile($input: UpdateAccountTeacherProfileInput!) {
    updateAccountTeacherProfile(input: $input) {
      accountTeacherProfile {
        id
        account {
          id
          firstName
          lastName
          email
        }
        organizationTeacherProfile {
          id
          name
        }
        financePaymentMethod {
          id
          name
        }
        dateStart
        dateEnd
        note
        registrationFeePaid        
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
        teacher_profile = f.AccountTeacherProfileFactory.create()
        variables = {
            'accountId': to_global_id('AccountTeacherProfileNode', teacher_profile.account.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountTeacherProfiles']['edges'][0]['node']['organizationTeacherProfile']['id'], 
            to_global_id("OrganizationTeacherProfileNode", teacher_profile.organization_teacher_profile.id)
        )
        self.assertEqual(
            data['accountTeacherProfiles']['edges'][0]['node']['financePaymentMethod']['id'], 
            to_global_id("FinancePaymentMethodNode", teacher_profile.finance_payment_method.id)
        )
        self.assertEqual(data['accountTeacherProfiles']['edges'][0]['node']['dateStart'], str(teacher_profile.date_start))
        self.assertEqual(data['accountTeacherProfiles']['edges'][0]['node']['dateEnd'], teacher_profile.date_end) # Factory is set to None so no string conversion required
        self.assertEqual(data['accountTeacherProfiles']['edges'][0]['node']['note'], teacher_profile.note)
        self.assertEqual(data['accountTeacherProfiles']['edges'][0]['node']['registrationFeePaid'], teacher_profile.registration_fee_paid)


    def test_query_permision_denied(self):
        """ Query list of account teacher_profiles - check permission denied """
        query = self.teacher_profiles_query
        teacher_profile = f.AccountTeacherProfileFactory.create()
        variables = {
            'accountId': to_global_id('AccountTeacherProfileNode', teacher_profile.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=teacher_profile.account.id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permision_granted(self):
        """ Query list of account teacher_profiles with view permission """
        query = self.teacher_profiles_query
        teacher_profile = f.AccountTeacherProfileFactory.create()
        variables = {
            'accountId': to_global_id('AccountTeacherProfileNode', teacher_profile.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=teacher_profile.account.id)
        permission = Permission.objects.get(codename='view_accountteacher_profile')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all teacher_profiles
        self.assertEqual(
            data['accountTeacherProfiles']['edges'][0]['node']['organizationTeacherProfile']['id'], 
            to_global_id("OrganizationTeacherProfileNode", teacher_profile.organization_teacher_profile.id)
        )


    def test_query_anon_user(self):
        """ Query list of account teacher_profiles - anon user """
        query = self.teacher_profiles_query
        teacher_profile = f.AccountTeacherProfileFactory.create()
        variables = {
            'accountId': to_global_id('AccountTeacherProfileNode', teacher_profile.account.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one account teacher_profile as admin """   
        teacher_profile = f.AccountTeacherProfileFactory.create()
        
        variables = {
            "id": to_global_id("AccountTeacherProfileNode", teacher_profile.id),
            "accountId": to_global_id("AccountNode", teacher_profile.account.id),
            "archived": False,
        }

        # Now query single teacher_profile and check
        executed = execute_test_client_api_query(self.teacher_profile_query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountTeacherProfile']['account']['id'], 
            to_global_id('AccountNode', teacher_profile.account.id)
        )
        self.assertEqual(
            data['accountTeacherProfile']['organizationTeacherProfile']['id'], 
            to_global_id('OrganizationTeacherProfileNode', teacher_profile.organization_teacher_profile.id)
        )
        self.assertEqual(
            data['accountTeacherProfile']['financePaymentMethod']['id'], 
            to_global_id('FinancePaymentMethodNode', teacher_profile.finance_payment_method.id)
        )
        self.assertEqual(data['accountTeacherProfile']['dateStart'], str(teacher_profile.date_start))
        self.assertEqual(data['accountTeacherProfile']['dateEnd'], teacher_profile.date_end)
        self.assertEqual(data['accountTeacherProfile']['note'], teacher_profile.note)
        self.assertEqual(data['accountTeacherProfile']['registrationFeePaid'], teacher_profile.registration_fee_paid)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account teacher_profile """   
        teacher_profile = f.AccountTeacherProfileFactory.create()

        variables = {
            "id": to_global_id("AccountTeacherProfileNode", teacher_profile.id),
            "accountId": to_global_id("AccountNode", teacher_profile.account.id),
            "archived": False,
        }

        # Now query single teacher_profile and check
        executed = execute_test_client_api_query(self.teacher_profile_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        teacher_profile = f.AccountTeacherProfileFactory.create()
        user = teacher_profile.account

        variables = {
            "id": to_global_id("AccountTeacherProfileNode", teacher_profile.id),
            "accountId": to_global_id("AccountNode", teacher_profile.account.id),
            "archived": False,
        }

        # Now query single teacher_profile and check
        executed = execute_test_client_api_query(self.teacher_profile_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        teacher_profile = f.AccountTeacherProfileFactory.create()
        user = teacher_profile.account
        permission = Permission.objects.get(codename='view_accountteacher_profile')
        user.user_permissions.add(permission)
        user.save()
        

        variables = {
            "id": to_global_id("AccountTeacherProfileNode", teacher_profile.id),
            "accountId": to_global_id("AccountNode", teacher_profile.account.id),
            "archived": False,
        }

        # Now query single teacher_profile and check   
        executed = execute_test_client_api_query(self.teacher_profile_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountTeacherProfile']['organizationTeacherProfile']['id'], 
            to_global_id('OrganizationTeacherProfileNode', teacher_profile.organization_teacher_profile.id)
        )


    def test_update_teacher_profile(self):
        """ Update a teacher_profile """
        query = self.teacher_profile_update_mutation
        teacher_profile = f.AccountTeacherProfileFactory.create()
        organization_teacher_profile = f.OrganizationTeacherProfileFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountTeacherProfileNode', teacher_profile.id)
        variables['input']['organizationTeacherProfile'] = to_global_id('OrganizationTeacherProfileNode', organization_teacher_profile.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateAccountTeacherProfile']['accountTeacherProfile']['organizationTeacherProfile']['id'], 
          variables['input']['organizationTeacherProfile']
        )
        self.assertEqual(
          data['updateAccountTeacherProfile']['accountTeacherProfile']['financePaymentMethod']['id'], 
          variables['input']['financePaymentMethod']
        )
        self.assertEqual(data['updateAccountTeacherProfile']['accountTeacherProfile']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['updateAccountTeacherProfile']['accountTeacherProfile']['dateEnd'], variables['input']['dateEnd'])
        self.assertEqual(data['updateAccountTeacherProfile']['accountTeacherProfile']['note'], variables['input']['note'])
        self.assertEqual(data['updateAccountTeacherProfile']['accountTeacherProfile']['registrationFeePaid'], variables['input']['registrationFeePaid'])


    def test_update_teacher_profile_anon_user(self):
        """ Don't allow updating teacher_profiles for non-logged in users """
        query = self.teacher_profile_update_mutation
        teacher_profile = f.AccountTeacherProfileFactory.create()
        organization_teacher_profile = f.OrganizationTeacherProfileFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountTeacherProfileNode', teacher_profile.id)
        variables['input']['organizationTeacherProfile'] = to_global_id('OrganizationTeacherProfileNode', organization_teacher_profile.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

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
        teacher_profile = f.AccountTeacherProfileFactory.create()
        organization_teacher_profile = f.OrganizationTeacherProfileFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountTeacherProfileNode', teacher_profile.id)
        variables['input']['organizationTeacherProfile'] = to_global_id('OrganizationTeacherProfileNode', organization_teacher_profile.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

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
        self.assertEqual(data['updateAccountTeacherProfile']['accountTeacherProfile']['dateStart'], variables['input']['dateStart'])


    def test_update_teacher_profile_permission_denied(self):
        """ Check update teacher_profile permission denied error message """
        query = self.teacher_profile_update_mutation
        teacher_profile = f.AccountTeacherProfileFactory.create()
        organization_teacher_profile = f.OrganizationTeacherProfileFactory.create()
        finance_payment_method = f.FinancePaymentMethodFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountTeacherProfileNode', teacher_profile.id)
        variables['input']['organizationTeacherProfile'] = to_global_id('OrganizationTeacherProfileNode', organization_teacher_profile.id)
        variables['input']['financePaymentMethod'] = to_global_id('FinancePaymentMethodNode', finance_payment_method.id)

        user = teacher_profile.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

