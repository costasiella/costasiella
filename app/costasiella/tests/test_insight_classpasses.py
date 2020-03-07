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


class GQLInsightClasspasses(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view_active = 'view_insightclasspassesactive'
        self.permission_view_sold = 'view_insightclasspassessold'

        # self.organization_membership = f.OrganizationMembershipFactory.create()

        self.variables_query = {
            'year': 2019
        }   

        self.query_classpasses_active = '''
  query InsightAccountClasspassesActive($year: Int!) {
    insightAccountClasspassesActive(year: $year) {
      description
      data
      year
    }
  }
'''


        self.query_classpasses_sold = '''
  query InsightAccountClasspassesSold($year: Int!) {
    insightAccountClasspassesSold(year: $year) {
      description
      data
      year
    }
  }
'''


    def tearDown(self):
        # This is run after every test
        pass


    def test_query_active(self):
        """ Query list of classpasses """
        query = self.query_classpasses_active
        classpass = f.AccountClasspassFactory.create()

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query)
        data = executed.get('data')

        print(executed)

        self.assertEqual(data['insightAccountClasspassesActive']['description'], 'account_classpasses_active')
        self.assertEqual(data['insightAccountClasspassesActive']['year'], self.variables_query['year'])
        self.assertEqual(data['insightAccountClasspassesActive']['data'][0], 1)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][1], 1)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][2], 1)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][3], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][4], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][5], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][6], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][7], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][8], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][9], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][10], 0)
        self.assertEqual(data['insightAccountClasspassesActive']['data'][11], 0)


    def test_query_permision_denied(self):
        """ Query list of classpasses - check permission denied """
        query = self.query_classpasses_active
        classpass = f.AccountClasspassFactory.create()

        # Create regular user
        user = classpass.account
        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')
        

    def test_query_permision_granted(self):
        """ Query list of classpasses with view permission """
        query = self.query_classpasses_active
        classpass = f.AccountClasspassFactory.create()      

        # Create regular user
        user = classpass.account
        permission = Permission.objects.get(codename='view_insightclasspassesactive')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query)
        data = executed.get('data')

        self.assertEqual(data['insightAccountClasspassesActive']['year'], self.variables_query['year'])


    def test_query_anon_user(self):
        """ Query list of classpasses - anon user """
        query = self.query_classpasses_active
        classpass = f.AccountClasspassFactory.create()  

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one(self):
    #     """ Query one classpasses as admin """   
    #     classpass = f.OrganizationClasspassFactory.create()

    #     # Get node id
    #     node_id = to_global_id("OrganizationClasspassNode", classpass.pk)

    #     variables = {
    #       "id": node_id,
    #       "archived": False
    #     }

    #     # Now query single classpasses and check
    #     executed = execute_test_client_api_query(self.classpass_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(data['organizationClasspass']['archived'], classpass.archived)
    #     self.assertEqual(data['organizationClasspass']['displayPublic'], classpass.display_public)
    #     self.assertEqual(data['organizationClasspass']['displayShop'], classpass.display_shop)
    #     self.assertEqual(data['organizationClasspass']['name'], classpass.name)
    #     self.assertEqual(data['organizationClasspass']['description'], classpass.description)
    #     self.assertEqual(data['organizationClasspass']['price'], classpass.price)
    #     self.assertEqual(data['organizationClasspass']['priceDisplay'], display_float_as_amount(classpass.price))
    #     self.assertEqual(data['organizationClasspass']['financeTaxRate']['id'], 
    #       to_global_id("FinanceTaxRateNode", classpass.finance_tax_rate.pk))
    #     self.assertEqual(data['organizationClasspass']['validityUnit'], classpass.validity_unit)
    #     self.assertEqual(data['organizationClasspass']['validityUnitDisplay'], display_validity_unit(classpass.validity_unit))
    #     self.assertEqual(data['organizationClasspass']['classes'], classpass.classes)
    #     self.assertEqual(data['organizationClasspass']['unlimited'], classpass.unlimited)
    #     self.assertEqual(data['organizationClasspass']['organizationMembership']['id'], 
    #       to_global_id("OrganizationMembershipNode", classpass.organization_membership.pk))
    #     self.assertEqual(data['organizationClasspass']['quickStatsAmount'], classpass.quick_stats_amount)
    #     self.assertEqual(data['organizationClasspass']['financeGlaccount']['id'], 
    #       to_global_id("FinanceGLAccountNode", classpass.finance_glaccount.pk))
    #     self.assertEqual(data['organizationClasspass']['financeCostcenter']['id'], 
    #       to_global_id("FinanceCostCenterNode", classpass.finance_costcenter.pk))
        

    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one classpass """   
    #     classpass = f.OrganizationClasspassFactory.create()

    #     # Get node id
    #     node_id = to_global_id("OrganizationClasspassNode", classpass.pk)
        
    #     variables = {
    #       "id": node_id,
    #       "archived": False
    #     }

    #     # Now query single classpasses and check
    #     executed = execute_test_client_api_query(self.classpass_query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     classpass = f.OrganizationClasspassFactory.create()

    #     # Get node id
    #     node_id = to_global_id("OrganizationClasspassNode", classpass.pk)
        
    #     variables = {
    #       "id": node_id,
    #       "archived": False
    #     }

    #     # Now query single classpasses and check
    #     executed = execute_test_client_api_query(self.classpass_query, user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')

    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_organizationclasspass')
    #     user.user_permissions.add(permission)
    #     user.save()
    #     classpass = f.OrganizationClasspassFactory.create()

    #     # Get node id
    #     node_id = to_global_id("OrganizationClasspassNode", classpass.pk)
        
    #     variables = {
    #       "id": node_id,
    #       "archived": False
    #     }

    #     # Now query single location and check   
    #     executed = execute_test_client_api_query(self.classpass_query, user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(data['organizationClasspass']['name'], classpass.name)

    # def test_create_classpasses(self):
    #     """ Create a classpasses """
    #     query = self.classpass_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['displayPublic'],
    #                      variables['input']['displayPublic'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['displayShop'],
    #                      variables['input']['displayShop'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['archived'], False)
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['name'],
    #                      variables['input']['name'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['description'],
    #                      variables['input']['description'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['price'],
    #                      variables['input']['price'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['financeTaxRate']['id'],
    #                      variables['input']['financeTaxRate'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['validity'],
    #                      variables['input']['validity'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['validityUnit'],
    #                      variables['input']['validityUnit'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['classes'],
    #                      variables['input']['classes'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['unlimited'],
    #                      variables['input']['unlimited'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['organizationMembership']['id'],
    #                      variables['input']['organizationMembership'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['quickStatsAmount'],
    #                      variables['input']['quickStatsAmount'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['financeGlaccount']['id'],
    #                      variables['input']['financeGlaccount'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['financeCostcenter']['id'],
    #                      variables['input']['financeCostcenter'])

    # def test_create_classpasses_trial(self):
    #     """ Create a classpasses """
    #     query = self.classpass_create_mutation
    #     variables = self.variables_create_trial

    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')

    #     # Only test the trial specific fields, the other fields are tested in the regular create test
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['trialPass'],
    #                      variables['input']['trialPass'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['trialTimes'],
    #                      variables['input']['trialTimes'])


    # def test_create_classpasses_anon_user(self):
    #     """ Don't allow creating classpasses for non-logged in users """
    #     query = self.classpass_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')

    # def test_create_location_permission_granted(self):
    #     """ Allow creating class passes for users with permissions """
    #     query = self.classpass_create_mutation
    #     variables = self.variables_create

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['displayPublic'], variables['input']['displayPublic'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['displayShop'], variables['input']['displayShop'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['archived'], False)
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['name'], variables['input']['name'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['description'], variables['input']['description'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['price'], variables['input']['price'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['financeTaxRate']['id'], variables['input']['financeTaxRate'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['validity'], variables['input']['validity'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['validityUnit'], variables['input']['validityUnit'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['classes'], variables['input']['classes'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['unlimited'], variables['input']['unlimited'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['organizationMembership']['id'], variables['input']['organizationMembership'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['quickStatsAmount'], variables['input']['quickStatsAmount'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
    #     self.assertEqual(data['createOrganizationClasspass']['organizationClasspass']['financeCostcenter']['id'], variables['input']['financeCostcenter'])

    # def test_create_classpasses_permission_denied(self):
    #     """ Check create classpasses permission denied error message """
    #     query = self.classpass_create_mutation
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

    # def test_update_classpasses(self):
    #     """ Update a classpasses """
    #     query = self.classpass_update_mutation
    #     classpass = f.OrganizationClasspassFactory.create()

    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')

    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['displayPublic'],
    #                      variables['input']['displayPublic'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['displayShop'],
    #                      variables['input']['displayShop'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['trialPass'],
    #                      variables['input']['trialPass'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['trialTimes'],
    #                      variables['input']['trialTimes'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['archived'], False)
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['name'],
    #                      variables['input']['name'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['description'],
    #                      variables['input']['description'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['price'],
    #                      variables['input']['price'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['financeTaxRate']['id'],
    #                      variables['input']['financeTaxRate'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['validity'],
    #                      variables['input']['validity'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['validityUnit'],
    #                      variables['input']['validityUnit'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['classes'],
    #                      variables['input']['classes'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['unlimited'],
    #                      variables['input']['unlimited'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['organizationMembership']['id'],
    #                      variables['input']['organizationMembership'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['quickStatsAmount'],
    #                      variables['input']['quickStatsAmount'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['financeGlaccount']['id'],
    #                      variables['input']['financeGlaccount'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['financeCostcenter']['id'],
    #                      variables['input']['financeCostcenter'])

    # def test_update_classpasses_anon_user(self):
    #     """ Don't allow updating classpasses for non-logged in users """
    #     query = self.classpass_update_mutation
    #     classpass = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

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
    #     classpass = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

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
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['displayPublic'], variables['input']['displayPublic'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['displayShop'], variables['input']['displayShop'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['archived'], False)
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['description'], variables['input']['description'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['price'], variables['input']['price'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['financeTaxRate']['id'], variables['input']['financeTaxRate'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['validity'], variables['input']['validity'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['validityUnit'], variables['input']['validityUnit'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['classes'], variables['input']['classes'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['unlimited'], variables['input']['unlimited'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['organizationMembership']['id'], variables['input']['organizationMembership'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['quickStatsAmount'], variables['input']['quickStatsAmount'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['financeGlaccount']['id'], variables['input']['financeGlaccount'])
    #     self.assertEqual(data['updateOrganizationClasspass']['organizationClasspass']['financeCostcenter']['id'], variables['input']['financeCostcenter'])


    # def test_update_classpasses_permission_denied(self):
    #     """ Check update classpasses permission denied error message """
    #     query = self.classpass_update_mutation
    #     classpass = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

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
    #     classpass = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     print(data)
    #     self.assertEqual(data['archiveOrganizationClasspass']['organizationClasspass']['archived'], variables['input']['archived'])


    # def test_archive_classpasses_anon_user(self):
    #     """ Archive classpasses denied for anon user """
    #     query = self.classpass_archive_mutation
    #     classpass = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

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
    #     classpass = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)

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
    #     self.assertEqual(data['archiveOrganizationClasspass']['organizationClasspass']['archived'], variables['input']['archived'])


    # def test_archive_classpasses_permission_denied(self):
    #     """ Check archive classpasses permission denied error message """
    #     query = self.classpass_archive_mutation
    #     classpass = f.OrganizationClasspassFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = to_global_id("OrganizationClasspassNode", classpass.pk)
        
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

