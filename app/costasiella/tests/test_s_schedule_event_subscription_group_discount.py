# from graphql.error.located_error import GraphQLLocatedError
import os
import shutil
import graphql
import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema

from app.settings.development import MEDIA_ROOT


class GQLScheduleEventSubscriptionGroupDiscount(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleeventsubscriptiongroupdiscount'
        self.permission_add = 'add_scheduleeventsubscriptiongroupdiscount'
        self.permission_change = 'change_scheduleeventsubscriptiongroupdiscount'
        self.permission_delete = 'delete_scheduleeventsubscriptiongroupdiscount'

        self.schedule_event_subscription_group_discount = f.ScheduleEventSubscriptionGroupDiscountFactory.create()

        self.variables_query_list = {
            "scheduleEvent": to_global_id("ScheduleEventNode",
                                          self.schedule_event_subscription_group_discount.schedule_event.id)
        }

        self.variables_query_one = {
            "id": to_global_id("ScheduleEventSubscriptionGroupDiscountNode",
                               self.schedule_event_subscription_group_discount.id)
        }

        self.variables_create = {
            "input": {
                "scheduleEvent": to_global_id("ScheduleEventNode",
                                              self.schedule_event_subscription_group_discount.schedule_event.id),
                "organizationSubscriptionGroup":
                    to_global_id("OrganizationSubscriptionGroupNode",
                                 self.schedule_event_subscription_group_discount.organization_subscription_group.id),
                "discountPercentage": "50",
            }
        }

        self.variables_update = {
            "input": {
                "id": to_global_id("ScheduleEventSubscriptionGroupDiscountNode",
                                   self.schedule_event_subscription_group_discount.id),
                "organizationSubscriptionGroup":
                    to_global_id("OrganizationSubscriptionGroupNode",
                                 self.schedule_event_subscription_group_discount.organization_subscription_group.id),
                "discountPercentage": "50",
            }
        }

        self.variables_delete = {
            "input": {
                "id": to_global_id("ScheduleEventSubscriptionGroupDiscountNode",
                                   self.schedule_event_subscription_group_discount.id),
            }
        }

        self.schedule_event_subscription_group_discounts_query = '''
  query ScheduleEventEarlybirds($before:String, $after:String, $scheduleEvent:ID!) {
    scheduleEventSubscriptionGroupDiscounts(first: 100, before:$before, after:$after, scheduleEvent:$scheduleEvent) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          scheduleEvent {
            id
          }
          organizationSubscriptionGroup {
            id
            name
          }
          discountPercentage
        }
      }
    }
  }
'''

        self.schedule_event_subscription_group_discount_query = '''
  query ScheduleEventSubscriptionGroupDiscount($id:ID!) {
    scheduleEventSubscriptionGroupDiscount(id: $id) {
      id
      discountPercentage
      scheduleEvent {
        id
      }  
      organizationSubscriptionGroup {
        id
        name
      }
    }
  }
'''

        self.schedule_event_subscription_group_discount_create_mutation = ''' 
  mutation CreateScheduleEventSubscriptionGroupDiscount($input:CreateScheduleEventSubscriptionGroupDiscountInput!) {
    createScheduleEventSubscriptionGroupDiscount(input: $input) {
      scheduleEventSubscriptionGroupDiscount {
        id
        discountPercentage
        scheduleEvent {
          id
        }
        organizationSubscriptionGroup {
          id
          name
        }
      }
    }
  }
'''

        self.schedule_event_subscription_group_discount_update_mutation = '''
  mutation UpdateScheduleEventSubscriptionGroupDiscount($input:UpdateScheduleEventSubscriptionGroupDiscountInput!) {
    updateScheduleEventSubscriptionGroupDiscount(input: $input) {
      scheduleEventSubscriptionGroupDiscount {
        id
        discountPercentage
        scheduleEvent {
          id
        }
        organizationSubscriptionGroup {
          id
          name
        }
      }  
    }
  }
'''

        self.schedule_event_subscription_group_discount_delete_mutation = '''
  mutation DeleteScheduleEventSubscriptionGroupDiscount($input: DeleteScheduleEventSubscriptionGroupDiscountInput!) {
    deleteScheduleEventSubscriptionGroupDiscount(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of schedule event subscription group discounts """
        query = self.schedule_event_subscription_group_discounts_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['scheduleEventSubscriptionGroupDiscounts']['edges'][0]['node']['id'],
            to_global_id('ScheduleEventSubscriptionGroupDiscountNode',
                         self.schedule_event_subscription_group_discount.id)
        )
        self.assertEqual(
            data['scheduleEventSubscriptionGroupDiscounts']['edges'][0]['node']['discountPercentage'],
            format(self.schedule_event_subscription_group_discount.discount_percentage, ".2f")
        )
        self.assertEqual(
            data['scheduleEventSubscriptionGroupDiscounts']['edges'][0]['node']['organizationSubscriptionGroup']['id'],
            to_global_id('OrganizationSubscriptionGroupNode',
                         self.schedule_event_subscription_group_discount.organization_subscription_group.id)
        )

    def test_query_anon_user_can_query_public_discounts(self):
        """ Query list of schedule event subscription group discounts as anon user """
        query = self.schedule_event_subscription_group_discounts_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['scheduleEventSubscriptionGroupDiscounts']['edges'][0]['node']['id'],
            to_global_id('ScheduleEventSubscriptionGroupDiscountNode',
                         self.schedule_event_subscription_group_discount.id)
        )

    def test_query_non_public_not_displayed(self):
        """ Query list of schedule event subscription group discounts - check non public """
        query = self.schedule_event_subscription_group_discounts_query
        schedule_event = self.schedule_event_subscription_group_discount.schedule_event
        schedule_event.display_public = False
        schedule_event.display_shop = False
        schedule_event.save()

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(len(data['scheduleEventSubscriptionGroupDiscounts']['edges']), 0)

    def test_query_one(self):
        """ Query one schedule event subscription group discount """
        query = self.schedule_event_subscription_group_discount_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['scheduleEventSubscriptionGroupDiscount']['id'], self.variables_query_one['id'])
        self.assertEqual(data['scheduleEventSubscriptionGroupDiscount']['discountPercentage'],
                         format(self.schedule_event_subscription_group_discount.discount_percentage, ".2f"))
        self.assertEqual(
            data['scheduleEventSubscriptionGroupDiscount']['organizationSubscriptionGroup']['id'],
            to_global_id("OrganizationSubscriptionGroupNode",
                         self.schedule_event_subscription_group_discount.organization_subscription_group.id)
        )

    def test_query_one_dont_display_non_public(self):
        """ Query one schedule event subscription group discount """
        query = self.schedule_event_subscription_group_discount_query
        schedule_event = self.schedule_event_subscription_group_discount.schedule_event
        schedule_event.display_public = False
        schedule_event.display_shop = False
        schedule_event.save()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['scheduleEventSubscriptionGroupDiscount']['id'], self.variables_query_one['id'])

    def test_query_one_dont_display_non_public_anon(self):
        """ Query one schedule event subscription group discount """
        query = self.schedule_event_subscription_group_discount_query
        schedule_event = self.schedule_event_subscription_group_discount.schedule_event
        schedule_event.display_public = False
        schedule_event.display_shop = False
        schedule_event.save()

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['scheduleEventSubscriptionGroupDiscount'], None)

    def test_query_one_display_public_anon(self):
        """ Query one schedule event subscription group discount """
        query = self.schedule_event_subscription_group_discount_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['scheduleEventSubscriptionGroupDiscount']['id'], self.variables_query_one['id'])

    def test_create_schedule_event_subscription_group_discount(self):
        """ Create schedule event subscription group discount """
        query = self.schedule_event_subscription_group_discount_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createScheduleEventSubscriptionGroupDiscount']['scheduleEventSubscriptionGroupDiscount']['scheduleEvent']['id'],
            variables['input']['scheduleEvent']
        )
        self.assertEqual(
            data['createScheduleEventSubscriptionGroupDiscount']['scheduleEventSubscriptionGroupDiscount']['organizationSubscriptionGroup']['id'],
            variables['input']['organizationSubscriptionGroup']
        )
        self.assertEqual(
            data['createScheduleEventSubscriptionGroupDiscount']['scheduleEventSubscriptionGroupDiscount']['discountPercentage'],
            variables['input']['discountPercentage']
        )

    def test_create_schedule_event_subscription_group_discount_anon_user(self):
        """ Don't allow creating schedule event for non-logged in users """
        query = self.schedule_event_subscription_group_discount_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_schedule_event_subscription_group_discount_permission_granted(self):
        """ Allow creating schedule event subscription group discount for users with permissions """
        query = self.schedule_event_subscription_group_discount_create_mutation

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
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
            data['createScheduleEventSubscriptionGroupDiscount']['scheduleEventSubscriptionGroupDiscount']['scheduleEvent']['id'],
            variables['input']['scheduleEvent']
        )

    def test_create_schedule_event_subscription_group_discount_permission_denied(self):
        """ Check create schedule event subscription group discount permission denied error message """
        query = self.schedule_event_subscription_group_discount_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_schedule_event_subscription_group_discount(self):
        """ Update schedule event subscription group discount """
        query = self.schedule_event_subscription_group_discount_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(
            data['updateScheduleEventSubscriptionGroupDiscount']['scheduleEventSubscriptionGroupDiscount']['id'],
            variables['input']['id']
        )
        self.assertEqual(
            data['updateScheduleEventSubscriptionGroupDiscount']['scheduleEventSubscriptionGroupDiscount']['organizationSubscriptionGroup']['id'],
            variables['input']['organizationSubscriptionGroup']
        )
        self.assertEqual(
            data['updateScheduleEventSubscriptionGroupDiscount']['scheduleEventSubscriptionGroupDiscount']['discountPercentage'],
            variables['input']['discountPercentage']
        )

    def test_update_schedule_event_subscription_group_discount_anon_user(self):
        """ Don't allow updating schedule event subscription group discount for non-logged in users """
        query = self.schedule_event_subscription_group_discount_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_schedule_event_subscription_group_discount_permission_granted(self):
        """ Allow updating schedule event subscription group discount for users with permissions """
        query = self.schedule_event_subscription_group_discount_update_mutation
        variables = self.variables_update

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
        self.assertEqual(
            data['updateScheduleEventSubscriptionGroupDiscount']['scheduleEventSubscriptionGroupDiscount']['id'],
            variables['input']['id']
        )

    def test_update_schedule_event_subscription_group_discount_permission_denied(self):
        """ Check update schedule event subscription group discount permission denied error message """
        query = self.schedule_event_subscription_group_discount_update_mutation
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

    def test_delete_schedule_event_subscription_group_discount(self):
        """ Delete a schedule event subscription group discount """
        query = self.schedule_event_subscription_group_discount_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['deleteScheduleEventSubscriptionGroupDiscount']['ok'], True)

    def test_delete_schedule_event_subscription_group_discount_anon_user(self):
        """ Delete a schedule event subscription group discount """
        query = self.schedule_event_subscription_group_discount_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_schedule_event_subscription_group_discount_permission_granted(self):
        """ Allow deleting schedule event subscription group discount for users with permissions """
        query = self.schedule_event_subscription_group_discount_delete_mutation
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

        self.assertEqual(data['deleteScheduleEventSubscriptionGroupDiscount']['ok'], True)

    def test_delete_schedule_event_subscription_group_discount_permission_denied(self):
        """ Check delete schedule event subscription group discount permission denied error message """
        query = self.schedule_event_subscription_group_discount_delete_mutation
        variables = self.variables_delete

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
