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


class GQLScheduleItemOrganizationClasspassGroup(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_scheduleitemorganizationclasspassgroup'
        self.permission_add = 'add_scheduleitemorganizationclasspassgroup'
        self.permission_change = 'change_scheduleitemorganizationclasspassgroup'
        self.permission_delete = 'delete_scheduleitemorganizationclasspassgroup'

        self.variables_update = {
            "input": {
                "shopBook": True,
                "attend": True
            }
        }


        self.schedule_item_organization_classpass_groups_query = '''
  query ScheduleItemOrganizationClasspassGroups($after: String, $before: String, $scheduleItem: ID!) {
    scheduleItemOrganizationClasspassGroups(before: $before, after: $after, scheduleItem:$scheduleItem) {
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
          organizationClasspassGroup {
            id
            name
          }
          shopBook
          attend
        }
      }
    }
  }
'''

        self.schedule_item_organization_classpass_group_update_mutation = '''
  mutation UpdateScheduleItemOrganizationClasspassGroup($input: UpdateScheduleItemOrganizationClasspassGroupInput!) {
    updateScheduleItemOrganizationClasspassGroup(input:$input) {
      scheduleItemOrganizationClasspassGroup {
        id
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
        """ Query list of schedule item organization_classpass_groups """
        schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupDenyFactory.create()

        query = self.schedule_item_organization_classpass_groups_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_organization_classpass_group.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemOrganizationClasspassGroups']['edges'][0]['node']['scheduleItem']['id'],
          to_global_id('ScheduleItemNode', schedule_item_organization_classpass_group.schedule_item.pk)
        )
        self.assertEqual(
          data['scheduleItemOrganizationClasspassGroups']['edges'][0]['node']['organizationClasspassGroup']['id'],
          to_global_id('OrganizationClasspassGroupNode', schedule_item_organization_classpass_group.organization_classpass_group.pk)
        )
        self.assertEqual(data['scheduleItemOrganizationClasspassGroups']['edges'][0]['node']['shopBook'], schedule_item_organization_classpass_group.shop_book)
        self.assertEqual(data['scheduleItemOrganizationClasspassGroups']['edges'][0]['node']['attend'], schedule_item_organization_classpass_group.attend)


    # All logged in users can query which classes can be accessed by which groups. 

    # def test_query_permission_denied(self):
    #     """ Query list of schedule item organization_classpass_groups """
    #     schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupDenyFactory.create()

    #     query = self.schedule_item_organization_classpass_groups_query
    #     variables = {
    #         'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_organization_classpass_group.schedule_item.pk)
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     errors = executed.get('errors')

    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_permission_granted(self):
    #     """ Query list of schedule item organization_classpass_groups """
    #     schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupDenyFactory.create()

    #     query = self.schedule_item_organization_classpass_groups_query
    #     variables = {
    #         'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_organization_classpass_group.schedule_item.pk)
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_scheduleitemorganizationclasspassgroup')
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')

    #     self.assertEqual(
    #       data['scheduleItemOrganizationClasspassGroups']['edges'][0]['node']['scheduleItem']['id'],
    #       to_global_id('ScheduleItemNode', schedule_item_organization_classpass_group.schedule_item.pk)
    #     )


    def test_query_anon_user(self):
        """ Query list of schedule item organization_classpass_groups """
        schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupDenyFactory.create()

        query = self.schedule_item_organization_classpass_groups_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_organization_classpass_group.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_schedule_item_organization_classpass_group(self):
        """ Update schedule item organization_classpass_group """
        schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupDenyFactory.create()

        query = self.schedule_item_organization_classpass_group_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemOrganizationClasspassGroupNode', schedule_item_organization_classpass_group.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateScheduleItemOrganizationClasspassGroup']['scheduleItemOrganizationClasspassGroup']['id'], variables['input']['id'])
        self.assertEqual(data['updateScheduleItemOrganizationClasspassGroup']['scheduleItemOrganizationClasspassGroup']['shopBook'], variables['input']['shopBook'])
        self.assertEqual(data['updateScheduleItemOrganizationClasspassGroup']['scheduleItemOrganizationClasspassGroup']['attend'], variables['input']['attend'])


    def test_update_schedule_item_organization_classpass_group_anon_user(self):
        """ Don't allow updating schedule item organization_classpass_groups for non-logged in users """
        schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupDenyFactory.create()
        query = self.schedule_item_organization_classpass_group_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemOrganizationClasspassGroupNode', schedule_item_organization_classpass_group.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_schedule_item_organization_classpass_group_permission_granted(self):
        """ Allow updating schedule item organization_classpass_group for users with permissions """
        schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupDenyFactory.create()
        query = self.schedule_item_organization_classpass_group_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemOrganizationClasspassGroupNode', schedule_item_organization_classpass_group.pk)

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

        self.assertEqual(data['updateScheduleItemOrganizationClasspassGroup']['scheduleItemOrganizationClasspassGroup']['shopBook'], variables['input']['shopBook'])


    def test_update_schedule_item_organization_classpass_group_permission_denied(self):
        """ Check update schedule item organization_classpass_group permission denied error message """
        schedule_item_organization_classpass_group = f.ScheduleItemOrganizationClasspassGroupDenyFactory.create()
        query = self.schedule_item_organization_classpass_group_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemOrganizationClasspassGroupNode', schedule_item_organization_classpass_group.pk)

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


