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


class GQLScheduleItemPrice(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleitemprice'
        self.permission_add = 'add_scheduleitemprice'
        self.permission_change = 'change_scheduleitemprice'
        self.permission_delete = 'delete_scheduleitemprice'

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

        self.schedule_item_prices_query = '''
  query ScheduleItemPrices($after: String, $before: String, $scheduleItem: ID!) {
    scheduleItemPrices(first: 15, before: $before, after: $after, scheduleItem: $scheduleItem) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationClasspassDropin {
            id
            name
          }
          organizationClasspassTrial {
            id
            name
          }
          dateStart
          dateEnd       
        }
      }
    }
  }
'''

        self.schedule_item_price_query = '''
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

        self.schedule_item_price_create_mutation = ''' 
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

        self.schedule_item_price_update_mutation = '''
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

        self.schedule_item_price_delete_mutation = '''
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
        """ Query list of schedule item prices """
        schedule_item_price = f.ScheduleItemTeacherFactory.create()

        query = self.schedule_item_prices_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_price.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemTeachers']['edges'][0]['node']['account']['id'],
          to_global_id('AccountNode', schedule_item_price.account.pk)
        )
        self.assertEqual(data['scheduleItemTeachers']['edges'][0]['node']['role'], schedule_item_price.role)
        self.assertEqual(
          data['scheduleItemTeachers']['edges'][0]['node']['account2']['id'],
          to_global_id('AccountNode', schedule_item_price.account_2.pk)
        )
        self.assertEqual(data['scheduleItemTeachers']['edges'][0]['node']['role2'], schedule_item_price.role_2)
        self.assertEqual(data['scheduleItemTeachers']['edges'][0]['node']['dateStart'], str(schedule_item_price.date_start))
        self.assertEqual(data['scheduleItemTeachers']['edges'][0]['node']['dateEnd'], schedule_item_price.date_end)


    # def test_query_permision_denied(self):
    #     """ Query list of schedule item prices """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()

    #     query = self.schedule_item_prices_query
    #     variables = {
    #         'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_price.schedule_item.pk)
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     errors = executed.get('errors')

    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_permision_granted(self):
    #     """ Query list of schedule item prices """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()

    #     query = self.schedule_item_prices_query
    #     variables = {
    #         'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_price.schedule_item.pk)
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_scheduleitemprice')
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')

    #     self.assertEqual(
    #       data['scheduleItemTeachers']['edges'][0]['node']['account']['id'],
    #       to_global_id('AccountNode', schedule_item_price.account.pk)
    #     )


    # def test_query_anon_user(self):
    #     """ Query list of schedule item prices """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()

    #     query = self.schedule_item_prices_query
    #     variables = {
    #         'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_price.schedule_item.pk)
    #     }

    #     executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one(self):
    #     """ Query list of schedule item price """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()
    #     query = self.schedule_item_price_query

    #     variables = {
    #       "id": to_global_id('ScheduleItemTeacherNode', schedule_item_price.id),
    #     }
       
    #     executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
    #     data = executed.get('data')

    #     self.assertEqual(
    #       data['scheduleItemTeacher']['account']['id'],
    #       to_global_id('AccountNode', schedule_item_price.account.pk)
    #     )
    #     self.assertEqual(data['scheduleItemTeacher']['role'], schedule_item_price.role)
    #     self.assertEqual(
    #       data['scheduleItemTeacher']['account2']['id'],
    #       to_global_id('AccountNode', schedule_item_price.account_2.pk)
    #     )
    #     self.assertEqual(data['scheduleItemTeacher']['role2'], schedule_item_price.role_2)
    #     self.assertEqual(data['scheduleItemTeacher']['dateStart'], str(schedule_item_price.date_start))
    #     self.assertEqual(data['scheduleItemTeacher']['dateEnd'], schedule_item_price.date_end)


    # def test_query_one_anon_user(self):
    #     """ Query list of schedule item price """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()
    #     query = self.schedule_item_price_query

    #     variables = {
    #       "id": to_global_id('ScheduleItemTeacherNode', schedule_item_price.id),
    #     }
       
    #     executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()
    #     query = self.schedule_item_price_query

    #     variables = {
    #       "id": to_global_id('ScheduleItemTeacherNode', schedule_item_price.id),
    #     }
       
    #     # Now query single schedule item price and check
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_scheduleitemprice')
    #     user.user_permissions.add(permission)
    #     user.save()
        
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()
    #     query = self.schedule_item_price_query

    #     variables = {
    #       "id": to_global_id('ScheduleItemTeacherNode', schedule_item_price.id),
    #     }

    #     # Now query single schedule item price and check
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #       data['scheduleItemTeacher']['account']['id'],
    #       to_global_id('AccountNode', schedule_item_price.account.pk)
    #     )


    # def test_create_schedule_item_price(self):
    #     """ Create schedule item price """
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     price = f.TeacherFactory.create()
    #     price2 = f.Teacher2Factory.create()

    #     query = self.schedule_item_price_create_mutation
    #     variables = self.variables_create
    #     variables['input']['scheduleItem'] = to_global_id('scheduleItemNode', schedule_class.pk)
    #     variables['input']['account'] = to_global_id('AccountNode', price.pk)
    #     variables['input']['account2'] = to_global_id('AccountNode', price2.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )

    #     data = executed.get('data')
    #     self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['account']['id'], variables['input']['account'])
    #     self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['role'], variables['input']['role'])
    #     self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['account2']['id'], variables['input']['account2'])
    #     self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['role2'], variables['input']['role2'])
    #     self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['dateEnd'], variables['input']['dateEnd'])


    # def test_create_schedule_item_price_anon_user(self):
    #     """ Don't allow creating schedule item price for non-logged in users """
    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     price = f.TeacherFactory.create()
    #     price2 = f.Teacher2Factory.create()

    #     query = self.schedule_item_price_create_mutation
    #     variables = self.variables_create
    #     variables['input']['scheduleItem'] = to_global_id('scheduleItemNode', schedule_class.pk)
    #     variables['input']['account'] = to_global_id('AccountNode', price.pk)
    #     variables['input']['account2'] = to_global_id('AccountNode', price2.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')

    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_create_schedule_item_price_permission_granted(self):
    #     """ Allow creating schedule item prices for users with permissions """
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     price = f.TeacherFactory.create()
    #     price2 = f.Teacher2Factory.create()

    #     query = self.schedule_item_price_create_mutation
    #     variables = self.variables_create
    #     variables['input']['scheduleItem'] = to_global_id('scheduleItemNode', schedule_class.pk)
    #     variables['input']['account'] = to_global_id('AccountNode', price.pk)
    #     variables['input']['account2'] = to_global_id('AccountNode', price2.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createScheduleItemTeacher']['scheduleItemTeacher']['account']['id'], variables['input']['account'])


    # def test_create_schedule_item_price_permission_denied(self):
    #     """ Check create schedule item price permission denied error message """
    #     # Create regular user
    #     user = f.RegularUserFactory.create()

    #     schedule_class = f.SchedulePublicWeeklyClassFactory.create()
    #     price = f.TeacherFactory.create()
    #     price2 = f.Teacher2Factory.create()

    #     query = self.schedule_item_price_create_mutation
    #     variables = self.variables_create
    #     variables['input']['scheduleItem'] = to_global_id('scheduleItemNode', schedule_class.pk)
    #     variables['input']['account'] = to_global_id('AccountNode', price.pk)
    #     variables['input']['account2'] = to_global_id('AccountNode', price2.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_update_schedule_item_price(self):
    #     """ Update schedule item price """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()

    #     query = self.schedule_item_price_update_mutation
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_price.pk)
    #     variables['input']['account'] = to_global_id('AccountNode', schedule_item_price.account_2.pk)
    #     variables['input']['account2'] = to_global_id('AccountNode', schedule_item_price.account.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )

    #     data = executed.get('data')
    #     self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['account']['id'], variables['input']['account'])
    #     self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['role'], variables['input']['role'])
    #     self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['account2']['id'], variables['input']['account2'])
    #     self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['role2'], variables['input']['role2'])
    #     self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['dateEnd'], variables['input']['dateEnd'])


    # def test_update_schedule_item_price_anon_user(self):
    #     """ Don't allow updating schedule item prices for non-logged in users """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()
    #     query = self.schedule_item_price_update_mutation
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_price.pk)
    #     variables['input']['account'] = to_global_id('AccountNode', schedule_item_price.account_2.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_schedule_item_price_permission_granted(self):
    #     """ Allow updating schedule item price for users with permissions """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()
    #     query = self.schedule_item_price_update_mutation
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_price.pk)
    #     variables['input']['account'] = to_global_id('AccountNode', schedule_item_price.account_2.pk)

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
    #     self.assertEqual(data['updateScheduleItemTeacher']['scheduleItemTeacher']['role'], variables['input']['role'])


    # def test_update_schedule_item_price_permission_denied(self):
    #     """ Check update schedule item price permission denied error message """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()
    #     query = self.schedule_item_price_update_mutation
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_price.pk)
    #     variables['input']['account'] = to_global_id('AccountNode', schedule_item_price.account_2.pk)

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


    # def test_delete_schedule_item_price(self):
    #     """ Delete a schedule item price """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()
    #     query = self.schedule_item_price_delete_mutation
    #     variables = self.variables_delete
    #     variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_price.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
        
    #     self.assertEqual(data['deleteScheduleItemTeacher']['ok'], True)

    #     exists = models.ScheduleItemTeacher.objects.exists()
    #     self.assertEqual(exists, False)


    # def test_delete_schedule_item_price_anon_user(self):
    #     """ Don't allow deleting schedule item prices for non logged in users """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()
    #     query = self.schedule_item_price_delete_mutation
    #     variables = self.variables_delete
    #     variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_price.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_delete_schedule_item_price_permission_granted(self):
    #     """ Allow deleting schedule item prices for users with permissions """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()
    #     query = self.schedule_item_price_delete_mutation
    #     variables = self.variables_delete
    #     variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_price.pk)

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
    #     self.assertEqual(data['deleteScheduleItemTeacher']['ok'], True)


    # def test_delete_schedule_item_price_permission_denied(self):
    #     """ Check delete schedule item price permission denied error message """
    #     schedule_item_price = f.ScheduleItemTeacherFactory.create()
    #     query = self.schedule_item_price_delete_mutation
    #     variables = self.variables_delete
    #     variables['input']['id'] = to_global_id('ScheduleItemTeacherNode', schedule_item_price.pk)
        
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

