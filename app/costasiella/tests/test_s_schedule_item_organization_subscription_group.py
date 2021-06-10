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
  query ScheduleItemOrganizationSubscriptionGroups($after: String, $before: String, $scheduleItem: ID!) {
    scheduleItemOrganizationSubscriptionGroups(before: $before, after: $after, scheduleItem:$scheduleItem) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          scheduleItem {
            id
          }
          organizationSubscriptionGroup {
            id
            name
          }
          enroll
          shopBook
          attend
        }
      }
    }
  }
'''

        self.schedule_item_organization_subscription_group_update_mutation = '''
  mutation UpdateScheduleItemOrganizationSubscriptionGroup($input: UpdateScheduleItemOrganizationSubscriptionGroupInput!) {
    updateScheduleItemOrganizationSubscriptionGroup(input:$input) {
      scheduleItemOrganizationSubscriptionGroup {
        id
        enroll
        shopBook
        attend     
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of schedule item organization_subscription_groups """
        schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupDenyFactory.create()

        query = self.schedule_item_organization_subscription_groups_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_organization_subscription_group.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemOrganizationSubscriptionGroups']['edges'][0]['node']['scheduleItem']['id'],
          to_global_id('ScheduleItemNode', schedule_item_organization_subscription_group.schedule_item.pk)
        )
        self.assertEqual(
          data['scheduleItemOrganizationSubscriptionGroups']['edges'][0]['node']['organizationSubscriptionGroup']['id'],
          to_global_id('OrganizationSubscriptionGroupNode', schedule_item_organization_subscription_group.organization_subscription_group.pk)
        )
        self.assertEqual(data['scheduleItemOrganizationSubscriptionGroups']['edges'][0]['node']['enroll'], schedule_item_organization_subscription_group.enroll)
        self.assertEqual(data['scheduleItemOrganizationSubscriptionGroups']['edges'][0]['node']['shopBook'], schedule_item_organization_subscription_group.shop_book)
        self.assertEqual(data['scheduleItemOrganizationSubscriptionGroups']['edges'][0]['node']['attend'], schedule_item_organization_subscription_group.attend)


    # All logged in users can query which classes can be accessed by which groups. 

    # def test_query_permission_denied(self):
    #     """ Query list of schedule item organization_subscription_groups """
    #     schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupDenyFactory.create()

    #     query = self.schedule_item_organization_subscription_groups_query
    #     variables = {
    #         'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_organization_subscription_group.schedule_item.pk)
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     errors = executed.get('errors')

    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_permission_granted(self):
    #     """ Query list of schedule item organization_subscription_groups """
    #     schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupDenyFactory.create()

    #     query = self.schedule_item_organization_subscription_groups_query
    #     variables = {
    #         'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_organization_subscription_group.schedule_item.pk)
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_scheduleitemorganizationsubscriptiongroup')
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')

    #     self.assertEqual(
    #       data['scheduleItemOrganizationSubscriptionGroups']['edges'][0]['node']['scheduleItem']['id'],
    #       to_global_id('ScheduleItemNode', schedule_item_organization_subscription_group.schedule_item.pk)
    #     )


    def test_query_anon_user(self):
        """ Query list of schedule item organization_subscription_groups """
        schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupDenyFactory.create()

        query = self.schedule_item_organization_subscription_groups_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_organization_subscription_group.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_schedule_item_organization_subscription_group(self):
        """ Update schedule item organization_subscription_group """
        schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupDenyFactory.create()

        query = self.schedule_item_organization_subscription_group_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemOrganizationSubscriptionGroupNode', schedule_item_organization_subscription_group.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateScheduleItemOrganizationSubscriptionGroup']['scheduleItemOrganizationSubscriptionGroup']['id'], variables['input']['id'])
        self.assertEqual(data['updateScheduleItemOrganizationSubscriptionGroup']['scheduleItemOrganizationSubscriptionGroup']['enroll'], variables['input']['enroll'])
        self.assertEqual(data['updateScheduleItemOrganizationSubscriptionGroup']['scheduleItemOrganizationSubscriptionGroup']['shopBook'], variables['input']['shopBook'])
        self.assertEqual(data['updateScheduleItemOrganizationSubscriptionGroup']['scheduleItemOrganizationSubscriptionGroup']['attend'], variables['input']['attend'])


    def test_update_schedule_item_organization_subscription_group_anon_user(self):
        """ Don't allow updating schedule item organization_subscription_groups for non-logged in users """
        schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupDenyFactory.create()
        query = self.schedule_item_organization_subscription_group_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemOrganizationSubscriptionGroupNode', schedule_item_organization_subscription_group.pk)

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
        schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupDenyFactory.create()
        query = self.schedule_item_organization_subscription_group_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemOrganizationSubscriptionGroupNode', schedule_item_organization_subscription_group.pk)

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

        self.assertEqual(data['updateScheduleItemOrganizationSubscriptionGroup']['scheduleItemOrganizationSubscriptionGroup']['enroll'], variables['input']['enroll'])


    def test_update_schedule_item_organization_subscription_group_permission_denied(self):
        """ Check update schedule item organization_subscription_group permission denied error message """
        schedule_item_organization_subscription_group = f.ScheduleItemOrganizationSubscriptionGroupDenyFactory.create()
        query = self.schedule_item_organization_subscription_group_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemOrganizationSubscriptionGroupNode', schedule_item_organization_subscription_group.pk)

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


