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


class GQLSchoolClasspass(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_schoolclasspass'
        self.permission_add = 'add_schoolclasspass'
        self.permission_change = 'change_schoolclasspass'
        self.permission_delete = 'delete_schoolclasspass'

        self.school_membership = f.SchoolMembershipFactory.create()
        self.finance_tax_rate = f.FinanceTaxRateFactory.create()
        self.finance_glaccount = f.FinanceGLAccountFactory.create()
        self.finance_costcenter = f.FinanceCostCenterFactory.create()

        self.variables_create = {
            "input": {
                "displayPublic": True,
                "displayShop": True,
                "name": "First classpass",
                "description": "Description",
                "price": 125,
                "financeTaxRate": to_global_id("FinanceTaxRateNode", self.finance_tax_rate.pk),
                "validity": 1,
                "validityUnit": "MONTHS",
                "classes": 10,
                "unlimited": False,
                "schoolMembership": to_global_id("SchoolMembershipNode", self.school_membership.pk),
                "quickStatsAmount": 12.5,
                "financeGlaccount": to_global_id("FinanceGLAccountNode", self.finance_glaccount.pk),
                "financeCostcenter": to_global_id("FinanceCostCenterNode", self.finance_costcenter.pk),
            }
        }

        self.variables_update = {
            "input": {
                "displayPublic": True,
                "displayShop": True,
                "name": "Updated classpass",
                "description": "Description",
                "price": 12.50,
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

        self.classpasses_query = '''
  query SchoolClasspasses($after: String, $before: String, $archived: Boolean) {
    schoolClasspasses(first: 15, before: $before, after: $after, archived: $archived) {
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
          classes
          unlimited
          schoolMembership {
            id
            name
          }
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
  query SchoolClasspass($id: ID!, $after: String, $before: String, $archived: Boolean!) {
    schoolClasspass(id:$id) {
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
      classes
      unlimited
      schoolMembership {
        id
        name
      }
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
    schoolMemberships(first: 15, before: $before, after: $after, archived: $archived) {
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
        }
      }
    }
    financeTaxrates(first: 15, before: $before, after: $after, archived: $archived) {
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
  mutation CreateClasspass($input: CreateSchoolClasspassInput!) {
    createSchoolClasspass(input: $input) {
      schoolClasspass {
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
        classes
        unlimited
        schoolMembership {
          id
          name
        }
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
  mutation UpdateSchoolClasspass($input: UpdateSchoolClasspassInput!) {
    updateSchoolClasspass(input: $input) {
        schoolClasspass {
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

        self.classpass_archive_mutation = '''
  mutation ArchiveSchoolClasspass($input: ArchiveSchoolClasspassInput!) {
    archiveSchoolClasspass(input: $input) {
      schoolClasspass {
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
        classpass = f.SchoolClasspassFactory.create()
        variables = {
            'archived': False
        }      

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['archived'], classpass.archived)
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['displayPublic'], classpass.display_public)
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['displayShop'], classpass.display_shop)
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['name'], classpass.name)
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['description'], classpass.description)
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['price'], classpass.price)
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['priceDisplay'], display_float_as_amount(classpass.price))
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['financeTaxRate']['id'], 
          to_global_id("FinanceTaxRateNode", classpass.finance_tax_rate.pk))
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['validityUnit'], classpass.validity_unit)
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['validityUnitDisplay'], display_validity_unit(classpass.validity_unit))
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['classes'], classpass.classes)
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['unlimited'], classpass.unlimited)
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['schoolMembership']['id'], 
          to_global_id("SchoolMembershipNode", classpass.school_membership.pk))
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['quickStatsAmount'], classpass.quick_stats_amount)
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['financeGlaccount']['id'], 
          to_global_id("FinanceGLAccountNode", classpass.finance_glaccount.pk))
        self.assertEqual(data['schoolClasspasses']['edges'][0]['node']['financeCostcenter']['id'], 
          to_global_id("FinanceCostCenterNode", classpass.finance_costcenter.pk))


    def test_query_permision_denied(self):
        """ Query list of classpasses - check permission denied """
        query = self.classpasses_query
        classpass = f.SchoolClasspassFactory.create()
        non_public = f.SchoolClasspassFactory.create()
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
        for item in data['schoolClasspasses']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        self.assertEqual(non_public_found, False)


    def test_query_permision_granted(self):
        """ Query list of classpasses with view permission """
        query = self.classpasses_query
        classpass = f.SchoolClasspassFactory.create()
        non_public = f.SchoolClasspassFactory.create()
        non_public.display_public = False
        non_public.save()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_schoolclasspass')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all class passes, including non public
        non_public_found = False
        for item in data['schoolClasspasses']['edges']:
            if not item['node']['displayPublic']:
                non_public_found = True

        # Assert non public classtypes are listed
        self.assertEqual(non_public_found, True)


    def test_query_anon_user(self):
        """ Query list of classpasses - anon user """
        query = self.classpasses_query
        classpass = f.SchoolClasspassFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_query_one(self):
        """ Query one classpasses as admin """   
        classpass = f.SchoolClasspassFactory.create()

        # Get node id
        node_id = to_global_id("SchoolClasspassNode", classpass.pk)

        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single classpasses and check
        executed = execute_test_client_api_query(self.classpass_query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['schoolClasspass']['archived'], classpass.archived)
        self.assertEqual(data['schoolClasspass']['displayPublic'], classpass.display_public)
        self.assertEqual(data['schoolClasspass']['displayShop'], classpass.display_shop)
        self.assertEqual(data['schoolClasspass']['name'], classpass.name)
        self.assertEqual(data['schoolClasspass']['description'], classpass.description)
        self.assertEqual(data['schoolClasspass']['price'], classpass.price)
        self.assertEqual(data['schoolClasspass']['priceDisplay'], display_float_as_amount(classpass.price))
        self.assertEqual(data['schoolClasspass']['financeTaxRate']['id'], 
          to_global_id("FinanceTaxRateNode", classpass.finance_tax_rate.pk))
        self.assertEqual(data['schoolClasspass']['validityUnit'], classpass.validity_unit)
        self.assertEqual(data['schoolClasspass']['validityUnitDisplay'], display_validity_unit(classpass.validity_unit))
        self.assertEqual(data['schoolClasspass']['classes'], classpass.classes)
        self.assertEqual(data['schoolClasspass']['unlimited'], classpass.unlimited)
        self.assertEqual(data['schoolClasspass']['schoolMembership']['id'], 
          to_global_id("SchoolMembershipNode", classpass.school_membership.pk))
        self.assertEqual(data['schoolClasspass']['quickStatsAmount'], classpass.quick_stats_amount)
        self.assertEqual(data['schoolClasspass']['financeGlaccount']['id'], 
          to_global_id("FinanceGLAccountNode", classpass.finance_glaccount.pk))
        self.assertEqual(data['schoolClasspass']['financeCostcenter']['id'], 
          to_global_id("FinanceCostCenterNode", classpass.finance_costcenter.pk))
        

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one classpass """   
        classpass = f.SchoolClasspassFactory.create()

        # Get node id
        node_id = to_global_id("SchoolClasspassNode", classpass.pk)
        
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
        classpass = f.SchoolClasspassFactory.create()

        # Get node id
        node_id = to_global_id("SchoolClasspassNode", classpass.pk)
        
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
        permission = Permission.objects.get(codename='view_schoolclasspass')
        user.user_permissions.add(permission)
        user.save()
        classpass = f.SchoolClasspassFactory.create()

        # Get node id
        node_id = to_global_id("SchoolClasspassNode", classpass.pk)
        
        variables = {
          "id": node_id,
          "archived": False
        }

        # Now query single location and check   
        executed = execute_test_client_api_query(self.classpass_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['schoolClasspass']['name'], classpass.name)


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
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['displayShop'], variables['input']['displayShop'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['archived'], False)
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['name'], variables['input']['name'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['description'], variables['input']['description'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['price'], variables['input']['price'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['financeTaxRate']['id'], variables['input']['financeTaxRate'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['validity'], variables['input']['validity'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['validityUnit'], variables['input']['validityUnit'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['classes'], variables['input']['classes'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['unlimited'], variables['input']['unlimited'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['schoolMembership']['id'], variables['input']['schoolMembership'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['quickStatsAmount'], variables['input']['quickStatsAmount'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['financeCostcenter']['id'], variables['input']['financeCostcenter'])


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
        """ Allow creating classpasses for users with permissions """
        query = self.classpass_create_mutation
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
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['displayPublic'], variables['input']['displayPublic'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['displayShop'], variables['input']['displayShop'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['archived'], False)
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['name'], variables['input']['name'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['description'], variables['input']['description'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['price'], variables['input']['price'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['financeTaxRate']['id'], variables['input']['financeTaxRate'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['validity'], variables['input']['validity'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['validityUnit'], variables['input']['validityUnit'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['classes'], variables['input']['classes'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['unlimited'], variables['input']['unlimited'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['schoolMembership']['id'], variables['input']['schoolMembership'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['quickStatsAmount'], variables['input']['quickStatsAmount'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
        self.assertEqual(data['createSchoolClasspass']['schoolClasspass']['financeCostcenter']['id'], variables['input']['financeCostcenter'])


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


    # def test_update_classpasses(self):
    #     """ Update a classpasses """
    #     query = self.classpass_update_mutation
    #     classpass = f.SchoolClasspassFactory.create()

    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id("SchoolClasspassNode", classpass.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['displayPublic'], variables['input']['displayPublic'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['displayShop'], variables['input']['displayShop'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['archived'], False)
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['description'], variables['input']['description'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['price'], variables['input']['price'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['financeTaxRate']['id'], variables['input']['financeTaxRate'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['validity'], variables['input']['validity'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['validityUnit'], variables['input']['validityUnit'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['termsAndConditions'], variables['input']['termsAndConditions'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['financeCostcenter']['id'], variables['input']['financeCostcenter'])


    # def test_update_classpasses_anon_user(self):
    #     """ Don't allow updating classpasses for non-logged in users """
    #     query = self.classpass_update_mutation
    #     classpass = f.SchoolClasspassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id("SchoolClasspassNode", classpass.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_classpasses_permission_granted(self):
    #     """ Allow updating classpasses for users with permissions """
    #     query = self.classpass_update_mutation
    #     classpass = f.SchoolClasspassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id("SchoolClasspassNode", classpass.pk)

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
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['displayPublic'], variables['input']['displayPublic'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['displayShop'], variables['input']['displayShop'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['archived'], False)
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['description'], variables['input']['description'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['price'], variables['input']['price'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['financeTaxRate']['id'], variables['input']['financeTaxRate'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['validity'], variables['input']['validity'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['validityUnit'], variables['input']['validityUnit'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['termsAndConditions'], variables['input']['termsAndConditions'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
    #     self.assertEqual(data['updateSchoolClasspass']['schoolClasspass']['financeCostcenter']['id'], variables['input']['financeCostcenter'])


    # def test_update_classpasses_permission_denied(self):
    #     """ Check update classpasses permission denied error message """
    #     query = self.classpass_update_mutation
    #     classpass = f.SchoolClasspassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id("SchoolClasspassNode", classpass.pk)

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


    # def test_archive_classpasses(self):
    #     """ Archive a classpasses """
    #     query = self.classpass_archive_mutation
    #     classpass = f.SchoolClasspassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id("SchoolClasspassNode", classpass.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     print(data)
    #     self.assertEqual(data['archiveSchoolClasspass']['schoolClasspass']['archived'], variables['input']['archived'])


    # def test_archive_classpasses_anon_user(self):
    #     """ Archive classpasses denied for anon user """
    #     query = self.classpass_archive_mutation
    #     classpass = f.SchoolClasspassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id("SchoolClasspassNode", classpass.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_archive_classpasses_permission_granted(self):
    #     """ Allow archiving classpasses for users with permissions """
    #     query = self.classpass_archive_mutation
    #     classpass = f.SchoolClasspassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id("SchoolClasspassNode", classpass.pk)

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
    #     self.assertEqual(data['archiveSchoolClasspass']['schoolClasspass']['archived'], variables['input']['archived'])


    # def test_archive_classpasses_permission_denied(self):
    #     """ Check archive classpasses permission denied error message """
    #     query = self.classpass_archive_mutation
    #     classpass = f.SchoolClasspassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id("SchoolClasspassNode", classpass.pk)
        
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

