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


class GQLOrganizationClasspass(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_finance_taxrate = 'view_financetaxrate'
        self.permission_view_finance_costcenter = 'view_financecostcenter'
        self.permission_view_finance_glaccount = 'view_financeglaccount'
        self.permission_view = 'view_organizationclasspass'
        self.permission_add = 'add_organizationclasspass'
        self.permission_change = 'change_organizationclasspass'
        self.permission_delete = 'delete_organizationclasspass'

        self.finance_tax_rate = f.FinanceTaxRateFactory.create()
        self.finance_glaccount = f.FinanceGLAccountFactory.create()
        self.finance_costcenter = f.FinanceCostCenterFactory.create()

        self.variables_create = {
            "input": {
                "displayPublic": True,
                "displayShop": True,
                "name": "First classpass",
                "description": "Description",
                "price": "125",
                "financeTaxRate": to_global_id("FinanceTaxRateNode", self.finance_tax_rate.pk),
                "validity": 1,
                "validityUnit": "MONTHS",
                "classes": 10,
                "unlimited": False,
                "quickStatsAmount": "12.5",
                "financeGlaccount": to_global_id("FinanceGLAccountNode", self.finance_glaccount.pk),
                "financeCostcenter": to_global_id("FinanceCostCenterNode", self.finance_costcenter.pk),
            }
        }

        self.variables_create_trial = {
            "input": {
                "displayPublic": True,
                "displayShop": True,
                "trialPass": True,
                "name": "Trial pass",
                "description": "Description",
                "price": "15",
                "financeTaxRate": to_global_id("FinanceTaxRateNode", self.finance_tax_rate.pk),
                "validity": 1,
                "validityUnit": "DAYS",
                "classes": 1,
                "unlimited": False,
                "quickStatsAmount": "15",
                "financeGlaccount": to_global_id("FinanceGLAccountNode", self.finance_glaccount.pk),
                "financeCostcenter": to_global_id("FinanceCostCenterNode", self.finance_costcenter.pk),
            }
        }

        self.variables_update = {
            "input": {
                "displayPublic": True,
                "displayShop": True,
                "trialPass": True,
                "name": "Updated classpass",
                "description": "Description",
                "price": "125" ,
                "financeTaxRate": to_global_id("FinanceTaxRateNode", self.finance_tax_rate.pk),
                "validity": 1,
                "validityUnit": "MONTHS",
                "classes": 10,
                "unlimited": False,
                "quickStatsAmount": "12.5",
                "financeGlaccount": to_global_id("FinanceGLAccountNode", self.finance_glaccount.pk),
                "financeCostcenter": to_global_id("FinanceCostCenterNode", self.finance_costcenter.pk),
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.classpasses_query = '''
  query OrganizationClasspasses($after: String, $before: String, $archived: Boolean) {
    organizationClasspasses(first: 15, before: $before, after: $after, archived: $archived) {
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
          trialPass
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
          classes
          unlimited
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

        self.classpass_query = '''
  query OrganizationClasspass($id: ID!, $after: String, $before: String, $archived: Boolean!) {
    organizationClasspass(id:$id) {
      id
      archived
      displayPublic
      displayShop
      trialPass
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
      classes
      unlimited
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

        self.classpass_create_mutation = ''' 
  mutation CreateClasspass($input: CreateOrganizationClasspassInput!) {
    createOrganizationClasspass(input: $input) {
      organizationClasspass {
        id
        archived
        displayPublic
        displayShop
        trialPass
        name
        description
        price
        financeTaxRate {
          id
          name
        }
        validity
        validityUnit
        classes
        unlimited
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

        self.classpass_update_mutation = '''
  mutation UpdateOrganizationClasspass($input: UpdateOrganizationClasspassInput!) {
    updateOrganizationClasspass(input: $input) {
      organizationClasspass {
        id
        archived
        displayPublic
        displayShop
        trialPass
        name
        description
        price
        financeTaxRate {
          id
          name
        }
        validity
        validityUnit
        classes
        unlimited
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

        self.classpass_archive_mutation = '''
  mutation ArchiveOrganizationClasspass($input: ArchiveOrganizationClasspassInput!) {
    archiveOrganizationClasspass(input: $input) {
      organizationClasspass {
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
        """ Query list of classpasses """
        query = self.classpasses_query
        classpass = f.OrganizationClasspassFactory.create()
        variables = {
            'archived': False
        }      

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['archived'], classpass.archived)
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['displayPublic'], classpass.display_public)
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['displayShop'], classpass.display_shop)
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['trialPass'], classpass.trial_pass)
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['name'], classpass.name)
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['description'], classpass.description)
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['price'],
                         format(classpass.price, ".2f"))
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['priceDisplay'],
                         display_float_as_amount(classpass.price))
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['financeTaxRate']['id'], 
                         to_global_id("FinanceTaxRateNode", classpass.finance_tax_rate.pk))
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['validityUnit'],
                         classpass.validity_unit)
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['validityUnitDisplay'],
                         display_validity_unit(classpass.validity_unit, classpass.validity))
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['classes'], classpass.classes)
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['unlimited'], classpass.unlimited)
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['quickStatsAmount'],
                         format(classpass.quick_stats_amount, '.2f'))
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['financeGlaccount']['id'], 
                         to_global_id("FinanceGLAccountNode", classpass.finance_glaccount.pk))
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['financeCostcenter']['id'], 
                         to_global_id("FinanceCostCenterNode", classpass.finance_costcenter.pk))

    def test_query_permission_denied(self):
        """ Query list of classpasses - check permission denied """
        query = self.classpasses_query
        classpass = f.OrganizationClasspassFactory.create()
        non_public = f.OrganizationClasspassFactory.create()
        non_public.display_public = False
        non_public.save()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # Public class only
        non_public_found = False
        for item in data['organizationClasspasses']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)

    def test_query_permission_granted(self):
        """ Query list of classpasses with view permission """
        query = self.classpasses_query
        classpass = f.OrganizationClasspassFactory.create()
        non_public = f.OrganizationClasspassFactory.create()
        non_public.display_public = False
        non_public.save()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationclasspass')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all class passes, including non public
        non_public_found = False
        for item in data['organizationClasspasses']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        # Assert non public classtypes are listed
        self.assertEqual(non_public_found, True)

    def test_query_anon_user_dont_show_archived_for_anon_users(self):
        """ Query list of classpasses - anon user """
        query = self.classpasses_query
        classpass = f.OrganizationClasspassFactory.create()
        classpass.archived = True
        classpass.save()

        variables = {
            'archived': True
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(len(data['organizationClasspasses']['edges']), 0)

    def test_query_anon_user_show_non_archived_for_anon_users(self):
        """ Query list of classpasses - anon user """
        query = self.classpasses_query
        classpass = f.OrganizationClasspassFactory.create()

        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['organizationClasspasses']['edges'][0]['node']['name'], classpass.name)

    def test_query_one(self):
        """ Query one classpasses as admin """   
        classpass = f.OrganizationClasspassFactory.create()

        # Get node id
        node_id = to_global_id("OrganizationClasspassNode", classpass.pk)

        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single classpasses and check
        executed = execute_test_client_api_query(self.classpass_query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['organizationClasspass']['archived'], classpass.archived)
        self.assertEqual(data['organizationClasspass']['displayPublic'], classpass.display_public)
        self.assertEqual(data['organizationClasspass']['displayShop'], classpass.display_shop)
        self.assertEqual(data['organizationClasspass']['name'], classpass.name)
        self.assertEqual(data['organizationClasspass']['description'], classpass.description)
        self.assertEqual(data['organizationClasspass']['price'], format(classpass.price, ".2f"))
        self.assertEqual(data['organizationClasspass']['priceDisplay'], display_float_as_amount(classpass.price))
        self.assertEqual(data['organizationClasspass']['financeTaxRate']['id'], 
          to_global_id("FinanceTaxRateNode", classpass.finance_tax_rate.pk))
        self.assertEqual(data['organizationClasspass']['validityUnit'], classpass.validity_unit)
        self.assertEqual(data['organizationClasspass']['validityUnitDisplay'],
                         display_validity_unit(classpass.validity_unit, classpass.validity))
        self.assertEqual(data['organizationClasspass']['classes'], classpass.classes)
        self.assertEqual(data['organizationClasspass']['unlimited'], classpass.unlimited)
        self.assertEqual(data['organizationClasspass']['quickStatsAmount'], format(classpass.quick_stats_amount, ".2f"))
        self.assertEqual(data['organizationClasspass']['financeGlaccount']['id'], 
          to_global_id("FinanceGLAccountNode", classpass.finance_glaccount.pk))
        self.assertEqual(data['organizationClasspass']['financeCostcenter']['id'], 
          to_global_id("FinanceCostCenterNode", classpass.finance_costcenter.pk))
        

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one classpass """   
        classpass = f.OrganizationClasspassFactory.create()

        # Get node id
        node_id = to_global_id("OrganizationClasspassNode", classpass.pk)
        
        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single classpasses and check
        executed = execute_test_client_api_query(self.classpass_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        classpass = f.OrganizationClasspassFactory.create()

        # Get node id
        node_id = to_global_id("OrganizationClasspassNode", classpass.pk)
        
        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single classpasses and check
        executed = execute_test_client_api_query(self.classpass_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_organizationclasspass')
        user.user_permissions.add(permission)
        user.save()
        classpass = f.OrganizationClasspassFactory.create()

        # Get node id
        node_id = to_global_id("OrganizationClasspassNode", classpass.pk)
        
        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single location and check   
        executed = execute_test_client_api_query(self.classpass_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['organizationClasspass']['name'], classpass.name)

    def test_create_classpasses(self):
        """ Create a classpasses """
        query = self.classpass_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['displayPublic'],
                         variables['input']['displayPublic'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['displayShop'],
                         variables['input']['displayShop'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['archived'], False)
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['name'],
                         variables['input']['name'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['description'],
                         variables['input']['description'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['price'],
                         variables['input']['price'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['financeTaxRate']['id'],
                         variables['input']['financeTaxRate'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['validity'],
                         variables['input']['validity'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['validityUnit'],
                         variables['input']['validityUnit'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['classes'],
                         variables['input']['classes'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['unlimited'],
                         variables['input']['unlimited'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['quickStatsAmount'],
                         variables['input']['quickStatsAmount'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['financeGlaccount']['id'],
                         variables['input']['financeGlaccount'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['financeCostcenter']['id'],
                         variables['input']['financeCostcenter'])

    def test_create_classpasses_trial(self):
        """ Create a classpasses """
        query = self.classpass_create_mutation
        variables = self.variables_create_trial

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        # Only test the trial specific fields, the other fields are tested in the regular create test
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['trialPass'],
                         variables['input']['trialPass'])

    def test_create_classpasses_anon_user(self):
        """ Don't allow creating classpasses for non-logged in users """
        query = self.classpass_create_mutation
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
        """ Allow creating class passes for users with permissions """
        query = self.classpass_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        # Tax rate, costcenter & glaccount
        permission = Permission.objects.get(codename=self.permission_view_finance_taxrate)
        user.user_permissions.add(permission)
        permission = Permission.objects.get(codename=self.permission_view_finance_glaccount)
        user.user_permissions.add(permission)
        permission = Permission.objects.get(codename=self.permission_view_finance_costcenter)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['displayShop'], variables['input']['displayShop'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['archived'], False)
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['name'], variables['input']['name'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['description'], variables['input']['description'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['price'], variables['input']['price'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['financeTaxRate']['id'], variables['input']['financeTaxRate'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['validity'], variables['input']['validity'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['validityUnit'], variables['input']['validityUnit'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['classes'], variables['input']['classes'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['unlimited'], variables['input']['unlimited'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['quickStatsAmount'], variables['input']['quickStatsAmount'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
        self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['financeCostcenter']['id'], variables['input']['financeCostcenter'])

    def test_create_classpasses_permission_denied(self):
        """ Check create classpasses permission denied error message """
        query = self.classpass_create_mutation
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

    def test_update_classpasses(self):
        """ Update a classpasses """
        query = self.classpass_update_mutation
        classpass = f.OrganizationClasspassFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['displayPublic'],
                         variables['input']['displayPublic'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['displayShop'],
                         variables['input']['displayShop'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['trialPass'],
                         variables['input']['trialPass'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['archived'], False)
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['name'],
                         variables['input']['name'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['description'],
                         variables['input']['description'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['price'],
                         variables['input']['price'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['financeTaxRate']['id'],
                         variables['input']['financeTaxRate'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['validity'],
                         variables['input']['validity'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['validityUnit'],
                         variables['input']['validityUnit'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['classes'],
                         variables['input']['classes'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['unlimited'],
                         variables['input']['unlimited'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['quickStatsAmount'],
                         variables['input']['quickStatsAmount'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['financeGlaccount']['id'],
                         variables['input']['financeGlaccount'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['financeCostcenter']['id'],
                         variables['input']['financeCostcenter'])

    def test_update_classpasses_anon_user(self):
        """ Don't allow updating classpasses for non-logged in users """
        query = self.classpass_update_mutation
        classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_classpasses_permission_granted(self):
        """ Allow updating classpasses for users with permissions """
        query = self.classpass_update_mutation
        classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        # Tax rate, costcenter & glaccount
        permission = Permission.objects.get(codename=self.permission_view_finance_taxrate)
        user.user_permissions.add(permission)
        permission = Permission.objects.get(codename=self.permission_view_finance_glaccount)
        user.user_permissions.add(permission)
        permission = Permission.objects.get(codename=self.permission_view_finance_costcenter)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['displayShop'], variables['input']['displayShop'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['archived'], False)
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['name'], variables['input']['name'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['description'], variables['input']['description'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['price'], variables['input']['price'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['financeTaxRate']['id'], variables['input']['financeTaxRate'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['validity'], variables['input']['validity'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['validityUnit'], variables['input']['validityUnit'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['classes'], variables['input']['classes'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['unlimited'], variables['input']['unlimited'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['quickStatsAmount'], variables['input']['quickStatsAmount'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
        self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['financeCostcenter']['id'], variables['input']['financeCostcenter'])


    def test_update_classpasses_permission_denied(self):
        """ Check update classpasses permission denied error message """
        query = self.classpass_update_mutation
        classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

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


    def test_archive_classpasses(self):
        """ Archive a classpasses """
        query = self.classpass_archive_mutation
        classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['archiveOrganizationClasspass']['organizationClasspass']['archived'], variables['input']['archived'])


    def test_archive_classpasses_anon_user(self):
        """ Archive classpasses denied for anon user """
        query = self.classpass_archive_mutation
        classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_classpasses_permission_granted(self):
        """ Allow archiving classpasses for users with permissions """
        query = self.classpass_archive_mutation
        classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

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
        self.assertEqual(data['archiveOrganizationClasspass']['organizationClasspass']['archived'], variables['input']['archived'])


    def test_archive_classpasses_permission_denied(self):
        """ Check archive classpasses permission denied error message """
        query = self.classpass_archive_mutation
        classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)
        
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

