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


class GQLOrganizationHoliday(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationholiday'
        self.permission_add = 'add_organizationholiday'
        self.permission_change = 'change_organizationholiday'
        self.permission_delete = 'delete_organizationholiday'

        self.variables_create = {
            "input": {
                "name": "New holiday",
                "description": "Holiday description",
                "dateStart": "2020-01-01",
                "dateEnd": "2050-01-01",
                "classes": True
            }
        }
        
        self.variables_update = {
            "input": {
                "name": "Updated holiday",
                "description": "Updated description",
                "dateStart": "2020-01-01",
                "dateEnd": "2050-01-01",
                "classes": True
            }
        }

        self.variable_delete = {
            "input": {}
        }

        self.holidays_query = '''
  query OrganizationHolidays($after: String, $before: String) {
    organizationHolidays(first: 15, before: $before, after: $after) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          name
          description
          dateStart
          dateEnd
          classes
          organizationLocations {
            edges {
              node {
                id
                name
              }
            }
          }
        }
      }
    }
  }
'''

        self.holiday_query = '''
  query OrganizationHoliday($id: ID!) {
    organizationHoliday(id:$id) {
      id
      name
      description
      dateStart
      dateEnd
      classes
    }
  }
'''

        self.holiday_create_mutation = '''
  mutation CreateOrganizationHoliday($input:CreateOrganizationHolidayInput!) {
    createOrganizationHoliday(input: $input) {
      organizationHoliday {
        id
        name
        description
        dateStart
        dateEnd
        classes
      }
    }
  }
'''

        self.holiday_update_mutation = '''
  mutation UpdateOrganizationHoliday($input: UpdateOrganizationHolidayInput!) {
    updateOrganizationHoliday(input: $input) {
      organizationHoliday {
        id
        name
        description
        dateStart
        dateEnd
        classes
      }
    }
  }
'''

        self.holiday_delete_mutation = '''
  mutation DeleteOrganizationHoliday($input: DeleteOrganizationHolidayInput!) {
    deleteOrganizationHoliday(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of holidays """
        query = self.holidays_query
        holiday = f.OrganizationHolidayFactory.create()

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')
        item = data['organizationHolidays']['edges'][0]['node']
        self.assertEqual(item['name'], holiday.name)
        self.assertEqual(item['description'], holiday.description)
        self.assertEqual(item['dateStart'], str(holiday.date_start))
        self.assertEqual(item['dateEnd'], str(holiday.date_end))
        self.assertEqual(item['classes'], holiday.classes)

    def test_query_permission_denied(self):
        """ Query list of holidays as user without permissions """
        query = self.holidays_query
        holiday = f.OrganizationHolidayFactory.create()

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of holidays with view permission """
        query = self.holidays_query
        holiday = f.OrganizationHolidayFactory.create()

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user)
        data = executed.get('data')
        item = data['organizationHolidays']['edges'][0]['node']
        self.assertEqual(item['name'], holiday.name)

    def test_query_anon_user(self):
        """ Query list of holidays as anon user """
        query = self.holidays_query
        holiday = f.OrganizationHolidayFactory.create()

        executed = execute_test_client_api_query(query, self.anon_user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one holiday """
        holiday = f.OrganizationHolidayFactory.create()

        # First query holidays to get node id easily
        node_id = to_global_id("OrganizationHolidayNode", holiday.pk)

        # Now query single holiday and check
        query = self.holiday_query
        executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationHoliday']['name'], holiday.name)
        self.assertEqual(data['organizationHoliday']['description'], holiday.description)
        self.assertEqual(data['organizationHoliday']['dateStart'], str(holiday.date_start))
        self.assertEqual(data['organizationHoliday']['dateEnd'], str(holiday.date_end))
        self.assertEqual(data['organizationHoliday']['classes'], holiday.classes)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one holiday """
        query = self.holiday_query
        holiday = f.OrganizationHolidayFactory.create()
        node_id = to_global_id("OrganizationHolidayNode", holiday.pk)
        executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        query = self.holiday_query

        user = f.RegularUserFactory.create()
        holiday = f.OrganizationHolidayFactory.create()
        node_id = to_global_id("OrganizationHolidayNode", holiday.pk)

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        query = self.holiday_query
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationholiday')
        user.user_permissions.add(permission)
        user.save()

        holiday = f.OrganizationHolidayFactory.create()
        node_id = to_global_id("OrganizationHolidayNode", holiday.pk)

        executed = execute_test_client_api_query(query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['organizationHoliday']['name'], holiday.name)

    def test_create_holiday(self):
        """ Create a holiday """
        query = self.holiday_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationHoliday']['organizationHoliday']['name'],
                         variables['input']['name'])
        self.assertEqual(data['createOrganizationHoliday']['organizationHoliday']['description'],
                         variables['input']['description'])
        self.assertEqual(data['createOrganizationHoliday']['organizationHoliday']['dateStart'],
                         variables['input']['dateStart'])
        self.assertEqual(data['createOrganizationHoliday']['organizationHoliday']['dateEnd'],
                         variables['input']['dateEnd'])
        self.assertEqual(data['createOrganizationHoliday']['organizationHoliday']['classes'],
                         variables['input']['classes'])

    def test_create_holiday_anon_user(self):
        """ Create a holiday with anonymous user, check error message """
        query = self.holiday_create_mutation

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=self.variables_create
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_holiday_permission_granted(self):
        """ Create a holiday with a user having the add permission """
        query = self.holiday_create_mutation
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
        self.assertEqual(data['createOrganizationHoliday']['organizationHoliday']['name'],
                         variables['input']['name'])

    def test_create_holiday_permission_denied(self):
        """ Create a holiday with a user not having the add permission """
        query = self.holiday_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=self.variables_create
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_holiday(self):
        """ Update a holiday as admin user """
        query = self.holiday_update_mutation
        holiday = f.OrganizationHolidayFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationHolidayNode", holiday.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganizationHoliday']['organizationHoliday']['name'],
                         variables['input']['name'])
        self.assertEqual(data['updateOrganizationHoliday']['organizationHoliday']['description'],
                         variables['input']['description'])
        self.assertEqual(data['updateOrganizationHoliday']['organizationHoliday']['dateStart'],
                         variables['input']['dateStart'])
        self.assertEqual(data['updateOrganizationHoliday']['organizationHoliday']['dateEnd'],
                         variables['input']['dateEnd'])
        self.assertEqual(data['updateOrganizationHoliday']['organizationHoliday']['classes'],
                         variables['input']['classes'])

    def test_update_holiday_anon_user(self):
        """ Update a holiday as anonymous user """
        query = self.holiday_update_mutation
        holiday = f.OrganizationHolidayFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationHolidayNode", holiday.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_holiday_permission_granted(self):
        """ Update a holiday as user with permission """
        query = self.holiday_update_mutation
        holiday = f.OrganizationHolidayFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationHolidayNode", holiday.pk)

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
        self.assertEqual(data['updateOrganizationHoliday']['organizationHoliday']['name'],
                         variables['input']['name'])

    def test_update_holiday_permission_denied(self):
        """ Update a holiday as user without permissions """
        query = self.holiday_update_mutation
        holiday = f.OrganizationHolidayFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationHolidayNode", holiday.pk)

        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_holiday(self):
        """ Delete a holiday """
        query = self.holiday_delete_mutation
        holiday = f.OrganizationHolidayFactory.create()
        variables = self.variable_delete
        variables['input']['id'] = to_global_id("OrganizationHolidayNode", holiday.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteOrganizationHoliday']['ok'], True)

    def test_delete_holiday_anon_user(self):
        """ Delete a holiday """
        query = self.holiday_delete_mutation
        holiday = f.OrganizationHolidayFactory.create()
        variables = self.variable_delete
        variables['input']['id'] = to_global_id("OrganizationHolidayNode", holiday.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_holiday_permission_granted(self):
        """ Allow deleting holidays for users with permissions """
        query = self.holiday_delete_mutation
        holiday = f.OrganizationHolidayFactory.create()
        variables = self.variable_delete
        variables['input']['id'] = to_global_id("OrganizationHolidayNode", holiday.pk)

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
        self.assertEqual(data['deleteOrganizationHoliday']['ok'], True)

    def test_delete_holiday_permission_denied(self):
        """ Check delete holiday permission denied error message """
        query = self.holiday_delete_mutation
        holiday = f.OrganizationHolidayFactory.create()
        variables = self.variable_delete
        variables['input']['id'] = to_global_id("OrganizationHolidayNode", holiday.pk)

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
