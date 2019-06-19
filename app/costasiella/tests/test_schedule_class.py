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


class GQLScheduleClass(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['initial_data.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleclass'
        self.permission_add = 'add_scheduleclass'
        self.permission_change = 'change_scheduleclass'
        self.permission_delete = 'delete_scheduleclass'

        self.variables_create = {
            "input": {
                "name": "New scheduleclass",
                "code" : "123"
            }
        }

        self.variables_update = {
            "input": {
                "name": "Updated scheduleclass",
                "code" : "987"
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.scheduleclasss_query = '''
  query ScheduleClasss($after: String, $before: String, $archived: Boolean) {
    scheduleClasses(first: 15, before: $before, after: $after, archived: $archived) {
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
          systemMethod
          name
          code
        }
      }
    }
  }
'''

        self.scheduleclass_query = '''
  query ScheduleClass($id: ID!) {
    scheduleClass(id:$id) {
      id
      name
      code
      archived
    }
  }
'''

        self.scheduleclass_create_mutation = ''' 
  mutation CreateScheduleClass($input:CreateScheduleClassInput!) {
    createScheduleClass(input: $input) {
      scheduleClass{
        id
        archived
        name
        code
      }
    }
  }
'''

        self.scheduleclass_update_mutation = '''
  mutation UpdateScheduleClass($input: UpdateScheduleClassInput!) {
    updateScheduleClass(input: $input) {
      scheduleClass {
        id
        name
        code
      }
    }
  }
'''

        self.scheduleclass_archive_mutation = '''
  mutation ArchiveScheduleClass($input: ArchiveScheduleClassInput!) {
    archiveScheduleClass(input: $input) {
      scheduleClass {
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
        """ Query list of scheduleclasss """
        query = self.scheduleclasss_query
        # The payment method "Cash" from the fixtures will be listed first
        scheduleclass = models.ScheduleItem.objects.get(pk=101)
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['scheduleClasses']['edges'][0]['node']['name'], scheduleclass.name)
        self.assertEqual(data['scheduleClasses']['edges'][0]['node']['archived'], scheduleclass.archived)
        self.assertEqual(data['scheduleClasses']['edges'][0]['node']['systemMethod'], scheduleclass.system_method)
        self.assertEqual(data['scheduleClasses']['edges'][0]['node']['code'], scheduleclass.code)


    def test_query_permision_denied(self):
        """ Query list of scheduleclasss - check permission denied """
        query = self.scheduleclasss_query
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permision_granted(self):
        """ Query list of scheduleclasss with view permission """
        query = self.scheduleclasss_query
        # The payment method "Cash" from the fixtures will be listed first
        scheduleclass = models.ScheduleItem.objects.get(pk=101)
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_scheduleclass')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all scheduleclasss
        self.assertEqual(data['scheduleClasses']['edges'][0]['node']['name'], scheduleclass.name)
        self.assertEqual(data['scheduleClasses']['edges'][0]['node']['archived'], scheduleclass.archived)
        self.assertEqual(data['scheduleClasses']['edges'][0]['node']['code'], scheduleclass.code)


    def test_query_anon_user(self):
        """ Query list of scheduleclasss - anon user """
        query = self.scheduleclasss_query
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one scheduleclass as admin """   
        # The payment method "Cash" from the fixtures
        scheduleclass = models.ScheduleItem.objects.get(pk=101)
        node_id = to_global_id('ScheduleItemNode', 101)

        # Now query single scheduleclass and check
        executed = execute_test_client_api_query(self.scheduleclass_query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['scheduleClass']['name'], scheduleclass.name)
        self.assertEqual(data['scheduleClass']['archived'], scheduleclass.archived)
        self.assertEqual(data['scheduleClass']['code'], scheduleclass.code)


    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one glacount """   
        scheduleclass = models.ScheduleItem.objects.get(pk=101)
        node_id = to_global_id('ScheduleItemNode', 101)

        # Now query single scheduleclass and check
        executed = execute_test_client_api_query(self.scheduleclass_query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        node_id = to_global_id('ScheduleItemNode', 101)

        # Now query single scheduleclass and check
        executed = execute_test_client_api_query(self.scheduleclass_query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_scheduleclass')
        user.user_permissions.add(permission)
        user.save()
        # Payment method Cash from fixtures
        scheduleclass = models.ScheduleItem.objects.get(pk=101)
        node_id = to_global_id('ScheduleItemNode', 101)

        # Now query single location and check   
        executed = execute_test_client_api_query(self.scheduleclass_query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['scheduleClass']['name'], scheduleclass.name)


    def test_create_scheduleclass(self):
        """ Create a scheduleclass """
        query = self.scheduleclass_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createScheduleClass']['scheduleClass']['name'], variables['input']['name'])
        self.assertEqual(data['createScheduleClass']['scheduleClass']['archived'], False)
        self.assertEqual(data['createScheduleClass']['scheduleClass']['code'], variables['input']['code'])


    def test_create_scheduleclass_anon_user(self):
        """ Don't allow creating scheduleclasss for non-logged in users """
        query = self.scheduleclass_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_location_permission_granted(self):
        """ Allow creating scheduleclasss for users with permissions """
        query = self.scheduleclass_create_mutation
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
        self.assertEqual(data['createScheduleClass']['scheduleClass']['name'], variables['input']['name'])
        self.assertEqual(data['createScheduleClass']['scheduleClass']['archived'], False)
        self.assertEqual(data['createScheduleClass']['scheduleClass']['code'], variables['input']['code'])


    def test_create_scheduleclass_permission_denied(self):
        """ Check create scheduleclass permission denied error message """
        query = self.scheduleclass_create_mutation
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


    def test_update_scheduleclass(self):
        """ Update a scheduleclass """
        query = self.scheduleclass_update_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateScheduleClass']['scheduleClass']['name'], variables['input']['name'])
        self.assertEqual(data['updateScheduleClass']['scheduleClass']['code'], variables['input']['code'])


    def test_update_scheduleclass_anon_user(self):
        """ Don't allow updating scheduleclasss for non-logged in users """
        query = self.scheduleclass_update_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_scheduleclass_permission_granted(self):
        """ Allow updating scheduleclasss for users with permissions """
        query = self.scheduleclass_update_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

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
        self.assertEqual(data['updateScheduleClass']['scheduleClass']['name'], variables['input']['name'])
        self.assertEqual(data['updateScheduleClass']['scheduleClass']['code'], variables['input']['code'])


    def test_update_scheduleclass_permission_denied(self):
        """ Check update scheduleclass permission denied error message """
        query = self.scheduleclass_update_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

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


    def test_archive_scheduleclass(self):
        """ Archive a scheduleclass """
        query = self.scheduleclass_archive_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveScheduleClass']['scheduleClass']['archived'], variables['input']['archived'])


    def test_unable_to_archive_system_scheduleclass(self):
        """ Test that we can't archive a sytem payment method """
        query = self.scheduleclass_archive_mutation
        # This is the "Cash" system payment method from the fixtures
        scheduleclass = models.ScheduleItem.objects.get(pk=101)
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Unable to archive, this is a system method!')


    def test_archive_scheduleclass_anon_user(self):
        """ Archive scheduleclass denied for anon user """
        query = self.scheduleclass_archive_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_scheduleclass_permission_granted(self):
        """ Allow archiving scheduleclasss for users with permissions """
        query = self.scheduleclass_archive_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)

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
        self.assertEqual(data['archiveScheduleClass']['scheduleClass']['archived'], variables['input']['archived'])


    def test_archive_scheduleclass_permission_denied(self):
        """ Check archive scheduleclass permission denied error message """
        query = self.scheduleclass_archive_mutation
        scheduleclass = f.SchedulePublicWeeklyClassFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id('ScheduleItemNode', scheduleclass.pk)
        
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

