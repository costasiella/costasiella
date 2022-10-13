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


class GQLFinanceTaxRate(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financetaxrate'
        self.permission_add = 'add_financetaxrate'
        self.permission_change = 'change_financetaxrate'
        self.permission_delete = 'delete_financetaxrate'

        self.variables_create = {
            "input": {
                "name": "BTW 21%",
                "percentage": "21",
                "rateType": "IN",
                "code": "8000"
            }
        }

        self.variables_update = {
            "input": {
                "name": "BTW 9%",
                "percentage": "9",
                "rateType": "IN",
                "code": "9000"
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.taxrates_query = '''
  query FinanceTaxRates($after: String, $before: String, $archived: Boolean) {
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
          code
        }
      }
    }
  }
'''

        self.taxrate_query = '''
  query FinanceTaxRate($id: ID!) {
    financeTaxRate(id:$id) {
      id
      archived
      name
      percentage
      rateType
      code
    }
  }
'''

        self.taxrate_create_mutation = ''' 
  mutation CreateFinanceTaxRate($input:CreateFinanceTaxRateInput!) {
    createFinanceTaxRate(input: $input) {
      financeTaxRate{
        id
        archived
        name
        percentage
        rateType
        code
      }
    }
  }
'''

        self.taxrate_update_mutation = '''
  mutation UpdateFinanceTaxRate($input: UpdateFinanceTaxRateInput!) {
    updateFinanceTaxRate(input: $input) {
      financeTaxRate {
        id
        archived
        name
        percentage
        rateType
        code
      }
    }
  }
'''

        self.taxrate_archive_mutation = '''
  mutation ArchiveFinanceTaxRate($input: ArchiveFinanceTaxRateInput!) {
    archiveFinanceTaxRate(input: $input) {
      financeTaxRate {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def get_node_id_of_first_taxrate(self):
        # query taxrates to get node id easily
        variables = {
            'archived': False
        }
        executed = execute_test_client_api_query(self.taxrates_query, self.admin_user, variables=variables)
        data = executed.get('data')
        
        return data['financeTaxRates']['edges'][0]['node']['id']

    def test_query(self):
        """ Query list of taxrates """
        query = self.taxrates_query
        taxrate = f.FinanceTaxRateFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['financeTaxRates']['edges'][0]['node']['name'], taxrate.name)
        self.assertEqual(data['financeTaxRates']['edges'][0]['node']['archived'], taxrate.archived)
        self.assertEqual(data['financeTaxRates']['edges'][0]['node']['percentage'],
                         format(taxrate.percentage, ".2f"))
        self.assertEqual(data['financeTaxRates']['edges'][0]['node']['rateType'], taxrate.rate_type)
        self.assertEqual(data['financeTaxRates']['edges'][0]['node']['code'], taxrate.code)

    def test_query_permission_denied(self):
        """ Query list of taxrates - check permission denied """
        query = self.taxrates_query
        taxrate = f.FinanceTaxRateFactory.create()
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permission_granted(self):
        """ Query list of taxrates with view permission """
        query = self.taxrates_query
        taxrate = f.FinanceTaxRateFactory.create()
        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financetaxrate')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all taxrates
        self.assertEqual(data['financeTaxRates']['edges'][0]['node']['name'], taxrate.name)
        self.assertEqual(data['financeTaxRates']['edges'][0]['node']['archived'], taxrate.archived)
        self.assertEqual(data['financeTaxRates']['edges'][0]['node']['percentage'],
                         format(taxrate.percentage, ".2f"))
        self.assertEqual(data['financeTaxRates']['edges'][0]['node']['rateType'], taxrate.rate_type)
        self.assertEqual(data['financeTaxRates']['edges'][0]['node']['code'], taxrate.code)

    def test_query_anon_user(self):
        """ Query list of taxrates - anon user """
        query = self.taxrates_query
        taxrate = f.FinanceTaxRateFactory.create()
        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one taxrate as admin """   
        taxrate = f.FinanceTaxRateFactory.create()

        # First query taxrates to get node id easily
        node_id = self.get_node_id_of_first_taxrate()

        # Now query single taxrate and check
        executed = execute_test_client_api_query(self.taxrate_query, self.admin_user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financeTaxRate']['name'], taxrate.name)
        self.assertEqual(data['financeTaxRate']['archived'], taxrate.archived)
        self.assertEqual(data['financeTaxRate']['percentage'], format(taxrate.percentage, ".2f"))
        self.assertEqual(data['financeTaxRate']['rateType'], taxrate.rate_type)
        self.assertEqual(data['financeTaxRate']['code'], taxrate.code)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one glacount """   
        taxrate = f.FinanceTaxRateFactory.create()

        # First query taxrates to get node id easily
        node_id = self.get_node_id_of_first_taxrate()

        # Now query single taxrate and check
        executed = execute_test_client_api_query(self.taxrate_query, self.anon_user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        user = f.RegularUserFactory.create()
        taxrate = f.FinanceTaxRateFactory.create()

        # First query taxrates to get node id easily
        node_id = self.get_node_id_of_first_taxrate()

        # Now query single taxrate and check
        executed = execute_test_client_api_query(self.taxrate_query, user, variables={"id": node_id})
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_financetaxrate')
        user.user_permissions.add(permission)
        user.save()
        taxrate = f.FinanceTaxRateFactory.create()

        # First query taxrates to get node id easily
        node_id = self.get_node_id_of_first_taxrate()

        # Now query single location and check   
        executed = execute_test_client_api_query(self.taxrate_query, user, variables={"id": node_id})
        data = executed.get('data')
        self.assertEqual(data['financeTaxRate']['name'], taxrate.name)


    def test_create_taxrate(self):
        """ Create a taxrate """
        query = self.taxrate_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['name'], variables['input']['name'])
        self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['archived'], False)
        self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['percentage'], variables['input']['percentage'])
        self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['rateType'], variables['input']['rateType'])
        self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['code'], variables['input']['code'])


    def test_create_taxrate_anon_user(self):
        """ Don't allow creating taxrates for non-logged in users """
        query = self.taxrate_create_mutation
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
        """ Allow creating taxrates for users with permissions """
        query = self.taxrate_create_mutation
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
        self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['name'], variables['input']['name'])
        self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['archived'], False)
        self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['percentage'], variables['input']['percentage'])
        self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['rateType'], variables['input']['rateType'])
        self.assertEqual(data['createFinanceTaxRate']['financeTaxRate']['code'], variables['input']['code'])


    def test_create_taxrate_permission_denied(self):
        """ Check create taxrate permission denied error message """
        query = self.taxrate_create_mutation
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


    def test_update_taxrate(self):
        """ Update a taxrate """
        query = self.taxrate_update_mutation
        taxrate = f.FinanceTaxRateFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_taxrate()

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['name'], variables['input']['name'])
        self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['percentage'], variables['input']['percentage'])
        self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['rateType'], variables['input']['rateType'])
        self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['code'], variables['input']['code'])


    def test_update_taxrate_anon_user(self):
        """ Don't allow updating taxrates for non-logged in users """
        query = self.taxrate_update_mutation
        taxrate = f.FinanceTaxRateFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_taxrate()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_update_taxrate_permission_granted(self):
        """ Allow updating taxrates for users with permissions """
        query = self.taxrate_update_mutation
        taxrate = f.FinanceTaxRateFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_taxrate()

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
        self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['name'], variables['input']['name'])
        self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['percentage'], variables['input']['percentage'])
        self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['rateType'], variables['input']['rateType'])
        self.assertEqual(data['updateFinanceTaxRate']['financeTaxRate']['code'], variables['input']['code'])


    def test_update_taxrate_permission_denied(self):
        """ Check update taxrate permission denied error message """
        query = self.taxrate_update_mutation
        taxrate = f.FinanceTaxRateFactory.create()
        variables = self.variables_update
        variables['input']['id'] = self.get_node_id_of_first_taxrate()

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


    def test_archive_taxrate(self):
        """ Archive a taxrate """
        query = self.taxrate_archive_mutation
        taxrate = f.FinanceTaxRateFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_taxrate()

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['archiveFinanceTaxRate']['financeTaxRate']['archived'], variables['input']['archived'])

    def test_archive_taxrate_anon_user(self):
        """ Archive taxrate denied for anon user """
        query = self.taxrate_archive_mutation
        taxrate = f.FinanceTaxRateFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_taxrate()

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    def test_archive_taxrate_permission_granted(self):
        """ Allow archiving taxrates for users with permissions """
        query = self.taxrate_archive_mutation
        taxrate = f.FinanceTaxRateFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_taxrate()

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
        self.assertEqual(data['archiveFinanceTaxRate']['financeTaxRate']['archived'], variables['input']['archived'])


    def test_archive_taxrate_permission_denied(self):
        """ Check archive taxrate permission denied error message """
        query = self.taxrate_archive_mutation
        taxrate = f.FinanceTaxRateFactory.create()
        variables = self.variables_archive
        variables['input']['id'] = self.get_node_id_of_first_taxrate()
        
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

