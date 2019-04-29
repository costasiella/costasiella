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


class GQLOrganizationSubscriptionPrice(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationsubscriptionprice'
        self.permission_add = 'add_organizationsubscriptionprice'
        self.permission_change = 'change_organizationsubscriptionprice'
        self.permission_delete = 'delete_organizationsubscriptionprice'

        self.organization_subscription = f.OrganizationSubscriptionFactory.create()
        self.finance_tax_rate = f.FinanceTaxRateFactory.create()
        self.organization_subscription_price = f.OrganizationSubscriptionPriceFactory.create()

        self.variables_create = {
            "input": {
                "organizationSubscription": to_global_id('OrganizationSubscriptionNode', self.organization_subscription.pk),
                "price": 10,
                "financeTaxRate": to_global_id('FinanceTaxRateNode', self.finance_tax_rate.pk),
                "dateStart": '2019-01-01',
                "dateEnd": '2019-12-31',
            }
        }

        self.variables_update = {
            "input": {
                "id": to_global_id('OrganizationSubscriptionPriceNode', self.organization_subscription_price.pk),
                "displayPublic": True,
                "name": "Updated room",
            }
        }

        self.variables_archive = {
            "input": {
                "id": to_global_id('OrganizationSubscriptionPriceNode', self.organization_subscription_price.pk),
                "archived": True,
            }
        }

        self.subscription_prices_query = '''
  query OrganizationSubscriptionPrices($after: String, $before: String, $organizationSubscription: ID!) {
    organizationSubscriptionPrices(first: 15, before: $before, after: $after, organizationSubscription: $organizationSubscription) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationSubscription {
            id
            name
          }
          price
          priceDisplay
          financeTaxRate {
            id
            name
          }
          dateStart
          dateEnd
        }
      }
    }
    organizationSubscription(id: $organizationSubscription) {
      id
      name
    }
  }
'''

        self.subscription_price_query = '''
  query OrganizationSubscriptionPrice($id: ID!) {
    organizationSubscriptionPrice(id:$id) {
      id
      organizationSubscription {
        id
        name
      }
      name
      displayPublic
      archived
    }
  }
'''

        self.subscription_price_create_mutation = ''' 
  mutation CreateOrganizationSubscriptionPrice($input: CreateOrganizationSubscriptionPriceInput!) {
    createOrganizationSubscriptionPrice(input: $input) {
      organizationSubscriptionPrice {
        id
        organizationSubscription {
          id
          name
        }
        archived
        displayPublic
        name
      }
    }
  }
'''

        self.subscription_price_update_mutation = '''
  mutation UpdateOrganizationSubscriptionPrice($input: UpdateOrganizationSubscriptionPriceInput!) {
    updateOrganizationSubscriptionPrice(input: $input) {
      organizationSubscriptionPrice {
        id
        organizationSubscription {
          id
          name
        }
        name
        displayPublic
      }
    }
  }
'''

        self.subscription_price_archive_mutation = '''
  mutation ArchiveOrganizationSubscriptionPrice($input: ArchiveOrganizationSubscriptionPriceInput!) {
    archiveOrganizationSubscriptionPrice(input: $input) {
      organizationSubscriptionPrice {
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
        """ Query list of locations """
        query = self.subscription_prices_query

        variables = {
            'organizationSubscription': to_global_id('OrganizationSubscriptionNode', self.organization_subscription_price.organization_subscription.pk),
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['organizationSubscriptionPrices']['edges'][0]['node']['organizationSubscription']['id'], 
            variables['organizationSubscription']
        )
        self.assertEqual(data['organizationSubscriptionPrices']['edges'][0]['node']['price'], self.organization_subscription_price.price)
        self.assertEqual(data['organizationSubscriptionPrices']['edges'][0]['node']['financeTaxRate']['id'], 
          to_global_id('FinanceTaxRateNode', self.organization_subscription_price.finance_tax_rate.pk))
        self.assertEqual(data['organizationSubscriptionPrices']['edges'][0]['node']['dateStart'], self.organization_subscription_price.date_start)
        self.assertEqual(data['organizationSubscriptionPrices']['edges'][0]['node']['dateEnd'], self.organization_subscription_price.date_end)


    # def test_query_permision_denied(self):
    #     """ Query list of location rooms """
    #     query = self.subscription_prices_query
    #     subscription_price = f.OrganizationSubscriptionPriceFactory.create()
    #     non_public_subscription_price = f.OrganizationSubscriptionPriceFactory.build()
    #     non_public_subscription_price.organization_subscription = subscription_price.organization_subscription
    #     non_public_subscription_price.display_public = False
    #     non_public_subscription_price.save()

    #     variables = {
    #         'organizationSubscription': to_global_id('OrganizationSubscriptionNode', subscription_price.organization_subscription.pk),
    #         'archived': False
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')

    #     # Public locations only
    #     non_public_found = False
    #     for item in data['organizationSubscriptionPrices']['edges']:
    #         if not item['node']['displayPublic']:
    #             non_public_found = True

    #     self.assertEqual(non_public_found, False)


    # def test_query_permision_granted(self):
    #     """ Query list of location rooms """
    #     query = self.subscription_prices_query
    #     subscription_price = f.OrganizationSubscriptionPriceFactory.create()
    #     non_public_subscription_price = f.OrganizationSubscriptionPriceFactory.build()
    #     non_public_subscription_price.organization_subscription = subscription_price.organization_subscription
    #     non_public_subscription_price.display_public = False
    #     non_public_subscription_price.save()

    #     variables = {
    #         'organizationSubscription': to_global_id('OrganizationSubscriptionNode', subscription_price.organization_subscription.pk),
    #         'archived': False
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_organizationsubscriptionprice')
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')

    #     # List all locations, including non public
    #     non_public_found = False
    #     for item in data['organizationSubscriptionPrices']['edges']:
    #         if not item['node']['displayPublic']:
    #             non_public_found = True

    #     # Assert non public locations are listed
    #     self.assertEqual(non_public_found, True)


    # def test_query_anon_user(self):
    #     """ Query list of location rooms """
    #     query = self.subscription_prices_query
    #     subscription_price = f.OrganizationSubscriptionPriceFactory.create()
    #     variables = {
    #         'organizationSubscription': to_global_id('OrganizationSubscriptionNode', subscription_price.organization_subscription.pk),
    #         'archived': False
    #     }

    #     executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one(self):
    #     """ Query one location room """   
    #     subscription_price = f.OrganizationSubscriptionPriceFactory.create()

    #     # First query locations to get node id easily
    #     node_id = to_global_id('OrganizationSubscriptionPriceNode', subscription_price.pk)

    #     # Now query single location and check
    #     query = self.subscription_price_query
    #     executed = execute_test_client_api_query(query, self.admin_user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['organizationSubscriptionPrice']['organizationSubscription']['id'], 
    #       to_global_id('OrganizationSubscriptionNode', subscription_price.organization_subscription.pk))
    #     self.assertEqual(data['organizationSubscriptionPrice']['name'], subscription_price.name)
    #     self.assertEqual(data['organizationSubscriptionPrice']['archived'], subscription_price.archived)
    #     self.assertEqual(data['organizationSubscriptionPrice']['displayPublic'], subscription_price.display_public)


    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one location room """   
    #     subscription_price = f.OrganizationSubscriptionPriceFactory.create()

    #     # First query locations to get node id easily
    #     node_id = to_global_id('OrganizationSubscriptionPriceNode', subscription_price.pk)

    #     # Now query single location and check
    #     query = self.subscription_price_query
    #     executed = execute_test_client_api_query(query, self.anon_user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     subscription_price = f.OrganizationSubscriptionPriceFactory.create()

    #     # First query locations to get node id easily
    #     node_id = to_global_id('OrganizationSubscriptionPriceNode', subscription_price.pk)

    #     # Now query single location and check
    #     query = self.subscription_price_query
    #     executed = execute_test_client_api_query(query, user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_organizationsubscriptionprice')
    #     user.user_permissions.add(permission)
    #     user.save()
    #     subscription_price = f.OrganizationSubscriptionPriceFactory.create()

    #     # First query locations to get node id easily
    #     node_id = to_global_id('OrganizationSubscriptionPriceNode', subscription_price.pk)

    #     # Now query single location and check   
    #     query = self.subscription_price_query
    #     executed = execute_test_client_api_query(query, user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['organizationSubscriptionPrice']['name'], subscription_price.name)


    # def test_create_subscription_price(self):
    #     """ Create a location room """
    #     query = self.subscription_price_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )

    #     data = executed.get('data')
    #     self.assertEqual(
    #       data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['organizationSubscription']['id'], 
    #       variables['input']['organizationSubscription'])
    #     self.assertEqual(data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['name'], variables['input']['name'])
    #     self.assertEqual(data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['archived'], False)
    #     self.assertEqual(data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['displayPublic'], variables['input']['displayPublic'])


    # def test_create_subscription_price_anon_user(self):
    #     """ Don't allow creating locations rooms for non-logged in users """
    #     query = self.subscription_price_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_create_subscription_price_permission_granted(self):
    #     """ Allow creating location rooms for users with permissions """
    #     query = self.subscription_price_create_mutation

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
    #     self.assertEqual(
    #       data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['organizationSubscription']['id'], 
    #       variables['input']['organizationSubscription'])
    #     self.assertEqual(data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['name'], variables['input']['name'])
    #     self.assertEqual(data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['archived'], False)
    #     self.assertEqual(data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['displayPublic'], variables['input']['displayPublic'])


    # def test_create_subscription_price_permission_denied(self):
    #     """ Check create location room permission denied error message """
    #     query = self.subscription_price_create_mutation
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


    # def test_update_subscription_price(self):
    #     """ Update a location room """
    #     query = self.subscription_price_update_mutation
    #     variables = self.variables_update

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )

    #     data = executed.get('data')
    #     self.assertEqual(data['updateOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['displayPublic'], variables['input']['displayPublic'])


    # def test_update_subscription_price_anon_user(self):
    #     """ Don't allow updating location rooms for non-logged in users """
    #     query = self.subscription_price_update_mutation
    #     variables = self.variables_update

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_subscription_price_permission_granted(self):
    #     """ Allow updating location rooms for users with permissions """
    #     query = self.subscription_price_update_mutation
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
    #     self.assertEqual(data['updateOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['displayPublic'], variables['input']['displayPublic'])


    # def test_update_subscription_price_permission_denied(self):
    #     """ Check update location room permission denied error message """
    #     query = self.subscription_price_update_mutation
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


    # def test_archive_subscription_price(self):
    #     """ Archive a location room"""
    #     query = self.subscription_price_archive_mutation
    #     variables = self.variables_archive

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['archiveOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['archived'], variables['input']['archived'])


    # def test_archive_subscription_price_anon_user(self):
    #     """ Archive a location room """
    #     query = self.subscription_price_archive_mutation
    #     variables = self.variables_archive

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_archive_subscription_price_permission_granted(self):
    #     """ Allow archiving locations for users with permissions """
    #     query = self.subscription_price_archive_mutation
    #     variables = self.variables_archive

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
    #     self.assertEqual(data['archiveOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['archived'], variables['input']['archived'])


    # def test_archive_subscription_price_permission_denied(self):
    #     """ Check archive location room permission denied error message """
    #     query = self.subscription_price_archive_mutation
    #     variables = self.variables_archive
        
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

