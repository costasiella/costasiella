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


class GQLOrganization(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['organization.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organization'
        self.permission_add = 'add_organization'
        self.permission_change = 'change_organization'
        self.permission_delete = 'delete_organization'

        self.organization_id = "T3JnYW5pemF0aW9uTm9kZToxMDA="
        
        self.variables_update = {
            "input": {
                "id": self.organization_id,
                "name": "Updated organization",
                "address": "The address",
                "phone": "033432432",
                "email": "tests@costasiella.com",
                "registration": "1234jhkd",
                "taxRegistration": "1234jhkd",
                "brandingColorBackground": "#111",
                "brandingColorText": "#222",
                "brandingColorAccent": "#333",
                "brandingColorSecondary": "#444"
            }
        }

        self.organization_query = '''
  query Organization($id: ID!) {
    organization(id:$id) {
      id
      name
      address
      phone
      email
      registration
      taxRegistration
      brandingColorBackground
      brandingColorText
      brandingColorAccent
      brandingColorSecondary
    }
  }
'''

        self.update_organization_mutation = '''
  mutation UpdateOrganization($input: UpdateOrganizationInput!) {
    updateOrganization(input: $input) {
      organization {
        id
        archived
        name
        address
        phone
        email
        registration
        taxRegistration
        brandingColorBackground
        brandingColorText
        brandingColorAccent
        brandingColorSecondary
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query_one(self):
        """ Query one  """   
        organization = models.Organization.objects.get(pk=100)

        # Now query single  and check
        query = self.organization_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": self.organization_id})
        data = executed.get('data')
        self.assertEqual(data['organization']['name'], organization.name)
        self.assertEqual(data['organization']['address'], organization.address)
        self.assertEqual(data['organization']['phone'], organization.phone)
        self.assertEqual(data['organization']['email'], organization.email)
        self.assertEqual(data['organization']['registration'], organization.registration)
        self.assertEqual(data['organization']['taxRegistration'], organization.tax_registration)
        self.assertEqual(data['organization']['brandingColorBackground'], organization.branding_color_background)
        self.assertEqual(data['organization']['brandingColorText'], organization.branding_color_text)
        self.assertEqual(data['organization']['brandingColorAccent'], organization.branding_color_accent)
        self.assertEqual(data['organization']['brandingColorSecondary'], organization.branding_color_secondary)

    # Organizations are public, so no need to test this anymore
    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one  """
    #     query = self.organization_query
    #
    #     executed = execute_test_client_api_query(query, self.anon_user, variables={"id": self.organization_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')

    # Organizations are public, so no need to test this anymore
    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """
    #     query = self.organization_query
    #
    #     user = f.RegularUserFactory.create()
    #
    #     executed = execute_test_client_api_query(query, user, variables={"id": self.organization_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        organization = models.Organization.objects.get(pk=100)

        query = self.organization_query
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organization')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables={"id": self.organization_id})
        data = executed.get('data')
        self.assertEqual(data['organization']['name'], organization.name)

    def test_update_organization(self):
        """ Update a  as admin user """
        query = self.update_organization_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganization']['organization']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganization']['organization']['address'], variables['input']['address'])
        self.assertEqual(data['updateOrganization']['organization']['phone'], variables['input']['phone'])
        self.assertEqual(data['updateOrganization']['organization']['email'], variables['input']['email'])
        self.assertEqual(data['updateOrganization']['organization']['registration'], variables['input']['registration'])
        self.assertEqual(data['updateOrganization']['organization']['taxRegistration'],
                         variables['input']['taxRegistration'])
        self.assertEqual(data['updateOrganization']['organization']['brandingColorBackground'],
                         variables['input']['brandingColorBackground'])
        self.assertEqual(data['updateOrganization']['organization']['brandingColorText'],
                         variables['input']['brandingColorText'])
        self.assertEqual(data['updateOrganization']['organization']['brandingColorAccent'],
                         variables['input']['brandingColorAccent'])
        self.assertEqual(data['updateOrganization']['organization']['brandingColorSecondary'],
                         variables['input']['brandingColorSecondary'])

    def test_update_organization_anon_user(self):
        """ Update a  as anonymous user """
        query = self.update_organization_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_organization_permission_granted(self):
        """ Update a  as user with permission """
        query = self.update_organization_mutation
        variables = self.variables_update

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
        self.assertEqual(data['updateOrganization']['organization']['name'], variables['input']['name'])

    def test_update_organization_permission_denied(self):
        """ Update a  as user without permissions """
        query = self.update_organization_mutation
        variables = self.variables_update

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
