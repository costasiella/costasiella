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
  query ScheduleItemPrice($id: ID!) {
    scheduleItemPrice(id: $id) {
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
'''

        self.schedule_item_price_create_mutation = ''' 
  mutation CreateScheduleItemPrice($input:CreateScheduleItemPriceInput!) {
    createScheduleItemPrice(input:$input) {
      scheduleItemPrice {
        id
        scheduleItem {
          id
        }
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
'''

        self.schedule_item_price_update_mutation = '''
  mutation UpdateScheduleItemPrice($input: UpdateScheduleItemPriceInput!) {
    updateScheduleItemPrice(input:$input) {
      scheduleItemPrice {
        id
        scheduleItem {
          id
        }
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
'''

        self.schedule_item_price_delete_mutation = '''
  mutation DeleteScheduleItemPrice($input: DeleteScheduleItemPriceInput!) {
    deleteScheduleItemPrice(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of schedule item prices """
        schedule_item_price = f.ScheduleItemPriceFactory.create()

        query = self.schedule_item_prices_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_price.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemPrices']['edges'][0]['node']['organizationClasspassDropin']['id'],
          to_global_id('OrganizationClasspassNode', schedule_item_price.organization_classpass_dropin.pk)
        )
        self.assertEqual(
          data['scheduleItemPrices']['edges'][0]['node']['organizationClasspassTrial']['id'],
          to_global_id('OrganizationClasspassNode', schedule_item_price.organization_classpass_trial.pk)
        )
        self.assertEqual(data['scheduleItemPrices']['edges'][0]['node']['dateStart'], str(schedule_item_price.date_start))
        self.assertEqual(data['scheduleItemPrices']['edges'][0]['node']['dateEnd'], schedule_item_price.date_end)


    def test_query_permission_denied(self):
        """ Query list of schedule item prices """
        schedule_item_price = f.ScheduleItemPriceFactory.create()

        query = self.schedule_item_prices_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_price.schedule_item.pk)
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permission_granted(self):
        """ Query list of schedule item prices """
        schedule_item_price = f.ScheduleItemPriceFactory.create()

        query = self.schedule_item_prices_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_price.schedule_item.pk)
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_scheduleitemprice')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemPrices']['edges'][0]['node']['organizationClasspassDropin']['id'],
          to_global_id('OrganizationClasspassNode', schedule_item_price.organization_classpass_dropin.pk)
        )

    def test_query_anon_user(self):
        """ Query list of schedule item prices """
        schedule_item_price = f.ScheduleItemPriceFactory.create()

        query = self.schedule_item_prices_query
        variables = {
            'scheduleItem': to_global_id('ScheduleItemNode', schedule_item_price.schedule_item.pk)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query list of schedule item price """
        schedule_item_price = f.ScheduleItemPriceFactory.create()
        query = self.schedule_item_price_query

        variables = {
          "id": to_global_id('ScheduleItemPriceNode', schedule_item_price.id),
        }
       
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
          data['scheduleItemPrice']['organizationClasspassDropin']['id'],
          to_global_id('OrganizationClasspassNode', schedule_item_price.organization_classpass_dropin.pk)
        )
        self.assertEqual(
          data['scheduleItemPrice']['organizationClasspassTrial']['id'],
          to_global_id('OrganizationClasspassNode', schedule_item_price.organization_classpass_trial.pk)
        )
        self.assertEqual(data['scheduleItemPrice']['dateStart'], str(schedule_item_price.date_start))
        self.assertEqual(data['scheduleItemPrice']['dateEnd'], schedule_item_price.date_end)


    def test_query_one_anon_user(self):
        """ Query list of schedule item price """
        schedule_item_price = f.ScheduleItemPriceFactory.create()
        query = self.schedule_item_price_query

        variables = {
          "id": to_global_id('ScheduleItemPriceNode', schedule_item_price.id),
        }
       
        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        schedule_item_price = f.ScheduleItemPriceFactory.create()
        query = self.schedule_item_price_query

        variables = {
          "id": to_global_id('ScheduleItemPriceNode', schedule_item_price.id),
        }
       
        # Now query single schedule item price and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_scheduleitemprice')
        user.user_permissions.add(permission)
        user.save()
        
        schedule_item_price = f.ScheduleItemPriceFactory.create()
        query = self.schedule_item_price_query

        variables = {
          "id": to_global_id('ScheduleItemPriceNode', schedule_item_price.id),
        }

        # Now query single schedule item price and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
          data['scheduleItemPrice']['organizationClasspassDropin']['id'],
          to_global_id('OrganizationClasspassNode', schedule_item_price.organization_classpass_dropin.pk)
        )


    def test_create_schedule_item_price(self):
        """ Create schedule item price """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        classpass_dropin = f.OrganizationClasspassFactory.create()
        classpass_trial = f.OrganizationClasspassTrialFactory.create()

        query = self.schedule_item_price_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_class.pk)
        variables['input']['organizationClasspassDropin'] = to_global_id('OrganizationClasspassNode', classpass_dropin.pk)
        variables['input']['organizationClasspassTrial'] = to_global_id('OrganizationClasspassNode', classpass_trial.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['createScheduleItemPrice']['scheduleItemPrice']['scheduleItem']['id'], variables['input']['scheduleItem'])
        self.assertEqual(data['createScheduleItemPrice']['scheduleItemPrice']['organizationClasspassDropin']['id'], 
          variables['input']['organizationClasspassDropin'])
        self.assertEqual(data['createScheduleItemPrice']['scheduleItemPrice']['organizationClasspassTrial']['id'], 
          variables['input']['organizationClasspassTrial'])
        self.assertEqual(data['createScheduleItemPrice']['scheduleItemPrice']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['createScheduleItemPrice']['scheduleItemPrice']['dateEnd'], variables['input']['dateEnd'])


    def test_create_schedule_item_price_anon_user(self):
        """ Don't allow creating schedule item price for non-logged in users """
        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        classpass_dropin = f.OrganizationClasspassFactory.create()
        classpass_trial = f.OrganizationClasspassTrialFactory.create()

        query = self.schedule_item_price_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_class.pk)
        variables['input']['organizationClasspassDropin'] = to_global_id('OrganizationClasspassNode', classpass_dropin.pk)
        variables['input']['organizationClasspassTrial'] = to_global_id('OrganizationClasspassNode', classpass_trial.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_schedule_item_price_permission_granted(self):
        """ Allow creating schedule item prices for users with permissions """
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        classpass_dropin = f.OrganizationClasspassFactory.create()
        classpass_trial = f.OrganizationClasspassTrialFactory.create()

        query = self.schedule_item_price_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_class.pk)
        variables['input']['organizationClasspassDropin'] = to_global_id('OrganizationClasspassNode', classpass_dropin.pk)
        variables['input']['organizationClasspassTrial'] = to_global_id('OrganizationClasspassNode', classpass_trial.pk)

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createScheduleItemPrice']['scheduleItemPrice']['organizationClasspassDropin']['id'], 
                         variables['input']['organizationClasspassDropin'])


    def test_create_schedule_item_price_permission_denied(self):
        """ Check create schedule item price permission denied error message """
        # Create regular user
        user = f.RegularUserFactory.create()

        schedule_class = f.SchedulePublicWeeklyClassFactory.create()
        classpass_dropin = f.OrganizationClasspassFactory.create()
        classpass_trial = f.OrganizationClasspassTrialFactory.create()

        query = self.schedule_item_price_create_mutation
        variables = self.variables_create
        variables['input']['scheduleItem'] = to_global_id('ScheduleItemNode', schedule_class.pk)
        variables['input']['organizationClasspassDropin'] = to_global_id('OrganizationClasspassNode', classpass_dropin.pk)
        variables['input']['organizationClasspassTrial'] = to_global_id('OrganizationClasspassNode', classpass_trial.pk)

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_update_schedule_item_price(self):
        """ Update schedule item price """
        schedule_item_price = f.ScheduleItemPriceFactory.create()
        classpass_dropin = f.OrganizationClasspassFactory.create()
        classpass_trial = f.OrganizationClasspassTrialFactory.create()

        query = self.schedule_item_price_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemPriceNode', schedule_item_price.pk)
        variables['input']['organizationClasspassDropin'] = to_global_id('OrganizationClasspassNode', classpass_dropin.pk)
        variables['input']['organizationClasspassTrial'] = to_global_id('OrganizationClasspassNode', classpass_trial.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateScheduleItemPrice']['scheduleItemPrice']['organizationClasspassDropin']['id'], 
          variables['input']['organizationClasspassDropin'])
        self.assertEqual(data['updateScheduleItemPrice']['scheduleItemPrice']['organizationClasspassTrial']['id'], 
          variables['input']['organizationClasspassTrial'])
        self.assertEqual(data['updateScheduleItemPrice']['scheduleItemPrice']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['updateScheduleItemPrice']['scheduleItemPrice']['dateEnd'], variables['input']['dateEnd'])


    def test_update_schedule_item_price_anon_user(self):
        """ Don't allow updating schedule item prices for non-logged in users """
        schedule_item_price = f.ScheduleItemPriceFactory.create()
        query = self.schedule_item_price_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemPriceNode', schedule_item_price.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_schedule_item_price_permission_granted(self):
        """ Allow updating schedule item price for users with permissions """
        schedule_item_price = f.ScheduleItemPriceFactory.create()
        classpass_dropin = f.OrganizationClasspassFactory.create()
        classpass_trial = f.OrganizationClasspassTrialFactory.create()

        query = self.schedule_item_price_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemPriceNode', schedule_item_price.pk)
        variables['input']['organizationClasspassDropin'] = to_global_id('OrganizationClasspassNode', classpass_dropin.pk)
        variables['input']['organizationClasspassTrial'] = to_global_id('OrganizationClasspassNode', classpass_trial.pk)

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
        self.assertEqual(data['updateScheduleItemPrice']['scheduleItemPrice']['dateEnd'], variables['input']['dateEnd'])


    def test_update_schedule_item_price_permission_denied(self):
        """ Check update schedule item price permission denied error message """
        schedule_item_price = f.ScheduleItemPriceFactory.create()
        classpass_dropin = f.OrganizationClasspassFactory.create()
        classpass_trial = f.OrganizationClasspassTrialFactory.create()

        query = self.schedule_item_price_update_mutation
        variables = self.variables_update
        variables['input']['id'] = to_global_id('ScheduleItemPriceNode', schedule_item_price.pk)
        variables['input']['organizationClasspassDropin'] = to_global_id('OrganizationClasspassNode', classpass_dropin.pk)
        variables['input']['organizationClasspassTrial'] = to_global_id('OrganizationClasspassNode', classpass_trial.pk)

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


    def test_delete_schedule_item_price(self):
        """ Delete a schedule item price """
        schedule_item_price = f.ScheduleItemPriceFactory.create()
        query = self.schedule_item_price_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemPriceNode', schedule_item_price.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        
        self.assertEqual(data['deleteScheduleItemPrice']['ok'], True)

        exists = models.ScheduleItemPrice.objects.exists()
        self.assertEqual(exists, False)


    def test_delete_schedule_item_price_anon_user(self):
        """ Don't allow deleting schedule item prices for non logged in users """
        schedule_item_price = f.ScheduleItemPriceFactory.create()
        query = self.schedule_item_price_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemPriceNode', schedule_item_price.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_delete_schedule_item_price_permission_granted(self):
        """ Allow deleting schedule item prices for users with permissions """
        schedule_item_price = f.ScheduleItemPriceFactory.create()
        query = self.schedule_item_price_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemPriceNode', schedule_item_price.pk)

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
        self.assertEqual(data['deleteScheduleItemPrice']['ok'], True)


    def test_delete_schedule_item_price_permission_denied(self):
        """ Check delete schedule item price permission denied error message """
        schedule_item_price = f.ScheduleItemPriceFactory.create()
        query = self.schedule_item_price_delete_mutation
        variables = self.variables_delete
        variables['input']['id'] = to_global_id('ScheduleItemPriceNode', schedule_item_price.pk)
        
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

