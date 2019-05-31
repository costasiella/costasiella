import graphene
from django.test import TestCase
from graphene.test import Client
from django.contrib.auth.models import AnonymousUser

# Create your tests here.
from .factories import AdminUserFactory
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema as cs_schema


# Create schema object
schema = graphene.Schema(
    query=cs_schema.Query,
    mutation=cs_schema.Mutation
)


class GQLAccount(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_account'
        self.permission_add = 'add_account'
        self.permission_change = 'change_account'
        self.permission_delete = 'delete_account'

        self.variables_create = {
            "input": {
                "name": "New costcenter",
                "code" : "8000"
            }
        }

        self.variables_update = {
            "input": {
                "name": "Updated costcenter",
                "code" : "9000"
            }
        }

        self.variables_archive = {
            "input": {
                "archived": True
            }
        }

        self.costcenters_query = '''
  query Accounts($isActive: Boolean!) {
    accounts(isActive: $isActive) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          firstName
          lastName
          email
          isActive
        }
      }
    }
  }
'''

        self.costcenter_query = '''
  query FinanceCostCenter($id: ID!) {
    financeCostcenter(id:$id) {
      id
      name
      code
      archived
    }
  }
'''

#         self.costcenter_create_mutation = ''' 
#   mutation CreateFinanceCostCenter($input:CreateFinanceCostCenterInput!) {
#     createFinanceCostcenter(input: $input) {
#       financeCostcenter{
#         id
#         archived
#         name
#         code
#       }
#     }
#   }
# '''

#         self.costcenter_update_mutation = '''
#   mutation UpdateFinanceCostCenter($input: UpdateFinanceCostCenterInput!) {
#     updateFinanceCostcenter(input: $input) {
#       financeCostcenter {
#         id
#         name
#         code
#       }
#     }
#   }
# '''

#         self.costcenter_archive_mutation = '''
#   mutation ArchiveFinanceCostCenter($input: ArchiveFinanceCostCenterInput!) {
#     archiveFinanceCostcenter(input: $input) {
#       financeCostcenter {
#         id
#         archived
#       }
#     }
#   }
# '''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of costcenters """
        query = self.costcenters_query
        variables = {
            'isActive': True
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['accounts']['edges'][0]['node']['firstName'], self.admin_user.first_name)
        self.assertEqual(data['accounts']['edges'][0]['node']['archived'], self.admin_user.isActive)


    # def test_query_permision_denied(self):
    #     """ Query list of costcenters - check permission denied """
    #     query = self.costcenters_query
    #     costcenter = f.FinanceCostCenterFactory.create()
    #     variables = {
    #         'archived': False
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     errors = executed.get('errors')

    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_permision_granted(self):
    #     """ Query list of costcenters with view permission """
    #     query = self.costcenters_query
    #     costcenter = f.FinanceCostCenterFactory.create()
    #     variables = {
    #         'archived': False
    #     }

    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_account')
    #     user.user_permissions.add(permission)
    #     user.save()

    #     executed = execute_test_client_api_query(query, user, variables=variables)
    #     data = executed.get('data')

    #     # List all costcenters
    #     self.assertEqual(data['financeCostcenters']['edges'][0]['node']['name'], costcenter.name)
    #     self.assertEqual(data['financeCostcenters']['edges'][0]['node']['archived'], costcenter.archived)
    #     self.assertEqual(data['financeCostcenters']['edges'][0]['node']['code'], costcenter.code)


    # def test_query_anon_user(self):
    #     """ Query list of costcenters - anon user """
    #     query = self.costcenters_query
    #     costcenter = f.FinanceCostCenterFactory.create()
    #     variables = {
    #         'archived': False
    #     }

    #     executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one(self):
    #     """ Query one costcenter as admin """   
    #     costcenter = f.FinanceCostCenterFactory.create()

    #     # First query costcenters to get node id easily
    #     node_id = self.get_node_id_of_first_costcenter()

    #     # Now query single costcenter and check
    #     executed = execute_test_client_api_query(self.costcenter_query, self.admin_user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['financeCostcenter']['name'], costcenter.name)
    #     self.assertEqual(data['financeCostcenter']['archived'], costcenter.archived)
    #     self.assertEqual(data['financeCostcenter']['code'], costcenter.code)


    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one glacount """   
    #     costcenter = f.FinanceCostCenterFactory.create()

    #     # First query costcenters to get node id easily
    #     node_id = self.get_node_id_of_first_costcenter()

    #     # Now query single costcenter and check
    #     executed = execute_test_client_api_query(self.costcenter_query, self.anon_user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     costcenter = f.FinanceCostCenterFactory.create()

    #     # First query costcenters to get node id easily
    #     node_id = self.get_node_id_of_first_costcenter()

    #     # Now query single costcenter and check
    #     executed = execute_test_client_api_query(self.costcenter_query, user, variables={"id": node_id})
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename='view_account')
    #     user.user_permissions.add(permission)
    #     user.save()
    #     costcenter = f.FinanceCostCenterFactory.create()

    #     # First query costcenters to get node id easily
    #     node_id = self.get_node_id_of_first_costcenter()

    #     # Now query single location and check   
    #     executed = execute_test_client_api_query(self.costcenter_query, user, variables={"id": node_id})
    #     data = executed.get('data')
    #     self.assertEqual(data['financeCostcenter']['name'], costcenter.name)


    # def test_create_costcenter(self):
    #     """ Create a costcenter """
    #     query = self.costcenter_create_mutation
    #     variables = self.variables_create

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['name'], variables['input']['name'])
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['archived'], False)
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['code'], variables['input']['code'])


    # def test_create_costcenter_anon_user(self):
    #     """ Don't allow creating costcenters for non-logged in users """
    #     query = self.costcenter_create_mutation
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
    #     """ Allow creating costcenters for users with permissions """
    #     query = self.costcenter_create_mutation
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
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['name'], variables['input']['name'])
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['archived'], False)
    #     self.assertEqual(data['createFinanceCostcenter']['financeCostcenter']['code'], variables['input']['code'])


    # def test_create_costcenter_permission_denied(self):
    #     """ Check create costcenter permission denied error message """
    #     query = self.costcenter_create_mutation
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


    # def test_update_costcenter(self):
    #     """ Update a costcenter """
    #     query = self.costcenter_update_mutation
    #     costcenter = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_costcenter()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateFinanceCostcenter']['financeCostcenter']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateFinanceCostcenter']['financeCostcenter']['code'], variables['input']['code'])


    # def test_update_costcenter_anon_user(self):
    #     """ Don't allow updating costcenters for non-logged in users """
    #     query = self.costcenter_update_mutation
    #     costcenter = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_costcenter()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_update_costcenter_permission_granted(self):
    #     """ Allow updating costcenters for users with permissions """
    #     query = self.costcenter_update_mutation
    #     costcenter = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_costcenter()

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
    #     self.assertEqual(data['updateFinanceCostcenter']['financeCostcenter']['name'], variables['input']['name'])
    #     self.assertEqual(data['updateFinanceCostcenter']['financeCostcenter']['code'], variables['input']['code'])


    # def test_update_costcenter_permission_denied(self):
    #     """ Check update costcenter permission denied error message """
    #     query = self.costcenter_update_mutation
    #     costcenter = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_update
    #     variables['input']['id'] = self.get_node_id_of_first_costcenter()

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


    # def test_archive_costcenter(self):
    #     """ Archive a costcenter """
    #     query = self.costcenter_archive_mutation
    #     costcenter = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_costcenter()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.admin_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     print(data)
    #     self.assertEqual(data['archiveFinanceCostcenter']['financeCostcenter']['archived'], variables['input']['archived'])


    # def test_archive_costcenter_anon_user(self):
    #     """ Archive costcenter denied for anon user """
    #     query = self.costcenter_archive_mutation
    #     costcenter = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_costcenter()

    #     executed = execute_test_client_api_query(
    #         query, 
    #         self.anon_user, 
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_archive_costcenter_permission_granted(self):
    #     """ Allow archiving costcenters for users with permissions """
    #     query = self.costcenter_archive_mutation
    #     costcenter = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_costcenter()

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
    #     self.assertEqual(data['archiveFinanceCostcenter']['financeCostcenter']['archived'], variables['input']['archived'])


    # def test_archive_costcenter_permission_denied(self):
    #     """ Check archive costcenter permission denied error message """
    #     query = self.costcenter_archive_mutation
    #     costcenter = f.FinanceCostCenterFactory.create()
    #     variables = self.variables_archive
    #     variables['input']['id'] = self.get_node_id_of_first_costcenter()
        
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

