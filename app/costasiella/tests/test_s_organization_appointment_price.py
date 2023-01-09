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

        self.permission_view_account = 'view_account'
        self.permission_view_appointment = 'view_organizationappointment'
        self.permission_view_finance_taxrate = 'view_financetaxrate'
        self.permission_view = 'view_organizationappointmentprice'
        self.permission_add = 'add_organizationappointmentprice'
        self.permission_change = 'change_organizationappointmentprice'
        self.permission_delete = 'delete_organizationappointmentprice'

        self.instructor = f.Instructor2Factory.create()
        self.organization_appointment = f.OrganizationAppointmentFactory.create()
        self.organization_appointment_price = f.OrganizationAppointmentPriceFactory.create()
        self.finance_tax_rate = f.FinanceTaxRateFactory.create()


        self.variables_query_list = {
          "organizationAppointment": to_global_id('OrganizationAppointmentNode', self.organization_appointment_price.organization_appointment.pk)
        }

        self.variables_create = {
            "input": {
                "account": to_global_id('AccountNode', self.instructor.pk),
                "organizationAppointment": to_global_id('OrganizationAppointmentNode', self.organization_appointment.pk),
                "price": "200",
                "financeTaxRate": to_global_id('FinanceTaxRateNode', self.finance_tax_rate.pk)
            }
        }

        self.variables_update = {
            "input": {
                "id": to_global_id('OrganizationAppointmentPriceNode', self.organization_appointment_price.pk),
                "account": to_global_id('AccountNode', self.instructor.pk),
                "price": "9876",
                "financeTaxRate": to_global_id('FinanceTaxRateNode', self.finance_tax_rate.pk)
            }
        }

        self.variables_delete = {
            "input": {
                "id": to_global_id('OrganizationAppointmentPriceNode', self.organization_appointment_price.pk),
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
      price
      organizationAppointment {
        id
      }
      account {
        id
        fullName
      }
      financeTaxRate {
        id
        name
      }
    }
  }
'''

        self.appointment_price_create_mutation = ''' 
  mutation CreateOrganizationAppointmentPrice($input: CreateOrganizationAppointmentPriceInput!) {
    createOrganizationAppointmentPrice(input: $input) {
      organizationAppointmentPrice {
        id
        account {
          id
          fullName
        }
        organizationAppointment {
          id
          name
        }
        price
        financeTaxRate {
          id
          name
        }
      }
    }
  }
'''

        self.appointment_price_update_mutation = '''
  mutation UpdateOrganizationAppointmentPrice($input: UpdateOrganizationAppointmentPriceInput!) {
    updateOrganizationAppointmentPrice(input: $input) {
      organizationAppointmentPrice {
        id
        account {
          id
          fullName
        }
        organizationAppointment {
          id
          name
        }
        price
        financeTaxRate {
          id
          name
        }
      }
    }
  }
'''

        self.appointment_price_delete_mutation = '''
  mutation DeleteOrganizationAppointmentPrice($input: DeleteOrganizationAppointmentPriceInput!) {
    deleteOrganizationAppointmentPrice(input: $input) {
      ok
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
        self.assertEqual(data['organizationAppointmentPrices']['edges'][0]['node']['price'],
                         format(self.organization_appointment_price.price, ".2f"))
        self.assertEqual(
            data['organizationAppointmentPrices']['edges'][0]['node']['financeTaxRate']['id'], 
            to_global_id('FinanceTaxRateNode', self.organization_appointment_price.finance_tax_rate.id)
        )

    def test_query_permission_denied(self):
        """ Query list of appointment prices """
        query = self.appointment_prices_query

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of appointment prices """
        query = self.appointment_prices_query


        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationappointmentprice')
        user.user_permissions.add(permission)
        # Account
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        # Appointment
        permission = Permission.objects.get(codename=self.permission_view_appointment)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        data = executed.get('data')

        # See if we're getting any data back
        self.assertEqual(
            data['organizationAppointmentPrices']['edges'][0]['node']['account']['id'], 
            to_global_id('AccountNode', self.organization_appointment_price.account.id)
        )

    def test_query_anon_user(self):
        """ Query list of appointment prices """
        query = self.appointment_prices_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one appointment price """   
        # First query appointments to get node id easily
        node_id = to_global_id('OrganizationAppointmentPriceNode', self.organization_appointment_price.pk)

        # Now query single appointment price and check
        query = self.appointment_price_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')

        self.assertEqual(data['organizationAppointmentPrice']['organizationAppointment']['id'], 
          to_global_id('OrganizationAppointmentNode', self.organization_appointment_price.organization_appointment.pk))
        self.assertEqual(data['organizationAppointmentPrice']['account']['id'], 
          to_global_id('AccountNode', self.organization_appointment_price.account.pk))
        self.assertEqual(data['organizationAppointmentPrice']['price'],
                         format(self.organization_appointment_price.price, ".2f"))
        self.assertEqual(data['organizationAppointmentPrice']['financeTaxRate']['id'], 
          to_global_id('FinanceTaxRateNode', self.organization_appointment_price.finance_tax_rate.id))

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one appointment price """   
        # First query appointments to get node id easily
        node_id = to_global_id('OrganizationAppointmentPriceNode', self.organization_appointment_price.pk)

        # Now query single appointment and check
        query = self.appointment_price_query
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()

        # First query appointments to get node id easily
        node_id = to_global_id('OrganizationAppointmentPriceNode', self.organization_appointment_price.pk)

        # Now query single appointment and check
        query = self.appointment_price_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationappointmentprice')
        user.user_permissions.add(permission)
        # Account
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        # Appointment
        permission = Permission.objects.get(codename=self.permission_view_appointment)
        user.user_permissions.add(permission)
        user.save()

        # First query appointments to get node id easily
        node_id = to_global_id('OrganizationAppointmentPriceNode', self.organization_appointment_price.pk)

        # Now query single appointment and check   
        query = self.appointment_price_query
        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationAppointmentPrice']['price'],
                         format(self.organization_appointment_price.price, ".2f"))

    def test_create_appointment_price(self):
        """ Create a appointment price """
        query = self.appointment_price_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
          data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['account']['id'], 
          variables['input']['account'])
        self.assertEqual(
          data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['organizationAppointment']['id'], 
          variables['input']['organizationAppointment'])
        self.assertEqual(
          data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['financeTaxRate']['id'], 
          variables['input']['financeTaxRate'])
        self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['price'], variables['input']['price'])


    def test_create_appointment_price_anon_user(self):
        """ Don't allow creating appointments rooms for non-logged in users """
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
        """ Allow creating appointment prices for users with permissions """
        query = self.appointment_price_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        # Account
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        # Appointment
        permission = Permission.objects.get(codename=self.permission_view_appointment)
        user.user_permissions.add(permission)
        # Tax rate
        permission = Permission.objects.get(codename=self.permission_view_finance_taxrate)
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
          data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['organizationAppointment']['id'], 
          variables['input']['organizationAppointment'])
        self.assertEqual(
          data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['account']['id'], 
          variables['input']['account'])
        self.assertEqual(
          data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['financeTaxRate']['id'], 
          variables['input']['financeTaxRate'])
        self.assertEqual(data['createOrganizationAppointmentPrice']['organizationAppointmentPrice']['price'], variables['input']['price'])


    def test_create_appointment_price_permission_denied(self):
        """ Check create appointment price permission denied error message """
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
        """ Update a appointment price """
        query = self.appointment_price_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
          data['updateOrganizationAppointmentPrice']['organizationAppointmentPrice']['account']['id'], 
          variables['input']['account'])
        self.assertEqual(
          data['updateOrganizationAppointmentPrice']['organizationAppointmentPrice']['financeTaxRate']['id'], 
          variables['input']['financeTaxRate'])
        self.assertEqual(data['updateOrganizationAppointmentPrice']['organizationAppointmentPrice']['price'], variables['input']['price'])


    def test_update_appointment_price_anon_user(self):
        """ Don't allow updating appointment prices for non-logged in users """
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
        """ Allow updating appointment prices for users with permissions """
        query = self.appointment_price_update_mutation
        variables = self.variables_update

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        # Account
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        # Appointment
        permission = Permission.objects.get(codename=self.permission_view_appointment)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
          data['updateOrganizationAppointmentPrice']['organizationAppointmentPrice']['account']['id'], 
          variables['input']['account']
        )


    def test_update_appointment_price_permission_denied(self):
        """ Check update appointment price permission denied error message """
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


    def test_delete_appointment_price(self):
        """ Delete a appointment price"""
        query = self.appointment_price_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteOrganizationAppointmentPrice']['ok'], True)


    def test_delete_appointment_price_anon_user(self):
        """ Delete a appointment price """
        query = self.appointment_price_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_delete_appointment_price_permission_granted(self):
        """ Allow archiving appointments for users with permissions """
        query = self.appointment_price_delete_mutation
        variables = self.variables_delete

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
        self.assertEqual(data['deleteOrganizationAppointmentPrice']['ok'], True)


    def test_delete_appointment_price_permission_denied(self):
        """ Check delete appointment price permission denied error message """
        query = self.appointment_price_delete_mutation
        variables = self.variables_delete
        
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

