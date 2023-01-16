import graphene
import os
from django.test import TestCase
from graphene.test import Client
from django.contrib.auth.models import AnonymousUser, Permission
from django.contrib.auth import get_user_model

# Create your tests here.
from graphql_relay import to_global_id
from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema
from ..modules.gql_tools import get_rid

from .factories import AdminUserFactory

# Allauth model
from allauth.account.models import EmailAddress


class GQLAccount(TestCase):
    # use TransActionTestCase to db is reset after each query
    # https://docs.djangoproject.com/en/2.2/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_account'
        self.permission_add = 'add_account'
        self.permission_change = 'change_account'
        self.permission_delete = 'delete_account'

        self.business = f.BusinessB2BFactory.create()

        self.variables_query_list = {
            "isActive": True
        }

        self.variables_create = {
            "input": {
                "firstName": "New",
                "lastName": "User",
                "email": "new72609QXF@user.nl",
            }
        }

        self.variables_update = {
            "input": {
                "firstName": "Updated",
                "lastName": "User",
                "email": "updated72609QXF@user.nl",
                "invoiceToBusiness": to_global_id("BusinessNode", self.business.id)
            }
        }

        with open(os.path.join(os.getcwd(), "costasiella", "tests", "files", "test_image.txt"), 'r') as input_file:
            input_image = input_file.read().replace("\n", "")

            self.variables_update_image = {
                "input": {
                    "imageFileName": "test_image.jpg",
                    "image": input_image
                }
            }

        self.variables_update_active = {
            "input": {
                "isActive": False
            }
        }

        self.variables_delete = {
            "input": {}
        }

        self.accounts_query = '''
  query Accounts($after: String, $before: String, $isActive: Boolean!) {
    accounts(first: 15, before: $before, after: $after, isActive: $isActive) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          firstName
          lastName
          email
          isActive
          organizationDiscovery {
            id
          }
          organizationLanguage {
            id
          }
          invoiceToBusiness {
            id
          }
          hasReachedTrialLimit
        }
      }
    }
  }
'''

        self.instructors_query = '''
    query Instructors {
      instructors{
        edges {
          node {
            id
            fullName
          }
        }
      }
    }        
'''
        self.instructors_contact_fields_query = '''
    query Instructors {
      instructors{
        edges {
          node {
            id
            fullName
            email
            phone
            mobile
          }
        }
      }
    }        
'''

        self.account_query = '''
  query Account($id: ID!) {
    account(id:$id) {
      id
      firstName
      lastName
      email
      isActive
    }
  }
'''

        self.account_create_mutation = ''' 
  mutation CreateAccount($input:CreateAccountInput!) {
    createAccount(input: $input) {
      account {
        id
        firstName
        lastName
        email
        invoiceToBusiness {
          id
        }
      }
    }
  }
'''

        self.account_update_mutation = '''
  mutation UpdateAccount($input:UpdateAccountInput!) {
    updateAccount(input: $input) {
      account {
        id
        firstName
        lastName
        email
        urlImageThumbnailSmall
        invoiceToBusiness {
          id
        }
      }
    }
  }
'''

        self.account_update_active_mutation = '''
  mutation UpdateAccountActive($input: UpdateAccountActiveInput!) {
    updateAccountActive(input: $input) {
      account {
        id
        isActive
      }
    }
  }
  '''

        self.account_delete_mutation = '''
  mutation DeleteAccount($input: DeleteAccountInput!) {
    deleteAccount(input: $input) {
      ok
    }
  }
  '''

    def tearDown(self):
        # This is run after every test
        # pass
        # Clean up accounts in costasiella_account table
        get_user_model().objects.all().delete()

    def test_query(self):
        """ Query list of accounts """
        query = self.accounts_query
        account = f.RegularUserFactory()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(len(data['accounts']['edges']), 1) # Ensure the Admin super use isn't listed
        self.assertEqual(data['accounts']['edges'][0]['node']['isActive'], account.is_active)
        self.assertEqual(data['accounts']['edges'][0]['node']['firstName'], account.first_name)
        self.assertEqual(data['accounts']['edges'][0]['node']['lastName'], account.last_name)
        self.assertEqual(data['accounts']['edges'][0]['node']['email'], account.email)
        self.assertEqual(data['accounts']['edges'][0]['node']['organizationDiscovery']['id'],
                         to_global_id('OrganizationDiscoveryNode', account.organization_discovery.id))
        self.assertEqual(data['accounts']['edges'][0]['node']['organizationLanguage']['id'],
                         to_global_id('OrganizationLanguageNode', account.organization_language.id))

    def test_query_instructors_anon(self):
        """ Query list of instructors as anon user """
        query = self.instructors_query
        instructor = f.InstructorFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user)
        data = executed.get('data')

        self.assertEqual(data['instructors']['edges'][0]['node']['fullName'], instructor.full_name)

    def test_query_instructors_anon_no_contact_fields(self):
        """ Permission denied when querying contact fields as anon user """
        query = self.instructors_contact_fields_query
        instructor = f.InstructorFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_instructors_user_no_contact_fields(self):
        """ Permission denied when querying contact fields as anon user """
        query = self.instructors_contact_fields_query
        account = f.RegularUserFactory.create()
        instructor = f.InstructorFactory.create()

        executed = execute_test_client_api_query(query, account)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_invoice_to_business(self):
        """ Query list of accounts - with invoice to business set
        - A separate test to the RegularUserFactory class isn't impacted
        """

        query = self.accounts_query
        account = f.RegularUserFactory()
        account.invoice_to_business = self.business
        account.save()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(len(data['accounts']['edges']), 1)  # Ensure the Admin super use isn't listed
        self.assertEqual(data['accounts']['edges'][0]['node']['firstName'], account.first_name)
        self.assertEqual(data['accounts']['edges'][0]['node']['invoiceToBusiness']['id'],
                         to_global_id('BusinessNode', account.invoice_to_business.id))

    def test_query_has_reached_trial_limit(self):
        """ Query list of accounts and check if trial limit field works """
        query = self.accounts_query
        account_classpass = f.AccountClasspassFactory.create()
        account_classpass.organization_classpass.trial_pass = True
        account_classpass.organization_classpass.save()
        account = account_classpass.account

        setting = models.SystemSetting(
            setting="workflow_trial_pass_limit",
            value="1"
        )
        setting.save()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(len(data['accounts']['edges']), 1) # Ensure the Admin super use isn't listed
        self.assertEqual(data['accounts']['edges'][0]['node']['hasReachedTrialLimit'], True)

    def test_query_permission_denied(self):
        """ Query list of accounts - check permission denied """
        query = self.accounts_query
        account = f.RegularUserFactory()
        
        # User created account
        executed = execute_test_client_api_query(query, account, variables=self.variables_query_list)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of accounts with view permission """
        query = self.accounts_query
        account = f.RegularUserFactory.create()

        # Create regular user
        permission = Permission.objects.get(codename='view_account')
        account.user_permissions.add(permission)
        account.save()

        executed = execute_test_client_api_query(query, account, variables=self.variables_query_list)
        data = executed.get('data')

        # List all accounts
        self.assertEqual(data['accounts']['edges'][0]['node']['isActive'], account.is_active)
        self.assertEqual(data['accounts']['edges'][0]['node']['firstName'], account.first_name)
        self.assertEqual(data['accounts']['edges'][0]['node']['lastName'], account.last_name)
        self.assertEqual(data['accounts']['edges'][0]['node']['email'], account.email)

    def test_query_anon_user(self):
        """ Query list of accounts - anon user """
        query = self.accounts_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account as admin """   
        account = f.RegularUserFactory.create()
        node_id = to_global_id('AccountNode', account.pk)

        # Now query single account and check
        executed = execute_test_client_api_query(self.account_query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['account']['firstName'], account.first_name)
        self.assertEqual(data['account']['lastName'], account.last_name)
        self.assertEqual(data['account']['email'], account.email)
        self.assertEqual(data['account']['isActive'], account.is_active)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one glacount """   
        account = f.RegularUserFactory.create()
        node_id = to_global_id('AccountNode', account.pk)

        # Now query single account and check
        executed = execute_test_client_api_query(self.account_query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization to view other acounts """
        # Create regular user
        account = f.RegularUserFactory.create()
        instructor = f.InstructorFactory.create()
        node_id = to_global_id('AccountNode', account.pk)

        # Now query single account and check
        executed = execute_test_client_api_query(self.account_query, instructor, variables={"id": node_id})

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_accounts_can_view_own_without_permissions(self):
        """ Accounts can get their own info """
        # Create regular user
        account = f.RegularUserFactory.create()
        node_id = to_global_id('AccountNode', account.pk)

        # Now query single account and check
        executed = execute_test_client_api_query(self.account_query, account, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['account']['firstName'], account.first_name)

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        account = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_account')
        account.user_permissions.add(permission)
        account.save()

        node_id = to_global_id('AccountNode', account.pk)
        # Now query single location and check   
        executed = execute_test_client_api_query(self.account_query, account, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['account']['firstName'], account.first_name)

    def test_create_account(self):
        """ Create a account """
        query = self.account_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['createAccount']['account']['firstName'], variables['input']['firstName'])
        self.assertEqual(data['createAccount']['account']['lastName'], variables['input']['lastName'])
        self.assertEqual(data['createAccount']['account']['email'], variables['input']['email'])

        # Check Allauth record
        self.assertEqual(
          EmailAddress.objects.filter(email=variables['input']['email']).exists(),
          True
        )

        # Check Instructor profile record
        rid = get_rid(data['createAccount']['account']['id'])
        self.assertEqual(
            models.AccountInstructorProfile.objects.filter(account=rid.id).exists(),
            True
        )

        # Check bank account record
        rid = get_rid(data['createAccount']['account']['id'])
        self.assertEqual(
            models.AccountBankAccount.objects.filter(account=rid.id).exists(),
            True
        )

    def test_create_account_anon_user(self):
        """ Don't allow creating accounts for non-logged in users """
        query = self.account_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_account_permission_granted(self):
        """ Allow creating accounts for users with permissions """
        query = self.account_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createAccount']['account']['firstName'], variables['input']['firstName'])

    def test_create_account_permission_denied(self):
        """ Check create account permission denied error message """
        query = self.account_create_mutation
        variables = self.variables_create

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

    def test_update_account(self):
        """ Update a account """
        query = self.account_update_mutation

        email = f.AllAuthEmailAddress.create()
        account = email.user
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['updateAccount']['account']['firstName'], variables['input']['firstName'])
        self.assertEqual(data['updateAccount']['account']['lastName'], variables['input']['lastName'])
        self.assertEqual(data['updateAccount']['account']['email'], variables['input']['email'])
        self.assertEqual(data['updateAccount']['account']['invoiceToBusiness']['id'],
                         variables['input']['invoiceToBusiness'])

    def test_update_account_permission_own(self):
        """ A user can update their own account """
        query = self.account_update_mutation

        email = f.AllAuthEmailAddress.create()
        account = email.user
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        executed = execute_test_client_api_query(
            query,
            account,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['updateAccount']['account']['firstName'], variables['input']['firstName'])
        self.assertEqual(data['updateAccount']['account']['lastName'], variables['input']['lastName'])
        self.assertEqual(data['updateAccount']['account']['email'], variables['input']['email'])

    def test_update_account_image(self):
        """ Update account image """
        query = self.account_update_mutation

        email = f.AllAuthEmailAddress.create()
        account = email.user
        variables = self.variables_update_image
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        # Check that an image url is generated
        self.assertEqual("d/media/" in data['updateAccount']['account']['urlImageThumbnailSmall'], True)

        # Check that the image field was set in the model
        account = models.Account.objects.last()
        self.assertNotEqual(account.image, None)

    def test_update_account_anon_user(self):
        """ Don't allow updating accounts for non-logged in users """
        query = self.account_update_mutation

        email = f.AllAuthEmailAddress.create()
        account = email.user
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_account_permission_granted(self):
        """ Allow updating accounts for users with permissions """
        query = self.account_update_mutation

        email = f.AllAuthEmailAddress.create()
        account = email.user
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        # Create regular user
        permission = Permission.objects.get(codename=self.permission_change)
        account.user_permissions.add(permission)
        account.save()

        executed = execute_test_client_api_query(
            query, 
            account, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateAccount']['account']['firstName'], variables['input']['firstName'])


    def test_update_account_permission_denied_other_user(self):
        """ Check update account permission denied error message """
        query = self.account_update_mutation

        email = f.AllAuthEmailAddress.create()
        account = email.user
        other_user = f.InstructorFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        executed = execute_test_client_api_query(
            query, 
            other_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_update_account_active(self):
        """ Change active status of an account """
        query = self.account_update_active_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_update_active
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateAccountActive']['account']['isActive'], variables['input']['isActive'])


    def test_update_account_active_anon_user(self):
        """ Update account active status denied for anon user """
        query = self.account_update_active_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_update_active
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_account_active_permission_granted(self):
        """ Allow update account status for users with permissions """
        query = self.account_update_active_mutation

        account = f.RegularUserFactory.create()
        other_user = f.InstructorFactory.create()
        variables = self.variables_update_active
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        # Grant permissions
        permission = Permission.objects.get(codename=self.permission_view)
        other_user.user_permissions.add(permission)
        permission = Permission.objects.get(codename=self.permission_delete)
        other_user.user_permissions.add(permission)
        other_user.save()

        executed = execute_test_client_api_query(
            query,
            other_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateAccountActive']['account']['isActive'], variables['input']['isActive'])

    def test_update_account_active_permission_granted_current_account(self):
        """ Allow update account status for users with permissions """
        query = self.account_update_active_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_update_active
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        # Grant permissions
        permission = Permission.objects.get(codename=self.permission_delete)
        account.user_permissions.add(permission)
        account.save()

        executed = execute_test_client_api_query(
            query,
            account,
            variables=variables
        )

        errors = executed.get('errors')
        self.assertEqual(errors[0]['extensions']['code'], "USER_CURRENTLY_LOGGED_IN")

    def test_update_account_active_permission_denied(self):
        """ Check update account status permission denied error message """
        query = self.account_update_active_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_update_active
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        executed = execute_test_client_api_query(
            query, 
            account, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_delete_account(self):
        """ Delete account """
        query = self.account_delete_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccount']['ok'], True)


    def test_delete_account_anon_user(self):
        """ Delete account denied for anon user """
        query = self.account_delete_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_account_permission_granted(self):
        """ Allow deleting accounts for users with permissions """
        query = self.account_delete_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        # Grant permissions
        permission = Permission.objects.get(codename=self.permission_delete)
        account.user_permissions.add(permission)
        account.save()

        executed = execute_test_client_api_query(
            query, 
            account,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['extensions']['code'], "USER_CURRENTLY_LOGGED_IN")

    def test_delete_account_permission_granted_other_user(self):
        """ Allow deleting accounts for users with permissions """
        query = self.account_delete_mutation

        account = f.RegularUserFactory.create()
        other_user = f.InstructorFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        # Grant permissions
        permission = Permission.objects.get(codename=self.permission_delete)
        other_user.user_permissions.add(permission)
        other_user.save()

        executed = execute_test_client_api_query(
            query,
            other_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccount']['ok'], True)

    def test_delete_account_permission_denied(self):
        """ Check delete account permission denied error message """
        query = self.account_delete_mutation

        account = f.RegularUserFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('AccountNode', account.pk)

        executed = execute_test_client_api_query(
            query, 
            account, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
