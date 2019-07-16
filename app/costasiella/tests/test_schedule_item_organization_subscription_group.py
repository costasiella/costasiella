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


class GQLScheduleItemOrganizationSubscriptionGroup(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleitemorganizationsubscriptiongroup'
        self.permission_add = 'add_scheduleitemorganizationsubscriptiongroup'
        self.permission_change = 'change_scheduleitemorganizationsubscriptiongroup'
        self.permission_delete = 'delete_scheduleitemorganizationsubscriptiongroup'

        self.variables_update = {
            "input": {
                "enroll": True,
                "shopBook": True,
                "attend": True
            }
        }


        self.schedule_item_organization_subscription_groups_query = '''
  query ScheduleItemTeachers($after: String, $before: String, $scheduleItem: ID!) {
    scheduleItemTeachers(first: 15, before: $before, after: $after, scheduleItem: $scheduleItem) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          account {
            id
            fullName
          }
          role
          account2 {
            id
            fullName
          }
          role2
          dateStart
          dateEnd       
        }
      }
    }
  }
'''

        self.schedule_item_organization_subscription_group_query = '''
  query ScheduleItemTeacher($id: ID!) {
    scheduleItemTeacher(id: $id) {
      id
      account {
        id
        fullName
      }
      role
      account2 {
        id
        fullName
      }
      role2
      dateStart
      dateEnd       
    }
  }
'''

        self.schedule_item_organization_subscription_group_create_mutation = ''' 
  mutation CreateScheduleItemTeacher($input:CreateScheduleItemTeacherInput!) {
    createScheduleItemTeacher(input:$input) {
      scheduleItemTeacher {
        id
        account {
          id
          fullName
        }
        role
        account2 {
          id
          fullName
        }
        role2
        dateStart
        dateEnd       
      }
    }
  }
'''

        self.schedule_item_organization_subscription_group_update_mutation = '''
  mutation UpdateScheduleItemTeacher($input: UpdateScheduleItemTeacherInput!) {
    updateScheduleItemTeacher(input:$input) {
      scheduleItemTeacher {
        id
        account {
          id
          fullName
        }
        role
        account2 {
          id
          fullName
        }
        role2
        dateStart
        dateEnd       
      }
    }
  }
'''

        self.schedule_item_organization_subscription_group_delete_mutation = '''
  mutation DeleteScheduleClassTeacher($input: DeleteScheduleItemTeacherInput!) {
    deleteScheduleItemTeacher(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of schedule item organization_subscription_groups """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()

        query = self.schedule_item_organization_subscription_groups_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_organization_subscription_group.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemTeachers']['edges'][0]['node']['account']['id'],
          to_global_id('AccountNode', schedule_item_organization_subscription_group.account.pk)
        )
        self.assertEqual(data['scheduleItemTeachers']['edges'][0]['node']['role'], schedule_item_organization_subscription_group.role)
        self.assertEqual(
          data['scheduleItemTeachers']['edges'][0]['node']['account2']['id'],
          to_global_id('AccountNode', schedule_item_organization_subscription_group.account_2.pk)
        )
        self.assertEqual(data['scheduleItemTeachers']['edges'][0]['node']['role2'], schedule_item_organization_subscription_group.role_2)
        self.assertEqual(data['scheduleItemTeachers']['edges'][0]['node']['dateStart'], str(schedule_item_organization_subscription_group.date_start))
        self.assertEqual(data['scheduleItemTeachers']['edges'][0]['node']['dateEnd'], schedule_item_organization_subscription_group.date_end)


    def test_query_permision_denied(self):
        """ Query list of schedule item organization_subscription_groups """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()

        query = self.schedule_item_organization_subscription_groups_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_organization_subscription_group.schedule_item.pk)
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permision_granted(self):
        """ Query list of schedule item organization_subscription_groups """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()

        query = self.schedule_item_organization_subscription_groups_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_organization_subscription_group.schedule_item.pk)
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_scheduleitemorganizationsubscriptiongroup')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemTeachers']['edges'][0]['node']['account']['id'],
          to_global_id('AccountNode', schedule_item_organization_subscription_group.account.pk)
        )


    def test_query_anon_user(self):
        """ Query list of schedule item organization_subscription_groups """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()

        query = self.schedule_item_organization_subscription_groups_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_organization_subscription_group.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query list of schedule item organization_subscription_group """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_organization_subscription_group_query

        variables = {
          "id": to_global_id('ScheduleItemTeacherNode', schedule_item_organization_subscription_group.id),
        }
       
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemTeacher']['account']['id'],
          to_global_id('AccountNode', schedule_item_organization_subscription_group.account.pk)
        )
        self.assertEqual(data['scheduleItemTeacher']['role'], schedule_item_organization_subscription_group.role)
        self.assertEqual(
          data['scheduleItemTeacher']['account2']['id'],
          to_global_id('AccountNode', schedule_item_organization_subscription_group.account_2.pk)
        )
        self.assertEqual(data['scheduleItemTeacher']['role2'], schedule_item_organization_subscription_group.role_2)
        self.assertEqual(data['scheduleItemTeacher']['dateStart'], str(schedule_item_organization_subscription_group.date_start))
        self.assertEqual(data['scheduleItemTeacher']['dateEnd'], schedule_item_organization_subscription_group.date_end)


    def test_query_one_anon_user(self):
        """ Query list of schedule item organization_subscription_group """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_organization_subscription_group_query

        variables = {
          "id": to_global_id('ScheduleItemTeacherNode', schedule_item_organization_subscription_group.id),
        }
       
        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_organization_subscription_group_query

        variables = {
          "id": to_global_id('ScheduleItemTeacherNode', schedule_item_organization_subscription_group.id),
        }
       
        # Now query single schedule item organization_subscription_group and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_scheduleitemorganizationsubscriptiongroup')
        user.user_permissions.add(permission)
        user.save()
        
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_organization_subscription_group_query

        variables = {
          "id": to_global_id('ScheduleItemTeacherNode', schedule_item_organization_subscription_group.id),
        }

        # Now query single schedule item organization_subscription_group and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
          data['scheduleItemTeacher']['account']['id'],
          to_global_id('AccountNode', schedule_item_organization_subscription_group.account.pk)
        )


    def test_create_schedule_item_organization_subscription_group(self):
        """ Create schedule item organization_subscription_group """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        organization_subscription_group = f.TeacherFactory.create()
        organization_subscription_group2 = f.Teacher2Factory.create()

        query = self.schedule_item_organization_subscription_group_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('scheduleItemNode', schedule_class.pk)
        variables['input']['account'] = to_global_id('AccountNode', organization_subscription_group.pk)
        variables['input']['account2'] = to_global_id('AccountNode', organization_subscription_group2.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['account']['id'], variables['input']['account'])
        self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['role'], variables['input']['role'])
        self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['account2']['id'], variables['input']['account2'])
        self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['role2'], variables['input']['role2'])
        self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['dateEnd'], variables['input']['dateEnd'])


    def test_create_schedule_item_organization_subscription_group_anon_user(self):
        """ Don't allow creating schedule item organization_subscription_group for non-logged in users """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        organization_subscription_group = f.TeacherFactory.create()
        organization_subscription_group2 = f.Teacher2Factory.create()

        query = self.schedule_item_organization_subscription_group_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('scheduleItemNode', schedule_class.pk)
        variables['input']['account'] = to_global_id('AccountNode', organization_subscription_group.pk)
        variables['input']['account2'] = to_global_id('AccountNode', organization_subscription_group2.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_schedule_item_organization_subscription_group_permission_granted(self):
        """ Allow creating schedule item organization_subscription_groups for users with permissions """
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        organization_subscription_group = f.TeacherFactory.create()
        organization_subscription_group2 = f.Teacher2Factory.create()

        query = self.schedule_item_organization_subscription_group_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('scheduleItemNode', schedule_class.pk)
        variables['input']['account'] = to_global_id('AccountNode', organization_subscription_group.pk)
        variables['input']['account2'] = to_global_id('AccountNode', organization_subscription_group2.pk)

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['account']['id'], variables['input']['account'])


    def test_create_schedule_item_organization_subscription_group_permission_denied(self):
        """ Check create schedule item organization_subscription_group permission denied error message """
        # Create regular user
        user = f.RegularUserFactory.create()

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        organization_subscription_group = f.TeacherFactory.create()
        organization_subscription_group2 = f.Teacher2Factory.create()

        query = self.schedule_item_organization_subscription_group_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('scheduleItemNode', schedule_class.pk)
        variables['input']['account'] = to_global_id('AccountNode', organization_subscription_group.pk)
        variables['input']['account2'] = to_global_id('AccountNode', organization_subscription_group2.pk)

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_update_schedule_item_organization_subscription_group(self):
        """ Update schedule item organization_subscription_group """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()

        query = self.schedule_item_organization_subscription_group_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_organization_subscription_group.pk)
        variables['input']['account'] = to_global_id('AccountNode', schedule_item_organization_subscription_group.account_2.pk)
        variables['input']['account2'] = to_global_id('AccountNode', schedule_item_organization_subscription_group.account.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['account']['id'], variables['input']['account'])
        self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['role'], variables['input']['role'])
        self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['account2']['id'], variables['input']['account2'])
        self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['role2'], variables['input']['role2'])
        self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['dateEnd'], variables['input']['dateEnd'])


    def test_update_schedule_item_organization_subscription_group_anon_user(self):
        """ Don't allow updating schedule item organization_subscription_groups for non-logged in users """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_organization_subscription_group_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_organization_subscription_group.pk)
        variables['input']['account'] = to_global_id('AccountNode', schedule_item_organization_subscription_group.account_2.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_schedule_item_organization_subscription_group_permission_granted(self):
        """ Allow updating schedule item organization_subscription_group for users with permissions """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_organization_subscription_group_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_organization_subscription_group.pk)
        variables['input']['account'] = to_global_id('AccountNode', schedule_item_organization_subscription_group.account_2.pk)

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
        self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['role'], variables['input']['role'])


    def test_update_schedule_item_organization_subscription_group_permission_denied(self):
        """ Check update schedule item organization_subscription_group permission denied error message """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_organization_subscription_group_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_organization_subscription_group.pk)
        variables['input']['account'] = to_global_id('AccountNode', schedule_item_organization_subscription_group.account_2.pk)

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


    def test_delete_schedule_item_organization_subscription_group(self):
        """ Delete a schedule item organization_subscription_group """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_organization_subscription_group_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_organization_subscription_group.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        
        self.assertEqual(data['deleteScheduleItemTeacher']['ok'], True)

        exists = models.ScheduleItemTeacher.objects.exists()
        self.assertEqual(exists, False)


    def test_delete_schedule_item_organization_subscription_group_anon_user(self):
        """ Don't allow deleting schedule item organization_subscription_groups for non logged in users """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_organization_subscription_group_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_organization_subscription_group.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_delete_schedule_item_organization_subscription_group_permission_granted(self):
        """ Allow deleting schedule item organization_subscription_groups for users with permissions """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_organization_subscription_group_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_organization_subscription_group.pk)

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
        self.assertEqual(data['deleteScheduleItemTeacher']['ok'], True)


    def test_delete_schedule_item_organization_subscription_group_permission_denied(self):
        """ Check delete schedule item organization_subscription_group permission denied error message """
        schedule_item_organization_subscription_group = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_organization_subscription_group_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_organization_subscription_group.pk)
        
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

