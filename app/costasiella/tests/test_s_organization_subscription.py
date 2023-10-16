# from graphql.error.located_error import GraphQLLocatedError
import graphql

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils import timezone
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema
from ..modules.finance_tools import display_float_as_amount
from ..modules.validity_tools import display_subscription_unit

from graphql_relay import to_global_id


class GQLOrganizationSubscription(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.maxDiff = None
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationsubscription'
        self.permission_add = 'add_organizationsubscription'
        self.permission_change = 'change_organizationsubscription'
        self.permission_delete = 'delete_organizationsubscription'

        self.finance_glaccount = f.FinanceGLAccountFactory.create()
        self.finance_costcenter = f.FinanceCostCenterFactory.create()

        self.variables_create = {
            "input": {
                "displayPublic": True,
                "displayShop": True,
                "name": "First subscription",
                "description": "Description",
                "sortOrder": 125,
                "minDuration": 3,
                "classes": 1,
                "subscriptionUnit": "WEEK",
                "reconciliationClasses": 1,
                "creditValidity": 1,
                "unlimited": False,
                "termsAndConditions": "T and C here",
                "registrationFee": 30,
                "quickStatsAmount": 12.5,
                "financeGlaccount": to_global_id("FinanceGLAccountNode", self.finance_glaccount.pk),
                "financeCostcenter": to_global_id("FinanceCostCenterNode", self.finance_costcenter.pk),
            }
        }

        self.variables_update = {
            "input": {
                "displayPublic": True,
                "displayShop": True,
                "name": "Updated subscription",
                "description": "Updated description",
                "sortOrder": 125,
                "minDuration": 3,
                "classes": 1,
                "subscriptionUnit": "WEEK",
                "reconciliationClasses": 1,
                "creditValidity": 1,
                "unlimited": False,
                "termsAndConditions": "T and C here",
                "registrationFee": 30,
                "quickStatsAmount": 12.5,
                "financeGlaccount": to_global_id("FinanceGLAccountNode", self.finance_glaccount.pk),
                "financeCostcenter": to_global_id("FinanceCostCenterNode", self.finance_costcenter.pk),
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.subscriptions_query = '''
  query OrganizationSubscriptions($after: String, $before: String, $archived: Boolean) {
    organizationSubscriptions(first: 15, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          displayPublic
          displayShop
          name
          description
          sortOrder
          minDuration
          classes
          subscriptionUnit
          subscriptionUnitDisplay
          reconciliationClasses
          creditValidity
          unlimited
          termsAndConditions
          registrationFee
          accountRegistrationFee
          priceFirstMonth
          quickStatsAmount
          financeGlaccount {
            id 
            name
          }
          financeCostcenter {
            id
            name
          }
        }
      }
    }
  }
'''

        self.subscription_query = '''
  query OrganizationSubscription($id: ID!, $after: String, $before: String, $archived: Boolean!) {
    organizationSubscription(id:$id) {
      id
      archived
      displayPublic
      displayShop
      name
      description
      sortOrder
      minDuration
      classes
      subscriptionUnit
      subscriptionUnitDisplay
      reconciliationClasses
      creditValidity
      unlimited
      termsAndConditions
      registrationFee
      accountRegistrationFee
      priceFirstMonth
      quickStatsAmount
      financeGlaccount {
        id 
        name
      }
      financeCostcenter {
        id
        name
      }
    }
    financeGlaccounts(first: 15, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          name
          code
        }
      }
    }
    financeCostcenters(first: 15, before: $before, after: $after, archived: $archived) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          archived
          name
          code
        }
      }
    }
  }
'''

        self.subscription_create_mutation = ''' 
  mutation CreateSubscription($input: CreateOrganizationSubscriptionInput!) {
    createOrganizationSubscription(input: $input) {
      organizationSubscription {
        id
        archived
        displayPublic
        displayShop
        name
        description
        sortOrder
        minDuration
        classes
        subscriptionUnit
        subscriptionUnitDisplay
        reconciliationClasses
        creditValidity
        unlimited
        termsAndConditions
        quickStatsAmount
        financeGlaccount {
          id
          name
        }
        financeCostcenter {
          id
          name
        }
      }
    }
  }
'''

        self.subscription_update_mutation = '''
  mutation UpdateOrganizationSubscription($input: UpdateOrganizationSubscriptionInput!) {
    updateOrganizationSubscription(input: $input) {
      organizationSubscription {
        id
        archived
        displayPublic
        displayShop
        name
        description
        sortOrder
        minDuration
        classes
        subscriptionUnit
        subscriptionUnitDisplay
        reconciliationClasses
        creditValidity
        unlimited
        termsAndConditions
        quickStatsAmount
        financeGlaccount {
          id
          name
        }
        financeCostcenter {
          id
          name
        }
      }
    }
  }
'''

        self.subscription_archive_mutation = '''
  mutation ArchiveOrganizationSubscription($input: ArchiveOrganizationSubscriptionInput!) {
    archiveOrganizationSubscription(input: $input) {
      organizationSubscription {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of subscriptions """
        today = timezone.now().date()

        query = self.subscriptions_query
        subscription = f.OrganizationSubscriptionFactory.create()
        variables = {
            'archived': False
        }      

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['archived'], subscription.archived)
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['displayPublic'], subscription.display_public)
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['displayShop'], subscription.display_shop)
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['name'], subscription.name)
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['description'], subscription.description)
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['sortOrder'], subscription.sort_order)
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['minDuration'], subscription.min_duration)
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['classes'], subscription.classes)
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['subscriptionUnit'], subscription.subscription_unit)
        self.assertEqual(
          data['organizationSubscriptions']['edges'][0]['node']['subscriptionUnitDisplay'], 
          display_subscription_unit(subscription.subscription_unit)
        )
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['accountRegistrationFee'],
                         format(subscription.registration_fee, '.2f'))
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['priceFirstMonth'],
                         subscription.get_price_first_month(today))
                         # format(subscription.get_price_first_month(today), ".2f"))
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['reconciliationClasses'],
                         subscription.reconciliation_classes)
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['creditValidity'],
                         subscription.credit_validity)
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['unlimited'], subscription.unlimited)
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['quickStatsAmount'],
                         format(subscription.quick_stats_amount, ".2f"))
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['financeGlaccount']['id'], 
          to_global_id("FinanceGLAccountNode", subscription.finance_glaccount.pk))
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['financeCostcenter']['id'], 
          to_global_id("FinanceCostCenterNode", subscription.finance_costcenter.pk))

    def test_query_permission_denied(self):
        """ Query list of subscriptions - check permission denied """
        query = self.subscriptions_query
        subscription = f.OrganizationSubscriptionFactory.create()
        non_public = f.OrganizationSubscriptionFactory.create()
        non_public.display_public = False
        non_public.display_shop = False
        non_public.save()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        # print(executed)
        data = executed.get('data')

        # Public subscriptions only
        non_public_found = False
        for item in data['organizationSubscriptions']['edges']:
            if not item['node']['displayPublic'] and not item['node']['displayShop']:
                non_public_found = True

        self.assertEqual(non_public_found, False)

    def test_query_permission_granted(self):
        """ Query list of subscriptions with view permission """
        query = self.subscriptions_query
        subscription = f.OrganizationSubscriptionFactory.create()
        non_public = f.OrganizationSubscriptionFactory.create()
        non_public.display_public = False
        non_public.save()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all class passes, including non public
        non_public_found = False
        for item in data['organizationSubscriptions']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        # Assert non public classtypes are listed
        self.assertEqual(non_public_found, True)

    def test_query_anon_user(self):
        """ Query list of subscriptions - anon user shouldn't see non public """
        query = self.subscriptions_query
        subscription = f.OrganizationSubscriptionFactory.create()
        subscription.display_public = False
        subscription.display_shop = False
        subscription.save()

        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(len(data['organizationSubscriptions']['edges']), 0)

    def test_query_anon_user_public(self):
        """ Query list of subscriptions - anon user should see public """
        query = self.subscriptions_query
        subscription = f.OrganizationSubscriptionFactory.create()

        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['organizationSubscriptions']['edges'][0]['node']['name'], subscription.name)

    def test_query_one(self):
        """ Query one subscriptions as admin """   
        subscription = f.OrganizationSubscriptionFactory.create()

        # Get node id
        node_id = to_global_id("OrganizationSubscriptionNode", subscription.pk)

        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single subscriptions and check
        executed = execute_test_client_api_query(self.subscription_query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['organizationSubscription']['archived'], subscription.archived)
        self.assertEqual(data['organizationSubscription']['displayPublic'], subscription.display_public)
        self.assertEqual(data['organizationSubscription']['displayShop'], subscription.display_shop)
        self.assertEqual(data['organizationSubscription']['name'], subscription.name)
        self.assertEqual(data['organizationSubscription']['description'], subscription.description)
        self.assertEqual(data['organizationSubscription']['sortOrder'], subscription.sort_order)
        self.assertEqual(data['organizationSubscription']['minDuration'], subscription.min_duration)
        self.assertEqual(data['organizationSubscription']['classes'], subscription.classes)
        self.assertEqual(data['organizationSubscription']['subscriptionUnit'], subscription.subscription_unit)
        self.assertEqual(
          data['organizationSubscription']['subscriptionUnitDisplay'], 
          display_subscription_unit(subscription.subscription_unit)
        )
        self.assertEqual(data['organizationSubscription']['reconciliationClasses'], subscription.reconciliation_classes)
        self.assertEqual(data['organizationSubscription']['creditValidity'],
                         subscription.credit_validity)
        self.assertEqual(data['organizationSubscription']['unlimited'], subscription.unlimited)
        self.assertEqual(data['organizationSubscription']['accountRegistrationFee'],
                         format(subscription.registration_fee, ".2f"))
        self.assertEqual(data['organizationSubscription']['quickStatsAmount'],
                         format(subscription.quick_stats_amount, ".2f"))
        self.assertEqual(data['organizationSubscription']['financeGlaccount']['id'], 
          to_global_id("FinanceGLAccountNode", subscription.finance_glaccount.pk))
        self.assertEqual(data['organizationSubscription']['financeCostcenter']['id'], 
          to_global_id("FinanceCostCenterNode", subscription.finance_costcenter.pk))

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one subscription """   
        subscription = f.OrganizationSubscriptionFactory.create()

        # Get node id
        node_id = to_global_id("OrganizationSubscriptionNode", subscription.pk)
        
        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single subscriptions and check
        executed = execute_test_client_api_query(self.subscription_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        subscription = f.OrganizationSubscriptionFactory.create()

        # Get node id
        node_id = to_global_id("OrganizationSubscriptionNode", subscription.pk)
        
        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single subscriptions and check
        executed = execute_test_client_api_query(self.subscription_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()
        subscription = f.OrganizationSubscriptionFactory.create()

        # Get node id
        node_id = to_global_id("OrganizationSubscriptionNode", subscription.pk)
        
        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single location and check   
        executed = execute_test_client_api_query(self.subscription_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['organizationSubscription']['name'], subscription.name)

    def test_create_subscriptions(self):
        """ Create a subscriptions """
        query = self.subscription_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['displayShop'], variables['input']['displayShop'])
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['archived'], False)
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['description'], variables['input']['description'])
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['sortOrder'], variables['input']['sortOrder'])
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['minDuration'], variables['input']['minDuration'])
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['classes'], variables['input']['classes'])
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['subscriptionUnit'], variables['input']['subscriptionUnit'])
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['reconciliationClasses'], variables['input']['reconciliationClasses'])
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['creditValidity'], variables['input']['creditValidity'])
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['unlimited'], variables['input']['unlimited'])
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['quickStatsAmount'],
                         str(variables['input']['quickStatsAmount']))
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['financeCostcenter']['id'], variables['input']['financeCostcenter'])

    def test_create_subscriptions_anon_user(self):
        """ Don't allow creating subscriptions for non-logged in users """
        query = self.subscription_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_location_permission_granted(self):
        """ Allow creating subscriptions for users with permissions """
        query = self.subscription_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationSubscription']['organizationSubscription']['name'], variables['input']['name'])

    def test_create_subscriptions_permission_denied(self):
        """ Check create subscriptions permission denied error message """
        query = self.subscription_create_mutation
        variables = self.variables_create

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

    def test_update_subscriptions(self):
        """ Update a subscriptions """
        query = self.subscription_update_mutation
        subscription = f.OrganizationSubscriptionFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationSubscriptionNode", subscription.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['displayShop'], variables['input']['displayShop'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['archived'], False)
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['description'], variables['input']['description'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['sortOrder'], variables['input']['sortOrder'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['minDuration'], variables['input']['minDuration'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['classes'], variables['input']['classes'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['subscriptionUnit'], variables['input']['subscriptionUnit'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['reconciliationClasses'], variables['input']['reconciliationClasses'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['creditValidity'], variables['input']['creditValidity'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['unlimited'], variables['input']['unlimited'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['quickStatsAmount'],
                         str(variables['input']['quickStatsAmount']))
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['financeCostcenter']['id'], variables['input']['financeCostcenter'])

    def test_update_subscriptions_anon_user(self):
        """ Don't allow updating subscriptions for non-logged in users """
        query = self.subscription_update_mutation
        subscription = f.OrganizationSubscriptionFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationSubscriptionNode", subscription.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_subscriptions_permission_granted(self):
        """ Allow updating subscriptions for users with permissions """
        query = self.subscription_update_mutation
        subscription = f.OrganizationSubscriptionFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationSubscriptionNode", subscription.pk)

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
  
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationSubscription']['organizationSubscription']['description'], variables['input']['description'])

    def test_update_subscriptions_permission_denied(self):
        """ Check update subscriptions permission denied error message """
        query = self.subscription_update_mutation
        subscription = f.OrganizationSubscriptionFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationSubscriptionNode", subscription.pk)

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

    def test_archive_subscriptions(self):
        """ Archive a subscriptions """
        query = self.subscription_archive_mutation
        subscription = f.OrganizationSubscriptionFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationSubscriptionNode", subscription.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationSubscription']['organizationSubscription']['archived'], variables['input']['archived'])

    def test_archive_subscriptions_anon_user(self):
        """ Archive subscriptions denied for anon user """
        query = self.subscription_archive_mutation
        subscription = f.OrganizationSubscriptionFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationSubscriptionNode", subscription.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_archive_subscriptions_permission_granted(self):
        """ Allow archiving subscriptions for users with permissions """
        query = self.subscription_archive_mutation
        subscription = f.OrganizationSubscriptionFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationSubscriptionNode", subscription.pk)

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
        self.assertEqual(data['archiveOrganizationSubscription']['organizationSubscription']['archived'], variables['input']['archived'])

    def test_archive_subscriptions_permission_denied(self):
        """ Check archive subscriptions permission denied error message """
        query = self.subscription_archive_mutation
        subscription = f.OrganizationSubscriptionFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationSubscriptionNode", subscription.pk)
        
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
