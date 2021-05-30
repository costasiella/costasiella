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

from graphql_relay import to_global_id


class GQLAccountBankAccountMandate(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountbankaccountmandate'
        self.permission_add = 'add_accountbankaccountmandate'
        self.permission_change = 'change_accountbankaccountmandate'
        self.permission_delete = 'delete_accountbankaccountmandate'

        self.variables_create = {
            "input": {
                "organizationLocation": to_global_id('OrganizationLocationNode', self.organization_location.pk),
                "displayPublic": True,
                "name": "First room",
            }
        }

        self.variables_update = {
            "input": {
                "id": to_global_id('OrganizationLocationRoomNode', self.organization_account_bank_account_mandate.pk),
                "displayPublic": True,
                "name": "Updated room",
            }
        }

        self.variables_archive = {
            "input": {
                "id": to_global_id('OrganizationLocationRoomNode', self.organization_account_bank_account_mandate.pk),
                "archived": True,
            }
        }

        self.account_bank_account_mandates_query = '''
  query AccountBankAccountMandates($after: String, $before: String, $account: ID!) {
    accountBankAccountMandates(
      first: 100, 
      before: $before, 
      after: $after, 
      account: $account
    ) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          reference
          content
          signatureDate
        }
      }
    }
  }
'''

        self.account_bank_account_mandate_query = '''
  query AccountBankAccountMandate($id: ID!) {
    accountBankAccountMandate(id:$id) {
      id
      reference
      content
      signatureDate
    }
  }
'''

        self.account_bank_account_mandate_create_mutation = ''' 
  mutation CreateAccountBankAccountMandate($input:CreateAccountBankAccountMandateInput!) {
    createAccountBankAccountMandate(input: $input) {
      accountBankAccountMandate {
        id
      }
    }
  }
'''

        self.account_bank_account_mandate_update_mutation = '''
  mutation UpdateAccountBankAccountMandate($input:UpdateAccountBankAccountMandateInput!) {
    updateAccountBankAccountMandate(input: $input) {
      accountBankAccountMandate {
        id
      }
    }
  }
'''

        self.account_bank_account_mandate_archive_mutation = '''
  mutation DeleteAccountBankAccountMandate($input:DeleteAccountBankAccountMandateInput!) {
    deleteAccountBankAccountMandate(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of locations """
        query = self.account_bank_account_mandates_query
        account_bank_account_mandate = f.OrganizationLocationRoomFactory.create()

        variables = {
            'organizationLocation': to_global_id('OrganizationLocationNode', account_bank_account_mandate.organization_location.pk),
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['organizationLocationRooms']['edges'][0]['node']['organizationLocation']['id'], 
            variables['organizationLocation']
        )
        self.assertEqual(data['organizationLocationRooms']['edges'][0]['node']['name'], account_bank_account_mandate.name)
        self.assertEqual(data['organizationLocationRooms']['edges'][0]['node']['archived'], account_bank_account_mandate.archived)
        self.assertEqual(data['organizationLocationRooms']['edges'][0]['node']['displayPublic'], account_bank_account_mandate.display_public)


    def test_query_permission_denied(self):
        """ Query list of location rooms """
        query = self.account_bank_account_mandates_query
        account_bank_account_mandate = f.OrganizationLocationRoomFactory.create()
        non_public_account_bank_account_mandate = f.OrganizationLocationRoomFactory.build()
        non_public_account_bank_account_mandate.organization_location = account_bank_account_mandate.organization_location
        non_public_account_bank_account_mandate.display_public = False
        non_public_account_bank_account_mandate.save()

        variables = {
            'organizationLocation': to_global_id('OrganizationLocationNode', account_bank_account_mandate.organization_location.pk),
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        print(data)

        # Public locations only
        non_public_found = False
        for item in data['organizationLocationRooms']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)


    def test_query_permission_granted(self):
        """ Query list of location rooms """
        query = self.account_bank_account_mandates_query
        account_bank_account_mandate = f.OrganizationLocationRoomFactory.create()
        non_public_account_bank_account_mandate = f.OrganizationLocationRoomFactory.build()
        non_public_account_bank_account_mandate.organization_location = account_bank_account_mandate.organization_location
        non_public_account_bank_account_mandate.display_public = False
        non_public_account_bank_account_mandate.save()

        variables = {
            'organizationLocation': to_global_id('OrganizationLocationNode', account_bank_account_mandate.organization_location.pk),
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_accountbankaccountmandate')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all locations, including non public
        non_public_found = False
        for item in data['organizationLocationRooms']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        # Assert non public locations are listed
        self.assertEqual(non_public_found, True)


    def test_query_anon_user(self):
        """ Query list of location rooms """
        query = self.account_bank_account_mandates_query
        account_bank_account_mandate = f.OrganizationLocationRoomFactory.create()
        variables = {
            'organizationLocation': to_global_id('OrganizationLocationNode', account_bank_account_mandate.organization_location.pk),
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one location room """   
        account_bank_account_mandate = f.OrganizationLocationRoomFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationRoomNode', account_bank_account_mandate.pk)

        # Now query single location and check
        query = self.account_bank_account_mandate_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLocationRoom']['organizationLocation']['id'], 
          to_global_id('OrganizationLocationNode', account_bank_account_mandate.organization_location.pk))
        self.assertEqual(data['organizationLocationRoom']['name'], account_bank_account_mandate.name)
        self.assertEqual(data['organizationLocationRoom']['archived'], account_bank_account_mandate.archived)
        self.assertEqual(data['organizationLocationRoom']['displayPublic'], account_bank_account_mandate.display_public)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one location room """   
        account_bank_account_mandate = f.OrganizationLocationRoomFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationRoomNode', account_bank_account_mandate.pk)

        # Now query single location and check
        query = self.account_bank_account_mandate_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        account_bank_account_mandate = f.OrganizationLocationRoomFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationRoomNode', account_bank_account_mandate.pk)

        # Now query single location and check
        query = self.account_bank_account_mandate_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_accountbankaccountmandate')
        user.user_permissions.add(permission)
        user.save()
        account_bank_account_mandate = f.OrganizationLocationRoomFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationLocationRoomNode', account_bank_account_mandate.pk)

        # Now query single location and check   
        query = self.account_bank_account_mandate_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationLocationRoom']['name'], account_bank_account_mandate.name)


    def test_create_account_bank_account_mandate(self):
        """ Create a location room """
        query = self.account_bank_account_mandate_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
          data['createOrganizationLocationRoom']['organizationLocationRoom']['organizationLocation']['id'], 
          variables['input']['organizationLocation'])
        self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['archived'], False)
        self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['displayPublic'], variables['input']['displayPublic'])


    def test_create_account_bank_account_mandate_anon_user(self):
        """ Don't allow creating locations rooms for non-logged in users """
        query = self.account_bank_account_mandate_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_account_bank_account_mandate_permission_granted(self):
        """ Allow creating location rooms for users with permissions """
        query = self.account_bank_account_mandate_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
          data['createOrganizationLocationRoom']['organizationLocationRoom']['organizationLocation']['id'], 
          variables['input']['organizationLocation'])
        self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['archived'], False)
        self.assertEqual(data['createOrganizationLocationRoom']['organizationLocationRoom']['displayPublic'], variables['input']['displayPublic'])


    def test_create_account_bank_account_mandate_permission_denied(self):
        """ Check create location room permission denied error message """
        query = self.account_bank_account_mandate_create_mutation
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


    def test_update_account_bank_account_mandate(self):
        """ Update a location room """
        query = self.account_bank_account_mandate_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateOrganizationLocationRoom']['organizationLocationRoom']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationLocationRoom']['organizationLocationRoom']['displayPublic'], variables['input']['displayPublic'])


    def test_update_account_bank_account_mandate_anon_user(self):
        """ Don't allow updating location rooms for non-logged in users """
        query = self.account_bank_account_mandate_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_account_bank_account_mandate_permission_granted(self):
        """ Allow updating location rooms for users with permissions """
        query = self.account_bank_account_mandate_update_mutation
        variables = self.variables_update

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
        self.assertEqual(data['updateOrganizationLocationRoom']['organizationLocationRoom']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationLocationRoom']['organizationLocationRoom']['displayPublic'], variables['input']['displayPublic'])


    def test_update_account_bank_account_mandate_permission_denied(self):
        """ Check update location room permission denied error message """
        query = self.account_bank_account_mandate_update_mutation
        variables = self.variables_update

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


    def test_archive_account_bank_account_mandate(self):
        """ Archive a location room"""
        query = self.account_bank_account_mandate_archive_mutation
        variables = self.variables_archive

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationLocationRoom']['organizationLocationRoom']['archived'], variables['input']['archived'])


    def test_archive_account_bank_account_mandate_anon_user(self):
        """ Archive a location room """
        query = self.account_bank_account_mandate_archive_mutation
        variables = self.variables_archive

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_account_bank_account_mandate_permission_granted(self):
        """ Allow archiving locations for users with permissions """
        query = self.account_bank_account_mandate_archive_mutation
        variables = self.variables_archive

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
        self.assertEqual(data['archiveOrganizationLocationRoom']['organizationLocationRoom']['archived'], variables['input']['archived'])


    def test_archive_account_bank_account_mandate_permission_denied(self):
        """ Check archive location room permission denied error message """
        query = self.account_bank_account_mandate_archive_mutation
        variables = self.variables_archive
        
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

