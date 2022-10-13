# from graphql.error.located_error import GraphQLLocatedError
import graphql

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
from ..modules.finance_tools import display_float_as_amount
from ..modules.validity_tools import display_validity_unit

from graphql_relay import to_global_id


class GQLOrganizationMembership(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationmembership'
        self.permission_add = 'add_organizationmembership'
        self.permission_change = 'change_organizationmembership'
        self.permission_delete = 'delete_organizationmembership'

        self.finance_tax_rate = f.FinanceTaxRateFactory.create()
        self.finance_glaccount = f.FinanceGLAccountFactory.create()
        self.finance_costcenter = f.FinanceCostCenterFactory.create()

        self.variables_create = {
            "input": {
                "displayPublic": True,
                "displayShop": True,
                "name": "First membership",
                "description": "Description",
                "price": "12.50",
                "financeTaxRate": to_global_id("FinanceTaxRateNode", self.finance_tax_rate.pk),
                "validity": 1,
                "validityUnit": "MONTHS",
                "termsAndConditions": "T and C",
                "financeGlaccount": to_global_id("FinanceGLAccountNode", self.finance_glaccount.pk),
                "financeCostcenter": to_global_id("FinanceCostCenterNode", self.finance_costcenter.pk),
            }
        }

        self.variables_update = {
            "input": {
                "displayPublic": True,
                "displayShop": True,
                "name": "Updated membership",
                "description": "Description",
                "price": "12.50",
                "financeTaxRate": to_global_id("FinanceTaxRateNode", self.finance_tax_rate.pk),
                "validity": 1,
                "validityUnit": "MONTHS",
                "termsAndConditions": "T and C",
                "financeGlaccount": to_global_id("FinanceGLAccountNode", self.finance_glaccount.pk),
                "financeCostcenter": to_global_id("FinanceCostCenterNode", self.finance_costcenter.pk),
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.memberships_query = '''
  query OrganizationMemberships($after: String, $before: String, $archived: Boolean) {
    organizationMemberships(first: 15, before: $before, after: $after, archived: $archived) {
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
          price
          priceDisplay
          financeTaxRate {
            id
            name
          }
          validity
          validityUnit
          validityUnitDisplay
          termsAndConditions
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

        self.membership_query = '''
  query OrganizationMembership($id: ID!, $after: String, $before: String, $archived: Boolean!) {
    organizationMembership(id:$id) {
      id
      archived
      displayPublic
      displayShop
      name
      description
      price
      priceDisplay
      financeTaxRate {
        id
        name
      }
      validity
      validityUnit
      validityUnitDisplay
      termsAndConditions
      financeGlaccount {
        id 
        name
      }
      financeCostcenter {
        id
        name
      }
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

        self.membership_create_mutation = ''' 
  mutation CreateMembership($input: CreateOrganizationMembershipInput!) {
    createOrganizationMembership(input: $input) {
      organizationMembership {
        id
        archived
        displayPublic
        displayShop
        name
        description
        price
        financeTaxRate {
          id
          name
        }
        validity
        validityUnit
        termsAndConditions
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

        self.membership_update_mutation = '''
  mutation UpdateOrganizationMembership($input: UpdateOrganizationMembershipInput!) {
    updateOrganizationMembership(input: $input) {
        organizationMembership {
          id
          archived
          displayPublic
          displayShop
          name
          description
          price
          financeTaxRate {
            id
            name
          }
          validity
          validityUnit
          termsAndConditions
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

        self.membership_archive_mutation = '''
  mutation ArchiveOrganizationMembership($input: ArchiveOrganizationMembershipInput!) {
    archiveOrganizationMembership(input: $input) {
      organizationMembership {
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
        """ Query list of memberships """
        query = self.memberships_query
        membership = f.OrganizationMembershipFactory.create()
        variables = {
            'archived': False
        }      

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['archived'], membership.archived)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['displayPublic'], membership.display_public)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['displayShop'], membership.display_shop)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['name'], membership.name)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['description'], membership.description)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['price'], format(membership.price, ".2f"))
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['priceDisplay'],
                         display_float_as_amount(membership.price))
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['financeTaxRate']['id'], 
          to_global_id("FinanceTaxRateNode", membership.finance_tax_rate.pk))
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['validity'], membership.validity)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['validityUnit'], membership.validity_unit)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['validityUnitDisplay'],
                         display_validity_unit(membership.validity_unit, membership.validity))
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['financeGlaccount']['id'], 
          to_global_id("FinanceGLAccountNode", membership.finance_glaccount.pk))
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['financeCostcenter']['id'], 
          to_global_id("FinanceCostCenterNode", membership.finance_costcenter.pk))

    def test_query_permission_denied(self):
        """ Query list of memberships - check permission denied """
        query = self.memberships_query
        membership = f.OrganizationMembershipFactory.create()
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permission_granted(self):
        """ Query list of memberships with view permission """
        query = self.memberships_query
        membership = f.OrganizationMembershipFactory.create()
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationmembership')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all memberships
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['archived'], membership.archived)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['displayPublic'], membership.display_public)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['displayShop'], membership.display_shop)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['name'], membership.name)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['description'], membership.description)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['price'], format(membership.price, ".2f"))
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['priceDisplay'], display_float_as_amount(membership.price))
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['financeTaxRate']['id'], 
          to_global_id("FinanceTaxRateNode", membership.finance_tax_rate.pk))
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['validity'], membership.validity)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['validityUnit'], membership.validity_unit)
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['validityUnitDisplay'],
                         display_validity_unit(membership.validity_unit, membership.validity))
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['financeGlaccount']['id'], 
          to_global_id("FinanceGLAccountNode", membership.finance_glaccount.pk))
        self.assertEqual(data['organizationMemberships']['edges'][0]['node']['financeCostcenter']['id'], 
          to_global_id("FinanceCostCenterNode", membership.finance_costcenter.pk))

    def test_query_anon_user(self):
        """ Query list of memberships - anon user """
        query = self.memberships_query
        membership = f.OrganizationMembershipFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one memberships as admin """   
        membership = f.OrganizationMembershipFactory.create()

        # Get node id
        node_id = to_global_id("OrganizationMembershipNode", membership.pk)

        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single memberships and check
        executed = execute_test_client_api_query(self.membership_query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['organizationMembership']['displayPublic'], membership.display_public)
        self.assertEqual(data['organizationMembership']['displayShop'], membership.display_shop)
        self.assertEqual(data['organizationMembership']['archived'], membership.archived)
        self.assertEqual(data['organizationMembership']['name'], membership.name)
        self.assertEqual(data['organizationMembership']['price'], format(membership.price, ".2f"))
        self.assertEqual(data['organizationMembership']['priceDisplay'], display_float_as_amount(membership.price))
        self.assertEqual(data['organizationMembership']['financeTaxRate']['id'], 
          to_global_id("FinanceTaxRateNode", membership.finance_tax_rate.pk))
        self.assertEqual(data['organizationMembership']['validity'], membership.validity)
        self.assertEqual(data['organizationMembership']['validityUnit'], membership.validity_unit)
        self.assertEqual(data['organizationMembership']['validityUnitDisplay'],
                         display_validity_unit(membership.validity_unit, membership.validity))
        self.assertEqual(data['organizationMembership']['financeGlaccount']['id'], 
          to_global_id("FinanceGLAccountNode", membership.finance_glaccount.pk))
        self.assertEqual(data['organizationMembership']['financeCostcenter']['id'], 
          to_global_id("FinanceCostCenterNode", membership.finance_costcenter.pk))
        

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one membership """   
        membership = f.OrganizationMembershipFactory.create()

        # Get node id
        node_id = to_global_id("OrganizationMembershipNode", membership.pk)
        
        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single memberships and check
        executed = execute_test_client_api_query(self.membership_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        membership = f.OrganizationMembershipFactory.create()

        # Get node id
        node_id = to_global_id("OrganizationMembershipNode", membership.pk)
        
        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single memberships and check
        executed = execute_test_client_api_query(self.membership_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationmembership')
        user.user_permissions.add(permission)
        user.save()
        membership = f.OrganizationMembershipFactory.create()

        # Get node id
        node_id = to_global_id("OrganizationMembershipNode", membership.pk)
        
        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single location and check   
        executed = execute_test_client_api_query(self.membership_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['organizationMembership']['name'], membership.name)


    def test_create_memberships(self):
        """ Create a memberships """
        query = self.membership_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['displayShop'], variables['input']['displayShop'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['archived'], False)
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['description'], variables['input']['description'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['price'], variables['input']['price'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['financeTaxRate']['id'], variables['input']['financeTaxRate'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['validity'], variables['input']['validity'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['validityUnit'], variables['input']['validityUnit'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['termsAndConditions'], variables['input']['termsAndConditions'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['financeCostcenter']['id'], variables['input']['financeCostcenter'])


    def test_create_memberships_anon_user(self):
        """ Don't allow creating memberships for non-logged in users """
        query = self.membership_create_mutation
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
        """ Allow creating memberships for users with permissions """
        query = self.membership_create_mutation
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
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['displayShop'], variables['input']['displayShop'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['archived'], False)
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['description'], variables['input']['description'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['price'], variables['input']['price'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['financeTaxRate']['id'], variables['input']['financeTaxRate'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['validity'], variables['input']['validity'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['validityUnit'], variables['input']['validityUnit'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['termsAndConditions'], variables['input']['termsAndConditions'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
        self.assertEqual(data['createOrganizationMembership']['organizationMembership']['financeCostcenter']['id'], variables['input']['financeCostcenter'])


    def test_create_memberships_permission_denied(self):
        """ Check create memberships permission denied error message """
        query = self.membership_create_mutation
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


    def test_update_memberships(self):
        """ Update a memberships """
        query = self.membership_update_mutation
        membership = f.OrganizationMembershipFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationMembershipNode", membership.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['displayShop'], variables['input']['displayShop'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['archived'], False)
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['description'], variables['input']['description'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['price'], variables['input']['price'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['financeTaxRate']['id'], variables['input']['financeTaxRate'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['validity'], variables['input']['validity'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['validityUnit'], variables['input']['validityUnit'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['termsAndConditions'], variables['input']['termsAndConditions'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['financeCostcenter']['id'], variables['input']['financeCostcenter'])


    def test_update_memberships_anon_user(self):
        """ Don't allow updating memberships for non-logged in users """
        query = self.membership_update_mutation
        membership = f.OrganizationMembershipFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationMembershipNode", membership.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_memberships_permission_granted(self):
        """ Allow updating memberships for users with permissions """
        query = self.membership_update_mutation
        membership = f.OrganizationMembershipFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationMembershipNode", membership.pk)

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
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['displayShop'], variables['input']['displayShop'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['archived'], False)
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['description'], variables['input']['description'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['price'], variables['input']['price'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['financeTaxRate']['id'], variables['input']['financeTaxRate'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['validity'], variables['input']['validity'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['validityUnit'], variables['input']['validityUnit'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['termsAndConditions'], variables['input']['termsAndConditions'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
        self.assertEqual(data['updateOrganizationMembership']['organizationMembership']['financeCostcenter']['id'], variables['input']['financeCostcenter'])


    def test_update_memberships_permission_denied(self):
        """ Check update memberships permission denied error message """
        query = self.membership_update_mutation
        membership = f.OrganizationMembershipFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationMembershipNode", membership.pk)

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


    def test_archive_memberships(self):
        """ Archive a memberships """
        query = self.membership_archive_mutation
        membership = f.OrganizationMembershipFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationMembershipNode", membership.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['archiveOrganizationMembership']['organizationMembership']['archived'], variables['input']['archived'])


    def test_archive_memberships_anon_user(self):
        """ Archive memberships denied for anon user """
        query = self.membership_archive_mutation
        membership = f.OrganizationMembershipFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationMembershipNode", membership.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_memberships_permission_granted(self):
        """ Allow archiving memberships for users with permissions """
        query = self.membership_archive_mutation
        membership = f.OrganizationMembershipFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationMembershipNode", membership.pk)

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
        self.assertEqual(data['archiveOrganizationMembership']['organizationMembership']['archived'], variables['input']['archived'])


    def test_archive_memberships_permission_denied(self):
        """ Check archive memberships permission denied error message """
        query = self.membership_archive_mutation
        membership = f.OrganizationMembershipFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationMembershipNode", membership.pk)
        
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

