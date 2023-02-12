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


class GQLScheduleItemEnrollment(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['app_settings.json', 'organization.json', 'system_mail_template.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleitemenrollment'
        self.permission_add = 'add_scheduleitemenrollment'
        self.permission_change = 'change_scheduleitemenrollment'
        self.permission_delete = 'delete_scheduleitemenrollment'

        self.schedule_item_enrollment = f.ScheduleItemEnrollmentFactory.create()
        self.user = self.schedule_item_enrollment.account_subscription.account

        self.variables_create = {
            "input": {
                "dateStart": '2019-01-01',
                "dateEnd": '2019-12-31',
            }
        }

        self.variables_update = {
            "input": {
                "dateStart": '2019-01-01',
                "dateEnd": '2019-12-31',
            }
        }

        self.variables_delete = {
            "input": {}
        }

        self.schedule_item_enrollments_query = '''
  query ScheduleItemEnrollments($after: String, $before: String, $scheduleItem: ID!) {
    scheduleItemEnrollments(first: 15, before: $before, after: $after, scheduleItem: $scheduleItem) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id 
          dateStart
          dateEnd
          accountSubscription {
            id           
          }
          scheduleItem {
            id
          }
        }
      }
    }
  }
'''

        self.schedule_item_enrollment_query = '''
  query ScheduleItemEnrollment($id: ID!) {
    scheduleItemEnrollment(id: $id) {
      id
      dateStart
      dateEnd
      scheduleItem {
        id
      }
      accountSubscription {
        id
      }   
    }
  }
'''

        self.schedule_item_enrollment_create_mutation = '''
  mutation CreateScheduleItemEnrollment($input: CreateScheduleItemEnrollmentInput!) {
    createScheduleItemEnrollment(input:$input) {
      scheduleItemEnrollment {
        id
        dateStart
        dateEnd
        scheduleItem {
          id
        }
        accountSubscription {
          id
        }
      }
    }
  }
'''

        self.schedule_item_enrollment_update_mutation = '''
  mutation UpdateScheduleItemEnrollment($input: UpdateScheduleItemEnrollmentInput!) {
    updateScheduleItemEnrollment(input:$input) {
      scheduleItemEnrollment {
        id
        dateStart
        dateEnd
        scheduleItem {
          id
        }
        accountSubscription {
          id
        }
      }
    }
  }
'''

        self.schedule_item_enrollment_delete_mutation = '''
  mutation DeleteScheduleItemEnrollment($input: DeleteScheduleItemEnrollmentInput!) {
    deleteScheduleItemEnrollment(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of schedule item enrollments """
        query = self.schedule_item_enrollments_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item_enrollment.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemEnrollments']['edges'][0]['node']['scheduleItem']['id'],
          to_global_id('ScheduleItemNode', self.schedule_item_enrollment.schedule_item.pk)
        )
        self.assertEqual(
          data['scheduleItemEnrollments']['edges'][0]['node']['accountSubscription']['id'],
          to_global_id('AccountSubscriptionNode', self.schedule_item_enrollment.account_subscription.id)
        )
        self.assertEqual(data['scheduleItemEnrollments']['edges'][0]['node']['dateStart'],
                         str(self.schedule_item_enrollment.date_start))
        self.assertEqual(data['scheduleItemEnrollments']['edges'][0]['node']['dateEnd'],
                         str(self.schedule_item_enrollment.date_end))


    def test_query_permission_denied(self):
        """ Query list of schedule item enrollments - permission denied """
        query = self.schedule_item_enrollments_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item_enrollment.schedule_item.pk)
        }

        # Create regular user
        user = self.user
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permission_granted(self):
        """ Query list of schedule item enrollments """
        query = self.schedule_item_enrollments_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item_enrollment.schedule_item.pk)
        }

        # Create regular user
        user = self.user
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemEnrollments']['edges'][0]['node']['scheduleItem']['id'],
          to_global_id('ScheduleItemNode', self.schedule_item_enrollment.schedule_item.pk)
        )

    def test_query_anon_user(self):
        """ Query list of schedule item enrollments - as anon user """

        query = self.schedule_item_enrollments_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', self.schedule_item_enrollment.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query a schedule item enrollment """
        query = self.schedule_item_enrollment_query

        variables = {
          "id": to_global_id('ScheduleItemEnrollmentNode', self.schedule_item_enrollment.id),
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemEnrollment']['scheduleItem']['id'],
          to_global_id('ScheduleItemNode', self.schedule_item_enrollment.schedule_item.pk)
        )
        self.assertEqual(
          data['scheduleItemEnrollment']['accountSubscription']['id'],
          to_global_id('AccountSubscriptionNode', self.schedule_item_enrollment.account_subscription.id)
        )
        self.assertEqual(data['scheduleItemEnrollment']['dateStart'], str(self.schedule_item_enrollment.date_start))
        self.assertEqual(data['scheduleItemEnrollment']['dateEnd'], str(self.schedule_item_enrollment.date_end))


    def test_query_one_anon_user(self):
        """ Query schedule item enrollment """
        query = self.schedule_item_enrollment_query

        variables = {
          "id": to_global_id('ScheduleItemEnrollmentNode', self.schedule_item_enrollment.id),
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        query = self.schedule_item_enrollment_query

        variables = {
          "id": to_global_id('ScheduleItemEnrollmentNode', self.schedule_item_enrollment.id),
        }

        # Now query single schedule item enrollment and check
        executed = execute_test_client_api_query(query, self.user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        permission = Permission.objects.get(codename=self.permission_view)
        self.user.user_permissions.add(permission)
        self.user.save()

        query = self.schedule_item_enrollment_query

        variables = {
          "id": to_global_id('ScheduleItemEnrollmentNode', self.schedule_item_enrollment.id),
        }

        # Now query single schedule item enrollment and check
        executed = execute_test_client_api_query(query, self.user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
          data['scheduleItemEnrollment']['scheduleItem']['id'],
          to_global_id('ScheduleItemNode', self.schedule_item_enrollment.schedule_item.pk)
        )


    def test_create_schedule_item_enrollment(self):
        """ Create schedule item enrollment """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        account_subscription = self.schedule_item_enrollment.account_subscription

        query = self.schedule_item_enrollment_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_class.pk)
        variables['input']['accountSubscription'] = to_global_id('AccountSubscriptionNode', account_subscription.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['createScheduleItemEnrollment']['scheduleItemEnrollment']['scheduleItem']['id'],
                         variables['input']['scheduleItem'])
        self.assertEqual(data['createScheduleItemEnrollment']['scheduleItemEnrollment']['accountSubscription']['id'],
                         variables['input']['accountSubscription'])
        self.assertEqual(data['createScheduleItemEnrollment']['scheduleItemEnrollment']['dateStart'],
                         variables['input']['dateStart'])
        self.assertEqual(data['createScheduleItemEnrollment']['scheduleItemEnrollment']['dateEnd'],
                         variables['input']['dateEnd'])


    def test_create_schedule_item_enrollment_anon_user(self):
        """ Don't allow creating schedule item enrollment for non-logged in users """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        account_subscription = self.schedule_item_enrollment.account_subscription

        query = self.schedule_item_enrollment_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_class.pk)
        variables['input']['accountSubscription'] = to_global_id('AccountSubscriptionNode', account_subscription.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_schedule_item_enrollment_permission_granted(self):
        """ Allow creating schedule item enrollments for users with permissions """
        # Create regular user
        user = self.user
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        account_subscription = self.schedule_item_enrollment.account_subscription

        query = self.schedule_item_enrollment_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_class.pk)
        variables['input']['accountSubscription'] = to_global_id('AccountSubscriptionNode', account_subscription.pk)

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createScheduleItemEnrollment']['scheduleItemEnrollment']['scheduleItem']['id'],
                         variables['input']['scheduleItem'])


    def test_create_schedule_item_enrollment_permission_denied(self):
        """ Check create schedule item enrollment permission denied error message """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        account_subscription = self.schedule_item_enrollment.account_subscription

        query = self.schedule_item_enrollment_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_class.pk)
        variables['input']['accountSubscription'] = to_global_id('AccountSubscriptionNode', account_subscription.pk)
        executed = execute_test_client_api_query(
            query,
            self.user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_update_schedule_item_enrollment(self):
        """ Update schedule item enrollment """
        query = self.schedule_item_enrollment_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemEnrollmentNode', self.schedule_item_enrollment.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateScheduleItemEnrollment']['scheduleItemEnrollment']['dateStart'],
                         variables['input']['dateStart'])
        self.assertEqual(data['updateScheduleItemEnrollment']['scheduleItemEnrollment']['dateEnd'],
                         variables['input']['dateEnd'])


    def test_update_schedule_item_enrollment_anon_user(self):
        """ Don't allow updating schedule item enrollments for non-logged in users """
        query = self.schedule_item_enrollment_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemEnrollmentNode', self.schedule_item_enrollment.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_schedule_item_enrollment_permission_granted(self):
        """ Allow updating schedule item enrollment for users with permissions """
        query = self.schedule_item_enrollment_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemEnrollmentNode', self.schedule_item_enrollment.pk)

        # Create regular user
        user = self.user
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateScheduleItemEnrollment']['scheduleItemEnrollment']['dateEnd'],
                         variables['input']['dateEnd'])


    def test_update_schedule_item_enrollment_permission_denied(self):
        """ Check update schedule item enrollment permission denied error message """
        query = self.schedule_item_enrollment_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemEnrollmentNode', self.schedule_item_enrollment.pk)

        # Create regular user
        user = self.user

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_delete_schedule_item_enrollment(self):
        """ Delete a schedule item enrollment """
        query = self.schedule_item_enrollment_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemEnrollmentNode', self.schedule_item_enrollment.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['deleteScheduleItemEnrollment']['ok'], True)

        exists = models.ScheduleItemEnrollment.objects.exists()
        self.assertEqual(exists, False)


    def test_delete_schedule_item_enrollment_anon_user(self):
        """ Don't allow deleting schedule item enrollments for non logged in users """
        query = self.schedule_item_enrollment_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemEnrollmentNode', self.schedule_item_enrollment.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_delete_schedule_item_enrollment_permission_granted(self):
        """ Allow deleting schedule item enrollments for users with permissions """
        query = self.schedule_item_enrollment_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemEnrollmentNode', self.schedule_item_enrollment.pk)

        # Create regular user
        user = self.user
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteScheduleItemEnrollment']['ok'], True)


    def test_delete_schedule_item_enrollment_permission_denied(self):
        """ Check delete schedule item enrollment permission denied error message """
        query = self.schedule_item_enrollment_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemEnrollmentNode', self.schedule_item_enrollment.pk)

        # Create regular user
        user = self.user

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

