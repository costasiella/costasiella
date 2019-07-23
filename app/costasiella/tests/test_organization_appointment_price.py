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

        self.organization_appointment = f.OrganizationAppointmentFactory.create()
        self.organization_appointment_price = f.OrganizationAppointmentPriceFactory.create()
        self.finance_tax_rate = f.FinanceTaxRateFactory.create()


        self.variables_query_list = {
          "organizationAppointment": to_global_id('OrganizationAppointmentNode', self.organization_appointment_price.organization_appointment.pk)
        }

        self.variables_create = {
            "input": {
                "organizationAppointment": to_global_id('OrganizationAppointmentNode', self.organization_appointment.pk),
                "price": 200,
                "financeTaxRate": to_global_id('FinanceTaxRateNode', self.finance_tax_rate.pk)
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
  query OrganizationAppointmentPrices($after: String, $before: String, $organizationAppointment: ID!) {
    organizationAppointmentPrices(first: 15, before: $before, after: $after, organizationAppointment: $organizationAppointment) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationAppointment {
            id
          }
          account {
            id
            fullName
          }
          price
          priceDisplay
          financeTaxRate {
            id
            name
          }
        }
      }
    }
    organizationAppointment(id: $organizationAppointment) {
      id
      name
    }
  }
'''

        self.appointment_price_query = '''
  query OrganizationAppointmentPrice($id: ID!) {
    organizationAppointmentPrice(id:$id) {
      id
      organizationAppointment {
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
        organizationAppointment {
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
        organizationAppointment {
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
        """ Query list of appointments """
        query = self.appointment_prices_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['organizationAppointmentPrices']['edges'][0]['node']['organizationAppointment']['id'], 
            self.variables_query_list['organizationAppointment']
        )
        self.assertEqual(
            data['organizationAppointmentPrices']['edges'][0]['node']['account']['id'], 
            to_global_id('AccountNode', self.organization_appointment_price.account.id)
        )
        self.assertEqual(data['organizationAppointmentPrices']['edges'][0]['node']['price'], self.organization_appointment_price.price)
        self.assertEqual(
            data['organizationAppointmentPrices']['edges'][0]['node']['financeTaxRate']['id'], 
            to_global_id('FinanceTaxRateNode', self.organization_appointment_price.finance_tax_rate.id)
        )


    # def test_query_permision_denied(self):
    #     """ Query list of appointment rooms """
    #     query = self.appointment_prices_query
    #     appointment_price = f.OrganizationAppointmentPriceFactory.create()
    #     non_public_appointment_price = f.OrganizationAppointmentPriceFactory.build()
    #     non_public_appointment_price.organization_appointment = appointment_price.organization_appointment
    #     non_public_appointment_price.display_public = False
    #     non_public_appointment_price.save()

    #     variables = {
    #         'organizationAppointment': to_global_id('OrganizationAppointmentNode', appointment_price.organization_appointment.pk),
    #         'archived': False
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')

    #     print(data)

    #     # Public appointments only
    #     non_public_found = False
    #     for item in data['organizationAppointmentPrices']['edges']:
    #         if not item['node']['displayPublic']:
    #             non_public_found = True

    #     self.assertEqual(non_public_found, False)


    # def test_query_permision_granted(self):
    #     """ Query list of appointment rooms """
    #     query = self.appointment_prices_query
    #     appointment_price = f.OrganizationAppointmentPriceFactory.create()
    #     non_public_appointment_price = f.OrganizationAppointmentPriceFactory.build()
    #     non_public_appointment_price.organization_appointment = appointment_price.organization_appointment
    #     non_public_appointment_price.display_public = False
    #     non_public_appointment_price.save()

    #     variables = {
    #         'organizationAppointment': to_global_id('OrganizationAppointmentNode', appointment_price.organization_appointment.pk),
    #         'archived': False
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_organizationappointmentprice')
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')

    #     # List all appointments, including non public
    #     non_public_found = False
    #     for item in data['organizationAppointmentPrices']['edges']:
    #         if not item['node']['displayPublic']:
    #             non_public_found = True

    #     # Assert non public appointments are listed
    #     self.assertEqual(non_public_found, True)


    # def test_query_anon_user(self):
    #     """ Query list of appointment rooms """
    #     query = self.appointment_prices_query
    #     appointment_price = f.OrganizationAppointmentPriceFactory.create()
    #     variables = {
    #         'organizationAppointment': to_global_id('OrganizationAppointmentNode', appointment_price.organization_appointment.pk),
    #         'archived': False
    #     }

    #     executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one(self):
    #     """ Query one appointment room """   
    #     appointment_price = f.OrganizationAppointmentPriceFactory.create()

    #     # First query appointments to get node id easily
    #     node_id = to_global_id('OrganizationAppointmentPriceNode', appointment_price.pk)

    #     # Now query single appointment and check
    #     query = self.appointment_price_query
    #     executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['organizationAppointmentPrice']['organizationAppointment']['id'], 
    #       to_global_id('OrganizationAppointmentNode', appointment_price.organization_appointment.pk))
    #     self.assertEqual(data['organizationAppointmentPrice']['name'], appointment_price.name)
    #     self.assertEqual(data['organizationAppointmentPrice']['archived'], appointment_price.archived)
    #     self.assertEqual(data['organizationAppointmentPrice']['displayPublic'], appointment_price.display_public)


    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one appointment room """   
    #     appointment_price = f.OrganizationAppointmentPriceFactory.create()

    #     # First query appointments to get node id easily
    #     node_id = to_global_id('OrganizationAppointmentPriceNode', appointment_price.pk)

    #     # Now query single appointment and check
    #     query = self.appointment_price_query
    #     executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     appointment_price = f.OrganizationAppointmentPriceFactory.create()

    #     # First query appointments to get node id easily
    #     node_id = to_global_id('OrganizationAppointmentPriceNode', appointment_price.pk)

    #     # Now query single appointment and check
    #     query = self.appointment_price_query
    #     executed = execute_test_client_api_query(query, user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_organizationappointmentprice')
    #     user.user_permissions.add(permission)
    #     user.save()
    #     appointment_price = f.OrganizationAppointmentPriceFactory.create()

    #     # First query appointments to get node id easily
    #     node_id = to_global_id('OrganizationAppointmentPriceNode', appointment_price.pk)

    #     # Now query single appointment and check   
    #     query = self.appointment_price_query
    #     executed = execute_test_client_api_query(query, user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['organizationAppointmentPrice']['name'], appointment_price.name)


    # def test_create_appointment_price(self):
    #     """ Create a appointment room """
    #     query = self.appointment_price_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )

    #     data = executed.get('data')
    #     self.assertEqual(
    #       data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['organizationAppointment']['id'], 
    #       variables['input']['organizationAppointment'])
    #     self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['name'], variables['input']['name'])
    #     self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['archived'], False)
    #     self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['displayPublic'], variables['input']['displayPublic'])


    # def test_create_appointment_price_anon_user(self):
    #     """ Don't allow creating appointments rooms for non-logged in users """
    #     query = self.appointment_price_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_create_appointment_price_permission_granted(self):
    #     """ Allow creating appointment rooms for users with permissions """
    #     query = self.appointment_price_create_mutation

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(
    #       data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['organizationAppointment']['id'], 
    #       variables['input']['organizationAppointment'])
    #     self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['name'], variables['input']['name'])
    #     self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['archived'], False)
    #     self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['displayPublic'], variables['input']['displayPublic'])


    # def test_create_appointment_price_permission_denied(self):
    #     """ Check create appointment room permission denied error message """
    #     query = self.appointment_price_create_mutation
    #     variables = self.variables_create

    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_update_appointment_price(self):
    #     """ Update a appointment room """
    #     query = self.appointment_price_update_mutation
    #     variables = self.variables_update

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )

    #     data = executed.get('data')
    #     self.assertEqual(data['updateOrganizationAppointmentPrice']['organizationAppointmentPrice']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateOrganizationAppointmentPrice']['organizationAppointmentPrice']['displayPublic'], variables['input']['displayPublic'])


    # def test_update_appointment_price_anon_user(self):
    #     """ Don't allow updating appointment rooms for non-logged in users """
    #     query = self.appointment_price_update_mutation
    #     variables = self.variables_update

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_appointment_price_permission_granted(self):
    #     """ Allow updating appointment rooms for users with permissions """
    #     query = self.appointment_price_update_mutation
    #     variables = self.variables_update

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateOrganizationAppointmentPrice']['organizationAppointmentPrice']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateOrganizationAppointmentPrice']['organizationAppointmentPrice']['displayPublic'], variables['input']['displayPublic'])


    # def test_update_appointment_price_permission_denied(self):
    #     """ Check update appointment room permission denied error message """
    #     query = self.appointment_price_update_mutation
    #     variables = self.variables_update

    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_archive_appointment_price(self):
    #     """ Archive a appointment room"""
    #     query = self.appointment_price_archive_mutation
    #     variables = self.variables_archive

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveOrganizationAppointmentPrice']['organizationAppointmentPrice']['archived'], variables['input']['archived'])


    # def test_archive_appointment_price_anon_user(self):
    #     """ Archive a appointment room """
    #     query = self.appointment_price_archive_mutation
    #     variables = self.variables_archive

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_archive_appointment_price_permission_granted(self):
    #     """ Allow archiving appointments for users with permissions """
    #     query = self.appointment_price_archive_mutation
    #     variables = self.variables_archive

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveOrganizationAppointmentPrice']['organizationAppointmentPrice']['archived'], variables['input']['archived'])


    # def test_archive_appointment_price_permission_denied(self):
    #     """ Check archive appointment room permission denied error message """
    #     query = self.appointment_price_archive_mutation
    #     variables = self.variables_archive
        
    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')

