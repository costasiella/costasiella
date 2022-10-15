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
        self.admin_user = f.AdminUserFactory.create()
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
                "price": "10",
                "financeTaxRate": to_global_id('FinanceTaxRateNode', self.finance_tax_rate.pk),
                "dateStart": '2019-01-01',
                "dateEnd": '2019-12-31',
            }
        }

        self.variables_update = {
            "input": {
                "id": to_global_id('OrganizationSubscriptionPriceNode', self.organization_subscription_price.pk),
                "price": "1466",
                "financeTaxRate": to_global_id('FinanceTaxRateNode', self.finance_tax_rate.pk),
                "dateStart": '2024-01-01',
                "dateEnd": '2024-12-31',
            }
        }

        self.variables_delete = {
            "input": {
                "id": to_global_id('OrganizationSubscriptionPriceNode', self.organization_subscription_price.pk),
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
  query OrganizationSubscriptionPrice($id: ID!, $after: String, $before: String, $archived: Boolean!) {
    organizationSubscriptionPrice(id:$id) {
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
    financeTaxRates(first: 15, before: $before, after: $after, archived: $archived) {
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
          percentage
          rateType
        }
      }
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

        self.subscription_price_update_mutation = '''
  mutation UpdateOrganizationSubscriptionPrice($input: UpdateOrganizationSubscriptionPriceInput!) {
    updateOrganizationSubscriptionPrice(input: $input) {
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

        self.subscription_price_delete_mutation = '''
  mutation DeleteOrganizationSubscriptionPrice($input: DeleteOrganizationSubscriptionPriceInput!) {
    deleteOrganizationSubscriptionPrice(input: $input) {
      ok
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
            'organizationSubscription': to_global_id('OrganizationSubscriptionNode',
                                                     self.organization_subscription_price.organization_subscription.pk),
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['organizationSubscriptionPrices']['edges'][0]['node']['organizationSubscription']['id'], 
            variables['organizationSubscription']
        )
        self.assertEqual(data['organizationSubscriptionPrices']['edges'][0]['node']['price'],
                         format(self.organization_subscription_price.price, ".2f"))
        self.assertEqual(data['organizationSubscriptionPrices']['edges'][0]['node']['financeTaxRate']['id'], 
          to_global_id('FinanceTaxRateNode', self.organization_subscription_price.finance_tax_rate.pk))
        self.assertEqual(data['organizationSubscriptionPrices']['edges'][0]['node']['dateStart'],
                         self.organization_subscription_price.date_start)
        self.assertEqual(data['organizationSubscriptionPrices']['edges'][0]['node']['dateEnd'],
                         self.organization_subscription_price.date_end)

    def test_query_permission_denied(self):
        """ Query list of location rooms """
        query = self.subscription_prices_query

        variables = {
            'organizationSubscription': to_global_id('OrganizationSubscriptionNode',
                                                     self.organization_subscription_price.organization_subscription.pk),
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of location rooms """
        query = self.subscription_prices_query

        variables = {
            'organizationSubscription': to_global_id('OrganizationSubscriptionNode', self.organization_subscription_price.organization_subscription.pk),
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationsubscriptionprice')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['organizationSubscriptionPrices']['edges'][0]['node']['price'],
                         format(self.organization_subscription_price.price, ".2f"))


    def test_query_anon_user(self):
        """ Query list of location rooms """
        query = self.subscription_prices_query
        variables = {
            'organizationSubscription': to_global_id('OrganizationSubscriptionNode', self.organization_subscription_price.organization_subscription.pk),
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one subscription price """   
        query = self.subscription_price_query

        variables = {
          "id": to_global_id('OrganizationSubscriptionPriceNode', self.organization_subscription_price.id),
          "archived": False # Used for tax rates
        }
       
        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['organizationSubscriptionPrice']['organizationSubscription']['id'],
                         to_global_id('OrganizationSubscriptionNode',
                                      self.organization_subscription_price.organization_subscription.pk))
        self.assertEqual(data['organizationSubscriptionPrice']['price'],
                         format(self.organization_subscription_price.price, ".2f"))
        self.assertEqual(data['organizationSubscriptionPrice']['financeTaxRate']['id'],
                         to_global_id('FinanceTaxRateNode', self.organization_subscription_price.finance_tax_rate.id))
        self.assertEqual(data['organizationSubscriptionPrice']['dateStart'],
                         self.organization_subscription_price.date_start)
        self.assertEqual(data['organizationSubscriptionPrice']['dateEnd'],
                         self.organization_subscription_price.date_end)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one subscription price """   
        query = self.subscription_price_query

        variables = {
          "id": to_global_id('OrganizationSubscriptionPriceNode', self.organization_subscription_price.id),
          "archived": False # Used for tax rates
        }
       
        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        query = self.subscription_price_query

        variables = {
          "id": to_global_id('OrganizationSubscriptionPriceNode', self.organization_subscription_price.id),
          "archived": False # Used for tax rates
        }
       
        # Now query single subscription price and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationsubscriptionprice')
        user.user_permissions.add(permission)
        user.save()
        
        query = self.subscription_price_query

        variables = {
          "id": to_global_id('OrganizationSubscriptionPriceNode', self.organization_subscription_price.id),
          "archived": False # Used for tax rates
        }
       
        # Now query single subscription price and check
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['organizationSubscriptionPrice']['price'],
                         format(self.organization_subscription_price.price, ".2f"))


    def test_create_subscription_price(self):
        """ Create a subscription price """
        query = self.subscription_price_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        errors = executed.get('errors')
        data = executed.get('data')

        self.assertEqual(
          data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['organizationSubscription']['id'], 
          variables['input']['organizationSubscription'])
        self.assertEqual(data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['price'], variables['input']['price'])
        self.assertEqual(data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['financeTaxRate']['id'], 
          variables['input']['financeTaxRate'])
        self.assertEqual(data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['dateEnd'], variables['input']['dateEnd'])


    def test_create_subscription_price_anon_user(self):
        """ Don't allow creating subscription prices for non-logged in users """
        query = self.subscription_price_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_create_subscription_price_permission_granted(self):
        """ Allow creating subscription prices for users with permissions """
        query = self.subscription_price_create_mutation

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
        self.assertEqual(data['createOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['price'], variables['input']['price'])


    def test_create_subscription_price_permission_denied(self):
        """ Check create subscription price permission denied error message """
        query = self.subscription_price_create_mutation
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


    def test_update_subscription_price(self):
        """ Update a subscription price """
        query = self.subscription_price_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['price'], variables['input']['price'])
        self.assertEqual(data['updateOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['financeTaxRate']['id'], 
          variables['input']['financeTaxRate'])
        self.assertEqual(data['updateOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['updateOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['dateEnd'], variables['input']['dateEnd'])


    def test_update_subscription_price_anon_user(self):
        """ Don't allow updating subscription prices for non-logged in users """
        query = self.subscription_price_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_subscription_price_permission_granted(self):
        """ Allow updating subscription prices for users with permissions """
        query = self.subscription_price_update_mutation
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
        self.assertEqual(data['updateOrganizationSubscriptionPrice']['organizationSubscriptionPrice']['price'], variables['input']['price'])


    def test_update_subscription_price_permission_denied(self):
        """ Check update subscription price permission denied error message """
        query = self.subscription_price_update_mutation
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


    def test_delete_subscription_price(self):
        """ Delete a subscription price """
        query = self.subscription_price_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        
        self.assertEqual(data['deleteOrganizationSubscriptionPrice']['ok'], True)

        exists = models.OrganizationSubscriptionPrice.objects.exists()
        self.assertEqual(exists, False)


    def test_delete_subscription_price_anon_user(self):
        """ Delete a subscription pricem """
        query = self.subscription_price_delete_mutation
        variables = self.variables_delete

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_delete_subscription_price_permission_granted(self):
        """ Allow deleting subscription prices for users with permissions """
        query = self.subscription_price_delete_mutation
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
        self.assertEqual(data['deleteOrganizationSubscriptionPrice']['ok'], True)


    def test_delete_subscription_price_permission_denied(self):
        """ Check delete subscription price permission denied error message """
        query = self.subscription_price_delete_mutation
        variables = self.variables_delete
        
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

