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


class GQLScheduleItemAccount(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_account = 'view_account'
        self.permission_view = 'view_scheduleitemaccount'
        self.permission_add = 'add_scheduleitemaccount'
        self.permission_change = 'change_scheduleitemaccount'
        self.permission_delete = 'delete_scheduleitemaccount'

        self.variables_create = {
            "input": {
                "role": "SUB",
                "role2": "ASSISTANT",
                "dateStart": '2019-01-01',
                "dateEnd": '2019-12-31',
            }
        }

        self.variables_update = {
            "input": {
                "role": "SUB",
                "role2": "ASSISTANT",
                "dateStart": '2019-01-01',
                "dateEnd": '2019-12-31',
            }
        }

        self.variables_delete = {
            "input": {}
        }

        self.schedule_item_accounts_query = '''
  query ScheduleItemAccounts($after: String, $before: String, $scheduleItem: ID!) {
    scheduleItemAccounts(first: 15, before: $before, after: $after, scheduleItem: $scheduleItem) {
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

        self.schedule_item_account_query = '''
  query ScheduleItemAccount($id: ID!) {
    scheduleItemAccount(id: $id) {
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

        self.schedule_item_account_create_mutation = ''' 
  mutation CreateScheduleItemAccount($input:CreateScheduleItemAccountInput!) {
    createScheduleItemAccount(input:$input) {
      scheduleItemAccount {
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

        self.schedule_item_account_update_mutation = '''
  mutation UpdateScheduleItemAccount($input: UpdateScheduleItemAccountInput!) {
    updateScheduleItemAccount(input:$input) {
      scheduleItemAccount {
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

        self.schedule_item_account_delete_mutation = '''
  mutation DeleteScheduleClassAccount($input: DeleteScheduleItemAccountInput!) {
    deleteScheduleItemAccount(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of schedule item accounts """
        schedule_item_account = f.ScheduleItemAccountFactory.create()

        query = self.schedule_item_accounts_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_account.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemAccounts']['edges'][0]['node']['account']['id'],
          to_global_id('AccountNode', schedule_item_account.account.pk)
        )
        self.assertEqual(data['scheduleItemAccounts']['edges'][0]['node']['role'], schedule_item_account.role)
        self.assertEqual(
          data['scheduleItemAccounts']['edges'][0]['node']['account2']['id'],
          to_global_id('AccountNode', schedule_item_account.account_2.pk)
        )
        self.assertEqual(data['scheduleItemAccounts']['edges'][0]['node']['role2'], schedule_item_account.role_2)
        self.assertEqual(data['scheduleItemAccounts']['edges'][0]['node']['dateStart'], str(schedule_item_account.date_start))
        self.assertEqual(data['scheduleItemAccounts']['edges'][0]['node']['dateEnd'], schedule_item_account.date_end)


    def test_query_permission_denied(self):
        """ Query list of schedule item accounts """
        schedule_item_account = f.ScheduleItemAccountFactory.create()

        query = self.schedule_item_accounts_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_account.schedule_item.pk)
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permission_granted(self):
        """ Query list of schedule item accounts """
        schedule_item_account = f.ScheduleItemAccountFactory.create()

        query = self.schedule_item_accounts_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_account.schedule_item.pk)
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        # View account
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemAccounts']['edges'][0]['node']['account']['id'],
          to_global_id('AccountNode', schedule_item_account.account.pk)
        )


    def test_query_anon_user(self):
        """ Query list of schedule item accounts """
        schedule_item_account = f.ScheduleItemAccountFactory.create()

        query = self.schedule_item_accounts_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_account.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query list of schedule item account """
        schedule_item_account = f.ScheduleItemAccountFactory.create()
        query = self.schedule_item_account_query

        variables = {
          "id": to_global_id('ScheduleItemAccountNode', schedule_item_account.id),
        }
       
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemAccount']['account']['id'],
          to_global_id('AccountNode', schedule_item_account.account.pk)
        )
        self.assertEqual(data['scheduleItemAccount']['role'], schedule_item_account.role)
        self.assertEqual(
          data['scheduleItemAccount']['account2']['id'],
          to_global_id('AccountNode', schedule_item_account.account_2.pk)
        )
        self.assertEqual(data['scheduleItemAccount']['role2'], schedule_item_account.role_2)
        self.assertEqual(data['scheduleItemAccount']['dateStart'], str(schedule_item_account.date_start))
        self.assertEqual(data['scheduleItemAccount']['dateEnd'], schedule_item_account.date_end)


    def test_query_one_anon_user(self):
        """ Query list of schedule item account """
        schedule_item_account = f.ScheduleItemAccountFactory.create()
        query = self.schedule_item_account_query

        variables = {
          "id": to_global_id('ScheduleItemAccountNode', schedule_item_account.id),
        }
       
        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        schedule_item_account = f.ScheduleItemAccountFactory.create()
        query = self.schedule_item_account_query

        variables = {
          "id": to_global_id('ScheduleItemAccountNode', schedule_item_account.id),
        }
       
        # Now query single schedule item account and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        # Permission view account
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        user.save()
        
        schedule_item_account = f.ScheduleItemAccountFactory.create()
        query = self.schedule_item_account_query

        variables = {
          "id": to_global_id('ScheduleItemAccountNode', schedule_item_account.id),
        }

        # Now query single schedule item account and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
          data['scheduleItemAccount']['account']['id'],
          to_global_id('AccountNode', schedule_item_account.account.pk)
        )


    def test_create_schedule_item_account(self):
        """ Create schedule item account """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        account = f.InstructorFactory.create()
        account2 = f.Instructor2Factory.create()

        query = self.schedule_item_account_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('scheduleItemNode', schedule_class.pk)
        variables['input']['account'] = to_global_id('AccountNode', account.pk)
        variables['input']['account2'] = to_global_id('AccountNode', account2.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['createScheduleItemAccount']['scheduleItemAccount']['account']['id'], variables['input']['account'])
        self.assertEqual(data['createScheduleItemAccount']['scheduleItemAccount']['role'], variables['input']['role'])
        self.assertEqual(data['createScheduleItemAccount']['scheduleItemAccount']['account2']['id'], variables['input']['account2'])
        self.assertEqual(data['createScheduleItemAccount']['scheduleItemAccount']['role2'], variables['input']['role2'])
        self.assertEqual(data['createScheduleItemAccount']['scheduleItemAccount']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['createScheduleItemAccount']['scheduleItemAccount']['dateEnd'], variables['input']['dateEnd'])


    def test_create_schedule_item_account_anon_user(self):
        """ Don't allow creating schedule item account for non-logged in users """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        account = f.InstructorFactory.create()
        account2 = f.Instructor2Factory.create()

        query = self.schedule_item_account_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('scheduleItemNode', schedule_class.pk)
        variables['input']['account'] = to_global_id('AccountNode', account.pk)
        variables['input']['account2'] = to_global_id('AccountNode', account2.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_schedule_item_account_permission_granted(self):
        """ Allow creating schedule item accounts for users with permissions """
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        # Permission view account
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        user.save()

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        account = f.InstructorFactory.create()
        account2 = f.Instructor2Factory.create()

        query = self.schedule_item_account_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('scheduleItemNode', schedule_class.pk)
        variables['input']['account'] = to_global_id('AccountNode', account.pk)
        variables['input']['account2'] = to_global_id('AccountNode', account2.pk)

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['createScheduleItemAccount']['scheduleItemAccount']['account']['id'], variables['input']['account'])


    def test_create_schedule_item_account_permission_denied(self):
        """ Check create schedule item account permission denied error message """
        # Create regular user
        user = f.RegularUserFactory.create()

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        account = f.InstructorFactory.create()
        account2 = f.Instructor2Factory.create()

        query = self.schedule_item_account_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('scheduleItemNode', schedule_class.pk)
        variables['input']['account'] = to_global_id('AccountNode', account.pk)
        variables['input']['account2'] = to_global_id('AccountNode', account2.pk)

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_update_schedule_item_account(self):
        """ Update schedule item account """
        schedule_item_account = f.ScheduleItemAccountFactory.create()

        query = self.schedule_item_account_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemAccountNode', schedule_item_account.pk)
        variables['input']['account'] = to_global_id('AccountNode', schedule_item_account.account_2.pk)
        variables['input']['account2'] = to_global_id('AccountNode', schedule_item_account.account.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateScheduleItemAccount']['scheduleItemAccount']['account']['id'], variables['input']['account'])
        self.assertEqual(data['updateScheduleItemAccount']['scheduleItemAccount']['role'], variables['input']['role'])
        self.assertEqual(data['updateScheduleItemAccount']['scheduleItemAccount']['account2']['id'], variables['input']['account2'])
        self.assertEqual(data['updateScheduleItemAccount']['scheduleItemAccount']['role2'], variables['input']['role2'])
        self.assertEqual(data['updateScheduleItemAccount']['scheduleItemAccount']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['updateScheduleItemAccount']['scheduleItemAccount']['dateEnd'], variables['input']['dateEnd'])


    def test_update_schedule_item_account_anon_user(self):
        """ Don't allow updating schedule item accounts for non-logged in users """
        schedule_item_account = f.ScheduleItemAccountFactory.create()
        query = self.schedule_item_account_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemAccountNode', schedule_item_account.pk)
        variables['input']['account'] = to_global_id('AccountNode', schedule_item_account.account_2.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_schedule_item_account_permission_granted(self):
        """ Allow updating schedule item account for users with permissions """
        schedule_item_account = f.ScheduleItemAccountFactory.create()
        query = self.schedule_item_account_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemAccountNode', schedule_item_account.pk)
        variables['input']['account'] = to_global_id('AccountNode', schedule_item_account.account_2.pk)

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        # Permission view account
        permission = Permission.objects.get(codename=self.permission_view_account)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateScheduleItemAccount']['scheduleItemAccount']['role'], variables['input']['role'])


    def test_update_schedule_item_account_permission_denied(self):
        """ Check update schedule item account permission denied error message """
        schedule_item_account = f.ScheduleItemAccountFactory.create()
        query = self.schedule_item_account_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemAccountNode', schedule_item_account.pk)
        variables['input']['account'] = to_global_id('AccountNode', schedule_item_account.account_2.pk)

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


    def test_delete_schedule_item_account(self):
        """ Delete a schedule item account """
        schedule_item_account = f.ScheduleItemAccountFactory.create()
        query = self.schedule_item_account_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemAccountNode', schedule_item_account.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        
        self.assertEqual(data['deleteScheduleItemAccount']['ok'], True)

        exists = models.ScheduleItemAccount.objects.exists()
        self.assertEqual(exists, False)


    def test_delete_schedule_item_account_anon_user(self):
        """ Don't allow deleting schedule item accounts for non logged in users """
        schedule_item_account = f.ScheduleItemAccountFactory.create()
        query = self.schedule_item_account_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemAccountNode', schedule_item_account.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_delete_schedule_item_account_permission_granted(self):
        """ Allow deleting schedule item accounts for users with permissions """
        schedule_item_account = f.ScheduleItemAccountFactory.create()
        query = self.schedule_item_account_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemAccountNode', schedule_item_account.pk)

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
        self.assertEqual(data['deleteScheduleItemAccount']['ok'], True)


    def test_delete_schedule_item_account_permission_denied(self):
        """ Check delete schedule item account permission denied error message """
        schedule_item_account = f.ScheduleItemAccountFactory.create()
        query = self.schedule_item_account_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemAccountNode', schedule_item_account.pk)
        
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

