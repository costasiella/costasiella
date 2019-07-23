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


class GQLOrganizationAppointmentPrice(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationappointmentprice'
        self.permission_add = 'add_organizationappointmentprice'
        self.permission_change = 'change_organizationappointmentprice'
        self.permission_delete = 'delete_organizationappointmentprice'

        self.organization_location = f.OrganizationLocationFactory.create()
        self.organization_appointment_price = f.OrganizationAppointmentPriceFactory.create()

        self.variables_create = {
            "input": {
                "organizationLocation": to_global_id('OrganizationLocationNode', self.organization_location.pk),
                "displayPublic": True,
                "name": "First room",
            }
        }

        self.variables_update = {
            "input": {
                "id": to_global_id('OrganizationAppointmentPriceNode', self.organization_appointment_price.pk),
                "displayPublic": True,
                "name": "Updated room",
            }
        }

        self.variables_archive = {
            "input": {
                "id": to_global_id('OrganizationAppointmentPriceNode', self.organization_appointment_price.pk),
                "archived": True,
            }
        }

        self.appointment_prices_query = '''
  query OrganizationAppointmentPrices($after: String, $before: String, $organizationLocation: ID!, $archived: Boolean!) {
    organizationAppointmentPrices(first: 15, before: $before, after: $after, organizationLocation: $organizationLocation, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationLocation {
            id
            name
          }
          archived,
          displayPublic
          name
        }
      }
    }
    organizationLocation(id: $organizationLocation) {
      id
      name
    }
  }
'''

        self.appointment_price_query = '''
  query OrganizationAppointmentPrice($id: ID!) {
    organizationAppointmentPrice(id:$id) {
      id
      organizationLocation {
        id
        name
      }
      name
      displayPublic
      archived
    }
  }
'''

        self.appointment_price_create_mutation = ''' 
  mutation CreateOrganizationAppointmentPrice($input: CreateOrganizationAppointmentPriceInput!) {
    createOrganizationAppointmentPrice(input: $input) {
      organizationAppointmentPrice {
        id
        organizationLocation {
          id
          name
        }
        archived
        displayPublic
        name
      }
    }
  }
'''

        self.appointment_price_update_mutation = '''
  mutation UpdateOrganizationAppointmentPrice($input: UpdateOrganizationAppointmentPriceInput!) {
    updateOrganizationAppointmentPrice(input: $input) {
      organizationAppointmentPrice {
        id
        organizationLocation {
          id
          name
        }
        name
        displayPublic
      }
    }
  }
'''

        self.appointment_price_archive_mutation = '''
  mutation ArchiveOrganizationAppointmentPrice($input: ArchiveOrganizationAppointmentPriceInput!) {
    archiveOrganizationAppointmentPrice(input: $input) {
      organizationAppointmentPrice {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of locations """
        query = self.appointment_prices_query
        appointment_price = f.OrganizationAppointmentPriceFactory.create()

        variables = {
            'organizationLocation': to_global_id('OrganizationLocationNode', appointment_price.organization_location.pk),
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['organizationAppointmentPrices']['edges'][0]['node']['organizationLocation']['id'], 
            variables['organizationLocation']
        )
        self.assertEqual(data['organizationAppointmentPrices']['edges'][0]['node']['name'], appointment_price.name)
        self.assertEqual(data['organizationAppointmentPrices']['edges'][0]['node']['archived'], appointment_price.archived)
        self.assertEqual(data['organizationAppointmentPrices']['edges'][0]['node']['displayPublic'], appointment_price.display_public)


    def test_query_permision_denied(self):
        """ Query list of location rooms """
        query = self.appointment_prices_query
        appointment_price = f.OrganizationAppointmentPriceFactory.create()
        non_public_appointment_price = f.OrganizationAppointmentPriceFactory.build()
        non_public_appointment_price.organization_location = appointment_price.organization_location
        non_public_appointment_price.display_public = False
        non_public_appointment_price.save()

        variables = {
            'organizationLocation': to_global_id('OrganizationLocationNode', appointment_price.organization_location.pk),
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        print(data)

        # Public locations only
        non_public_found = False
        for item in data['organizationAppointmentPrices']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)


    def test_query_permision_granted(self):
        """ Query list of location rooms """
        query = self.appointment_prices_query
        appointment_price = f.OrganizationAppointmentPriceFactory.create()
        non_public_appointment_price = f.OrganizationAppointmentPriceFactory.build()
        non_public_appointment_price.organization_location = appointment_price.organization_location
        non_public_appointment_price.display_public = False
        non_public_appointment_price.save()

        variables = {
            'organizationLocation': to_global_id('OrganizationLocationNode', appointment_price.organization_location.pk),
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationappointmentprice')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all locations, including non public
        non_public_found = False
        for item in data['organizationAppointmentPrices']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        # Assert non public locations are listed
        self.assertEqual(non_public_found, True)


    def test_query_anon_user(self):
        """ Query list of location rooms """
        query = self.appointment_prices_query
        appointment_price = f.OrganizationAppointmentPriceFactory.create()
        variables = {
            'organizationLocation': to_global_id('OrganizationLocationNode', appointment_price.organization_location.pk),
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one location room """   
        appointment_price = f.OrganizationAppointmentPriceFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationAppointmentPriceNode', appointment_price.pk)

        # Now query single location and check
        query = self.appointment_price_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationAppointmentPrice']['organizationLocation']['id'], 
          to_global_id('OrganizationLocationNode', appointment_price.organization_location.pk))
        self.assertEqual(data['organizationAppointmentPrice']['name'], appointment_price.name)
        self.assertEqual(data['organizationAppointmentPrice']['archived'], appointment_price.archived)
        self.assertEqual(data['organizationAppointmentPrice']['displayPublic'], appointment_price.display_public)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one location room """   
        appointment_price = f.OrganizationAppointmentPriceFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationAppointmentPriceNode', appointment_price.pk)

        # Now query single location and check
        query = self.appointment_price_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        appointment_price = f.OrganizationAppointmentPriceFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationAppointmentPriceNode', appointment_price.pk)

        # Now query single location and check
        query = self.appointment_price_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationappointmentprice')
        user.user_permissions.add(permission)
        user.save()
        appointment_price = f.OrganizationAppointmentPriceFactory.create()

        # First query locations to get node id easily
        node_id = to_global_id('OrganizationAppointmentPriceNode', appointment_price.pk)

        # Now query single location and check   
        query = self.appointment_price_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationAppointmentPrice']['name'], appointment_price.name)


    def test_create_appointment_price(self):
        """ Create a location room """
        query = self.appointment_price_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
          data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['organizationLocation']['id'], 
          variables['input']['organizationLocation'])
        self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['archived'], False)
        self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['displayPublic'], variables['input']['displayPublic'])


    def test_create_appointment_price_anon_user(self):
        """ Don't allow creating locations rooms for non-logged in users """
        query = self.appointment_price_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_appointment_price_permission_granted(self):
        """ Allow creating location rooms for users with permissions """
        query = self.appointment_price_create_mutation

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
          data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['organizationLocation']['id'], 
          variables['input']['organizationLocation'])
        self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['archived'], False)
        self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['displayPublic'], variables['input']['displayPublic'])


    def test_create_appointment_price_permission_denied(self):
        """ Check create location room permission denied error message """
        query = self.appointment_price_create_mutation
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


    def test_update_appointment_price(self):
        """ Update a location room """
        query = self.appointment_price_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateOrganizationAppointmentPrice']['organizationAppointmentPrice']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationAppointmentPrice']['organizationAppointmentPrice']['displayPublic'], variables['input']['displayPublic'])


    def test_update_appointment_price_anon_user(self):
        """ Don't allow updating location rooms for non-logged in users """
        query = self.appointment_price_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_appointment_price_permission_granted(self):
        """ Allow updating location rooms for users with permissions """
        query = self.appointment_price_update_mutation
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
        self.assertEqual(data['updateOrganizationAppointmentPrice']['organizationAppointmentPrice']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationAppointmentPrice']['organizationAppointmentPrice']['displayPublic'], variables['input']['displayPublic'])


    def test_update_appointment_price_permission_denied(self):
        """ Check update location room permission denied error message """
        query = self.appointment_price_update_mutation
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


    def test_archive_appointment_price(self):
        """ Archive a location room"""
        query = self.appointment_price_archive_mutation
        variables = self.variables_archive

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationAppointmentPrice']['organizationAppointmentPrice']['archived'], variables['input']['archived'])


    def test_archive_appointment_price_anon_user(self):
        """ Archive a location room """
        query = self.appointment_price_archive_mutation
        variables = self.variables_archive

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_appointment_price_permission_granted(self):
        """ Allow archiving locations for users with permissions """
        query = self.appointment_price_archive_mutation
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
        self.assertEqual(data['archiveOrganizationAppointmentPrice']['organizationAppointmentPrice']['archived'], variables['input']['archived'])


    def test_archive_appointment_price_permission_denied(self):
        """ Check archive location room permission denied error message """
        query = self.appointment_price_archive_mutation
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

