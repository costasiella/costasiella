# from graphql.error.located_error import GraphQLLocatedError
import datetime

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


class GQLAccountSubscriptionPause(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    fixtures = ['system_setting.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountsubscriptionpause'
        self.permission_add = 'add_accountsubscriptionpause'
        self.permission_change = 'change_accountsubscriptionpause'
        self.permission_delete = 'delete_accountsubscriptionpause'

        self.variables_create = {
            "input": {
                "dateStart": "2019-01-01",
                "dateEnd": "2019-01-31",
                "description": "Test description"
            }
        }

        self.variables_update = {
            "input": {
                "dateStart": "2019-01-01",
                "dateEnd": "2019-01-31",
                "description": "Test description"
            }
        }

        self.subscription_pauses_query = '''
    query AccountSubscriptionPauses($before: String, $after: String, $accountSubscription: ID!) {
      accountSubscriptionPauses(first: 20, before: $before, after: $after, accountSubscription: $accountSubscription) {
        pageInfo {
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
        }
        edges {
          node {
            id
            accountSubscription {
              id
            }
            dateStart
            dateEnd
            description
            createdAt
          }
        } 
      }
    }
'''

        self.subscription_pause_query = '''
    query AccountSubscriptionPause($id: ID!) {
      accountSubscriptionPause(id:$id) {
        id
        accountSubscription {
          id
        }
        dateStart
        dateEnd
        description
      }
    }
'''

        self.subscription_pause_create_mutation = ''' 
  mutation CreateAccountSubscriptionPause($input:CreateAccountSubscriptionPauseInput!) {
    createAccountSubscriptionPause(input: $input) {
      accountSubscriptionPause {
        id
        accountSubscription {
          id
        }
        dateStart
        dateEnd
        description
      }
    }
  }
'''

        self.subscription_pause_update_mutation = '''
  mutation UpdateAccountSubscriptionPause($input:UpdateAccountSubscriptionPauseInput!) {
    updateAccountSubscriptionPause(input: $input) {
      accountSubscriptionPause {
        id
        accountSubscription {
          id
        }
        dateStart
        dateEnd
        description
      }
    }
  }
'''

        self.subscription_pause_delete_mutation = '''
  mutation DeleteAccountSubscriptionPause($input: DeleteAccountSubscriptionPauseInput!) {
    deleteAccountSubscriptionPause(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of account subscriptions """
        query = self.subscription_pauses_query
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode', subscription_pause.account_subscription.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionPauses']['edges'][0]['node']['accountSubscription']['id'],
            to_global_id("AccountSubscriptionNode", subscription_pause.account_subscription.id)
        )
        self.assertEqual(data['accountSubscriptionPauses']['edges'][0]['node']['dateStart'],
                         subscription_pause.date_start)
        self.assertEqual(data['accountSubscriptionPauses']['edges'][0]['node']['dateEnd'],
                         subscription_pause.date_end)
        self.assertEqual(data['accountSubscriptionPauses']['edges'][0]['node']['description'],
                         subscription_pause.description)

    def test_query_permission_denied(self):
        """ Query list of account subscriptions - check permission denied """
        query = self.subscription_pauses_query
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode', subscription_pause.account_subscription.id)
        }

        # Create regular user
        user_id = subscription_pause.account_subscription.account.id
        user = get_user_model().objects.get(pk=user_id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of account subscriptions with view permission """
        query = self.subscription_pauses_query
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode', subscription_pause.account_subscription.id)
        }

        # Create regular user
        user_id = subscription_pause.account_subscription.account.id
        user = get_user_model().objects.get(pk=user_id)
        permission = Permission.objects.get(codename='view_accountsubscriptionpause')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all subscription pause mutations
        self.assertEqual(
            data['accountSubscriptionPauses']['edges'][0]['node']['accountSubscription']['id'],
            to_global_id("AccountSubscriptionNode", subscription_pause.account_subscription.id)
        )

    def test_query_anon_user(self):
        """ Query list of account subscriptions - anon user """
        query = self.subscription_pauses_query
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        variables = {
            'accountSubscription': to_global_id('AccountSubscriptionNode', subscription_pause.account_subscription.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account subscription pause as admin """
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        variables = {
            "id": to_global_id("AccountSubscriptionPauseNode", subscription_pause.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_pause_query,
                                                 self.admin_user,
                                                 variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionPause']['id'],
            to_global_id('AccountSubscriptionPauseNode', subscription_pause.id)
        )
        self.assertEqual(data['accountSubscriptionPause']['dateStart'],
                         subscription_pause.date_start)
        self.assertEqual(data['accountSubscriptionPause']['dateEnd'],
                         subscription_pause.date_end)
        self.assertEqual(data['accountSubscriptionPause']['description'],
                         subscription_pause.description)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account subscription """
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        variables = {
            "id": to_global_id("AccountSubscriptionPauseNode", subscription_pause.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_pause_query,
                                                 self.anon_user,
                                                 variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        user = subscription_pause.account_subscription.account
        variables = {
            "id": to_global_id("AccountSubscriptionPauseNode", subscription_pause.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_pause_query,
                                                 user,
                                                 variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        user = subscription_pause.account_subscription.account
        permission = Permission.objects.get(codename='view_accountsubscriptionpause')
        user.user_permissions.add(permission)
        user.save()

        variables = {
            "id": to_global_id("AccountSubscriptionPauseNode", subscription_pause.id),
        }

        # Now query single subscription and check
        executed = execute_test_client_api_query(self.subscription_pause_query,
                                                 user,
                                                 variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountSubscriptionPause']['id'],
            to_global_id('AccountSubscriptionPauseNode', subscription_pause.id)
        )

    def test_create_subscription_pause(self):
        """ Create an account subscription pause """
        query = self.subscription_pause_create_mutation

        account_subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', account_subscription.id
        )

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountSubscriptionPause']['accountSubscriptionPause']['accountSubscription']['id'],
            variables['input']['accountSubscription']
        )
        self.assertEqual(
            data['createAccountSubscriptionPause']['accountSubscriptionPause']['dateStart'],
            variables['input']['dateStart']
        )
        self.assertEqual(
            data['createAccountSubscriptionPause']['accountSubscriptionPause']['dateEnd'],
            variables['input']['dateEnd']
        )
        self.assertEqual(
            data['createAccountSubscriptionPause']['accountSubscriptionPause']['description'],
            variables['input']['description']
        )

    def test_create_subscription_pause_booked_classes_in_pause_cancelled(self):
        """ Create an account subscription pause and check if classed booked within pause are cancelled """
        query = self.subscription_pause_create_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceSubscriptionFactory.create()
        account_subscription = schedule_item_attendance.account_subscription
        account_subscription_credit = f.AccountSubscriptionCreditFactory.create(
            account_subscription=account_subscription
        )
        account_subscription_credit.schedule_item_attendance = schedule_item_attendance
        account_subscription_credit.save()

        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', account_subscription.id
        )
        variables['input']['dateStart'] = str(schedule_item_attendance.date)
        variables['input']['dateEnd'] = str(schedule_item_attendance.date + datetime.timedelta(days=7))

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountSubscriptionPause']['accountSubscriptionPause']['accountSubscription']['id'],
            variables['input']['accountSubscription']
        )

        refetched_schedule_item_attendance = models.ScheduleItemAttendance.objects.get(id=schedule_item_attendance.id)
        self.assertEqual(refetched_schedule_item_attendance.booking_status, 'CANCELLED')

    def test_create_subscription_pause_booked_classes_credit_returned(self):
        """ Create an account subscription pause and check if credits for classed booked within pause are returned """
        query = self.subscription_pause_create_mutation

        schedule_item_attendance = f.ScheduleItemAttendanceSubscriptionFactory.create()
        account_subscription = schedule_item_attendance.account_subscription
        account_subscription_credit = f.AccountSubscriptionCreditFactory.create(
            account_subscription=account_subscription
        )
        account_subscription_credit.schedule_item_attendance = schedule_item_attendance
        account_subscription_credit.save()

        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', account_subscription.id
        )
        variables['input']['dateStart'] = str(schedule_item_attendance.date)
        variables['input']['dateEnd'] = str(schedule_item_attendance.date + datetime.timedelta(days=7))

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountSubscriptionPause']['accountSubscriptionPause']['accountSubscription']['id'],
            variables['input']['accountSubscription']
        )

        refetched_credit = models.AccountSubscriptionCredit.objects.get(id=account_subscription_credit.id)
        self.assertEqual(refetched_credit.schedule_item_attendance, None)


    def test_create_subscription_pause_raises_exception_when_min_duration_not_reached(self):
        """
        Exception when pause is too short
        :return:
        """
        query = self.subscription_pause_create_mutation

        account_subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', account_subscription.id
        )

        system_setting = models.SystemSetting.objects.get(setting="workflow_subscription_pauses_min_duration_in_days")
        system_setting.value = "100"
        system_setting.save()

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], "A pause should be at least 100 day(s)")

    def test_create_subscription_pause_raises_exception_when_over_max_pauses(self):
        """
        Exception when pause is too short
        :return:
        """
        query = self.subscription_pause_create_mutation

        account_subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', account_subscription.id
        )

        system_setting = models.SystemSetting.objects.get(setting="workflow_subscription_pauses_max_pauses_in_year")
        system_setting.value = "0"
        system_setting.save()

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], "Maximum number of pauses reached for year 2019")

    def test_create_subscription_anon_user(self):
        """ Don't allow creating account subscription pause for non-logged in users """
        query = self.subscription_pause_create_mutation

        account_subscription = f.AccountSubscriptionFactory.create()
        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', account_subscription.id
        )

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_subscription_pause_permission_granted(self):
        """ Allow creating subscription pauses for users with permissions """
        query = self.subscription_pause_create_mutation

        account_subscription = f.AccountSubscriptionFactory.create()
        account = account_subscription.account
        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', account_subscription.id
        )

        # Create regular user
        user = account
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
            data['createAccountSubscriptionPause']['accountSubscriptionPause']['accountSubscription']['id'],
            variables['input']['accountSubscription']
        )

    def test_create_subscription_pause_permission_denied(self):
        """ Check create subscription permission denied error message """
        query = self.subscription_pause_create_mutation

        account_subscription = f.AccountSubscriptionFactory.create()
        account = account_subscription.account
        variables = self.variables_create
        variables['input']['accountSubscription'] = to_global_id(
            'AccountSubscriptionNode', account_subscription.id
        )

        executed = execute_test_client_api_query(
            query,
            account,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_subscription_pause(self):
        """ Update a subscription pause """
        query = self.subscription_pause_update_mutation
        subscription_pause = f.AccountSubscriptionPauseFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionPauseNode', subscription_pause.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['updateAccountSubscriptionPause']['accountSubscriptionPause']['accountSubscription']['id'],
            to_global_id('AccountSubscriptionNode', subscription_pause.account_subscription.id)
        )
        self.assertEqual(
            data['updateAccountSubscriptionPause']['accountSubscriptionPause']['dateStart'],
            variables['input']['dateStart']
        )
        self.assertEqual(
            data['updateAccountSubscriptionPause']['accountSubscriptionPause']['dateEnd'],
            variables['input']['dateEnd']
        )
        self.assertEqual(
            data['updateAccountSubscriptionPause']['accountSubscriptionPause']['description'],
            variables['input']['description']
        )

    def test_update_subscription_pause_anon_user(self):
        """ Don't allow updating subscription pauses for non-logged in users """
        query = self.subscription_pause_update_mutation
        subscription_pause = f.AccountSubscriptionPauseFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionPauseNode', subscription_pause.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_subscription_pause_permission_granted(self):
        """ Allow updating subscriptions for users with permissions """
        query = self.subscription_pause_update_mutation
        subscription_pause = f.AccountSubscriptionPauseFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionPauseNode', subscription_pause.id)

        user = subscription_pause.account_subscription.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
          data['updateAccountSubscriptionPause']['accountSubscriptionPause']['accountSubscription']['id'],
          to_global_id('AccountSubscriptionNode', subscription_pause.account_subscription.id)
        )

    def test_update_subscription_pause_permission_denied(self):
        """ Check update subscription permission denied error message """
        query = self.subscription_pause_update_mutation
        subscription_pause = f.AccountSubscriptionPauseFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountSubscriptionPauseNode', subscription_pause.id)

        user = subscription_pause.account_subscription.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_subscription_pause(self):
        """ Delete an account subscription pause"""
        query = self.subscription_pause_delete_mutation
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionPauseNode', subscription_pause.id)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        # print(data)
        self.assertEqual(data['deleteAccountSubscriptionPause']['ok'], True)

    def test_delete_subscription_pause_anon_user(self):
        """ Delete subscription pause denied for anon user """
        query = self.subscription_pause_delete_mutation
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionPauseNode', subscription_pause.id)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_subscription_pause_permission_granted(self):
        """ Allow deleting subscription pauses for users with permissions """
        query = self.subscription_pause_delete_mutation
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionPauseNode', subscription_pause.id)

        # Give permissions
        user = subscription_pause.account_subscription.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountSubscriptionPause']['ok'], True)

    def test_delete_subscription_pause_permission_denied(self):
        """ Check delete subscription pause permission denied error message """
        query = self.subscription_pause_delete_mutation
        subscription_pause = f.AccountSubscriptionPauseFactory.create()
        variables = {"input": {}}
        variables['input']['id'] = to_global_id('AccountSubscriptionPauseNode', subscription_pause.id)

        user = subscription_pause.account_subscription.account

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
