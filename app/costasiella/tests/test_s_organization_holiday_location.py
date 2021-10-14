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

from graphql_relay import to_global_id


class GQLOrganizationHolidayLocation(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.organization_holiday_location = f.OrganizationHolidayLocationFactory.create()
        self.organization_location = self.organization_holiday_location.organization_location
        self.organization_holiday = self.organization_holiday_location.organization_holiday

        self.location_id = to_global_id('OrganizationLocationNode', self.organization_location.pk)
        self.holiday_id = to_global_id('OrganizationHolidayNode', self.organization_holiday.pk)

        
        self.permission_view = 'view_organizationholidaylocation'
        self.permission_add = 'add_organizationholidaylocation'
        self.permission_change = 'change_organizationholidaylocation'
        self.permission_delete = 'delete_organizationholidaylocation'

        self.variables_create = {
            "input": {
                "organizationLocation": self.location_id,
                "organizationHoliday": self.holiday_id
            }
        }
        

        self.variables_delete = {
            "input": {
                "organizationLocation": self.location_id,
                "organizationHoliday": self.holiday_id
            }
        }


        self.holidaylocation_create_mutation = '''
  mutation AddLocationToHoliday($input: CreateOrganizationHolidayLocationInput!) {
    createOrganizationHolidayLocation(input:$input) {
      organizationHolidayLocation {
        id
        organizationLocation {
          id
          name
        }
        organizationHoliday {
          id
          name
        }
      }
    }
  }
'''

        self.holidaylocation_delete_mutation = '''
  mutation DeleteLocationFromHoliday($input: DeleteOrganizationHolidayLocationInput!) {
    deleteOrganizationHolidayLocation(input:$input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_create_holidaylocation(self):
        """ Create a holidaylocation """
        query = self.holidaylocation_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['createOrganizationHolidayLocation']['organizationHolidayLocation']['organizationLocation']['id'],
          self.location_id
        )
        self.assertEqual(
          data['createOrganizationHolidayLocation']['organizationHolidayLocation']['organizationHoliday']['id'],
          self.holiday_id
        )


    def test_create_holidaylocation_anon_user(self):
        """ Create a holidaylocation with anonymous user, check error message """
        query = self.holidaylocation_create_mutation

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_holidaylocation_permission_granted(self):
        """ Create a holidaylocation with a user having the add permission """
        query = self.holidaylocation_create_mutation
        variables = self.variables_create

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
        self.assertEqual(
          data['createOrganizationHolidayLocation']['organizationHolidayLocation']['organizationLocation']['id'],
          self.location_id
        )
        self.assertEqual(
          data['createOrganizationHolidayLocation']['organizationHolidayLocation']['organizationHoliday']['id'],
          self.holiday_id
        )


    def test_create_holidaylocation_permission_denied(self):
        """ Create a holidaylocation with a user not having the add permission """
        query = self.holidaylocation_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_delete_holidaylocation(self):
        """ Delete a holidaylocation """
        query = self.holidaylocation_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['deleteOrganizationHolidayLocation']['ok'], True)

        exists = models.OrganizationHolidayLocation.objects.exists()
        self.assertEqual(exists, False)


    def test_delete_holidaylocation_anon_user(self):
        """ Delete a holidaylocation """
        query = self.holidaylocation_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_delete_holidaylocation_permission_granted(self):
        """ Allow archiving holidaylocations for users with permissions """
        query = self.holidaylocation_delete_mutation
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
        self.assertEqual(data['deleteOrganizationHolidayLocation']['ok'], True)

        exists = models.OrganizationHolidayLocation.objects.exists()
        self.assertEqual(exists, False)


    def test_delete_holidaylocation_permission_denied(self):
        """ Check delete holidaylocation permission denied error message """
        query = self.holidaylocation_delete_mutation
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

