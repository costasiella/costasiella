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


class GQLScheduleItemteacher(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleitemteacher'
        self.permission_add = 'add_scheduleitemteacher'
        self.permission_change = 'change_scheduleitemteacher'
        self.permission_delete = 'delete_scheduleitemteacher'

        # self.organization_subscription = f.OrganizationSubscriptionFactory.create()
        # self.finance_tax_rate = f.FinanceTaxRateFactory.create()
        # self.organization_schedule_item_teacher = f.ScheduleItemTeacherFactory.create()

        # self.variables_create = {
        #     "input": {
        #         "organizationSubscription": to_global_id('OrganizationSubscriptionNode', self.organization_subscription.pk),
        #         "price": 10,
        #         "financeTaxRate": to_global_id('FinanceTaxRateNode', self.finance_tax_rate.pk),
        #         "dateStart": '2019-01-01',
        #         "dateEnd": '2019-12-31',
        #     }
        # }

        # self.variables_update = {
        #     "input": {
        #         "id": to_global_id('ScheduleItemTeacherNode', self.organization_schedule_item_teacher.pk),
        #         "price": 1466,
        #         "financeTaxRate": to_global_id('FinanceTaxRateNode', self.finance_tax_rate.pk),
        #         "dateStart": '2024-01-01',
        #         "dateEnd": '2024-12-31',
        #     }
        # }

        # self.variables_delete = {
        #     "input": {
        #         "id": to_global_id('ScheduleItemTeacherNode', self.organization_schedule_item_teacher.pk),
        #     }
        # }

        self.schedule_item_teachers_query = '''
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

        self.schedule_item_teacher_query = '''
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

        self.schedule_item_teacher_create_mutation = ''' 
  mutation CreateScheduleItemTeacher($input:CreateScheduleItemTeacherInput!) {
    createScheduleItemTeacher(input:$input) {
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
  }
'''

        self.schedule_item_teacher_update_mutation = '''
  mutation UpdateScheduleItemTeacher($input: UpdateScheduleItemTeacherInput!) {
    updateScheduleItemTeacher(input: $input) {
      organizationSubscriptionPrice {
        id
        organizationSubscription {
          id
          name
        }
        price
        financeTaxRate {
          id
          name
        }
        dateStart
        dateEnd
      }
    }
  }
'''

        self.schedule_item_teacher_delete_mutation = '''
  mutation DeleteScheduleItemTeacher($input: DeleteScheduleItemTeacherInput!) {
    deleteScheduleItemTeacher(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of schedule item teachers """
        schedule_item_teacher = f.ScheduleItemTeacherFactory.create()

        query = self.schedule_item_teachers_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_teacher.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemTeachers']['edges'][0]['node']['account']['id'],
          to_global_id('AccountNode', schedule_item_teacher.account.pk)
        )
        self.assertEqual(data['scheduleItemTeachers']['edges'][0]['node']['role'], schedule_item_teacher.role)
        self.assertEqual(
          data['scheduleItemTeachers']['edges'][0]['node']['account2']['id'],
          to_global_id('AccountNode', schedule_item_teacher.account_2.pk)
        )
        self.assertEqual(data['scheduleItemTeachers']['edges'][0]['node']['role2'], schedule_item_teacher.role_2)
        self.assertEqual(data['scheduleItemTeachers']['edges'][0]['node']['dateStart'], str(schedule_item_teacher.date_start))
        self.assertEqual(data['scheduleItemTeachers']['edges'][0]['node']['dateEnd'], schedule_item_teacher.date_end)


    def test_query_permision_denied(self):
        """ Query list of schedule item teachers """
        schedule_item_teacher = f.ScheduleItemTeacherFactory.create()

        query = self.schedule_item_teachers_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_teacher.schedule_item.pk)
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permision_granted(self):
        """ Query list of schedule item teachers """
        schedule_item_teacher = f.ScheduleItemTeacherFactory.create()

        query = self.schedule_item_teachers_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_teacher.schedule_item.pk)
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_scheduleitemteacher')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemTeachers']['edges'][0]['node']['account']['id'],
          to_global_id('AccountNode', schedule_item_teacher.account.pk)
        )


    def test_query_anon_user(self):
        """ Query list of schedule item teachers """
        schedule_item_teacher = f.ScheduleItemTeacherFactory.create()

        query = self.schedule_item_teachers_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_teacher.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query list of schedule item teacher """
        schedule_item_teacher = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_teacher_query

        variables = {
          "id": to_global_id('ScheduleItemTeacherNode', schedule_item_teacher.id),
        }
       
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemTeacher']['account']['id'],
          to_global_id('AccountNode', schedule_item_teacher.account.pk)
        )
        self.assertEqual(data['scheduleItemTeacher']['role'], schedule_item_teacher.role)
        self.assertEqual(
          data['scheduleItemTeacher']['account2']['id'],
          to_global_id('AccountNode', schedule_item_teacher.account_2.pk)
        )
        self.assertEqual(data['scheduleItemTeacher']['role2'], schedule_item_teacher.role_2)
        self.assertEqual(data['scheduleItemTeacher']['dateStart'], str(schedule_item_teacher.date_start))
        self.assertEqual(data['scheduleItemTeacher']['dateEnd'], schedule_item_teacher.date_end)


    def test_query_one_anon_user(self):
        """ Query list of schedule item teacher """
        schedule_item_teacher = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_teacher_query

        variables = {
          "id": to_global_id('ScheduleItemTeacherNode', schedule_item_teacher.id),
        }
       
        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        schedule_item_teacher = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_teacher_query

        variables = {
          "id": to_global_id('ScheduleItemTeacherNode', schedule_item_teacher.id),
        }
       
        # Now query single subscription price and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_scheduleitemteacher')
        user.user_permissions.add(permission)
        user.save()
        
        schedule_item_teacher = f.ScheduleItemTeacherFactory.create()
        query = self.schedule_item_teacher_query

        variables = {
          "id": to_global_id('ScheduleItemTeacherNode', schedule_item_teacher.id),
        }

        # Now query single subscription price and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
          data['scheduleItemTeacher']['account']['id'],
          to_global_id('AccountNode', schedule_item_teacher.account.pk)
        )


    # def test_create_schedule_item_teacher(self):
    #     """ Create a subscription price """
    #     query = self.schedule_item_teacher_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )

    #     print("################## create output###########")
    #     errors = executed.get('errors')
    #     print(errors)

    #     data = executed.get('data')
    #     print(data)
    #     self.assertEqual(
    #       data['createScheduleItemTeacher']['organizationSubscriptionPrice']['organizationSubscription']['id'], 
    #       variables['input']['organizationSubscription'])
    #     self.assertEqual(data['createScheduleItemTeacher']['organizationSubscriptionPrice']['price'], variables['input']['price'])
    #     self.assertEqual(data['createScheduleItemTeacher']['organizationSubscriptionPrice']['financeTaxRate']['id'], 
    #       variables['input']['financeTaxRate'])
    #     self.assertEqual(data['createScheduleItemTeacher']['organizationSubscriptionPrice']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['createScheduleItemTeacher']['organizationSubscriptionPrice']['dateEnd'], variables['input']['dateEnd'])


    # def test_create_schedule_item_teacher_anon_user(self):
    #     """ Don't allow creating subscription prices for non-logged in users """
    #     query = self.schedule_item_teacher_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_create_schedule_item_teacher_permission_granted(self):
    #     """ Allow creating subscription prices for users with permissions """
    #     query = self.schedule_item_teacher_create_mutation

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
    #     self.assertEqual(data['createScheduleItemTeacher']['organizationSubscriptionPrice']['price'], variables['input']['price'])


    # def test_create_schedule_item_teacher_permission_denied(self):
    #     """ Check create subscription price permission denied error message """
    #     query = self.schedule_item_teacher_create_mutation
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


    # def test_update_schedule_item_teacher(self):
    #     """ Update a subscription price """
    #     query = self.schedule_item_teacher_update_mutation
    #     variables = self.variables_update

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )

    #     data = executed.get('data')
    #     self.assertEqual(data['updateScheduleItemTeacher']['organizationSubscriptionPrice']['price'], variables['input']['price'])
    #     self.assertEqual(data['updateScheduleItemTeacher']['organizationSubscriptionPrice']['financeTaxRate']['id'], 
    #       variables['input']['financeTaxRate'])
    #     self.assertEqual(data['updateScheduleItemTeacher']['organizationSubscriptionPrice']['dateStart'], variables['input']['dateStart'])
    #     self.assertEqual(data['updateScheduleItemTeacher']['organizationSubscriptionPrice']['dateEnd'], variables['input']['dateEnd'])


    # def test_update_schedule_item_teacher_anon_user(self):
    #     """ Don't allow updating subscription prices for non-logged in users """
    #     query = self.schedule_item_teacher_update_mutation
    #     variables = self.variables_update

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_schedule_item_teacher_permission_granted(self):
    #     """ Allow updating subscription prices for users with permissions """
    #     query = self.schedule_item_teacher_update_mutation
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
    #     self.assertEqual(data['updateScheduleItemTeacher']['organizationSubscriptionPrice']['price'], variables['input']['price'])


    # def test_update_schedule_item_teacher_permission_denied(self):
    #     """ Check update subscription price permission denied error message """
    #     query = self.schedule_item_teacher_update_mutation
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


    # def test_delete_schedule_item_teacher(self):
    #     """ Delete a subscription price """
    #     query = self.schedule_item_teacher_delete_mutation
    #     variables = self.variables_delete

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
        
    #     self.assertEqual(data['deleteScheduleItemTeacher']['ok'], True)

    #     exists = models.ScheduleItemTeacher.objects.exists()
    #     self.assertEqual(exists, False)


    # def test_delete_schedule_item_teacher_anon_user(self):
    #     """ Delete a subscription pricem """
    #     query = self.schedule_item_teacher_delete_mutation
    #     variables = self.variables_delete

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_delete_schedule_item_teacher_permission_granted(self):
    #     """ Allow deleting subscription prices for users with permissions """
    #     query = self.schedule_item_teacher_delete_mutation
    #     variables = self.variables_delete

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


    # def test_delete_schedule_item_teacher_permission_denied(self):
    #     """ Check delete subscription price permission denied error message """
    #     query = self.schedule_item_teacher_delete_mutation
    #     variables = self.variables_delete
        
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

