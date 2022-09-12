# from graphql.error.located_error import GraphQLLocatedError
import os
import shutil
import graphql
import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser

from . import factories as f
from .helpers import clean_media, execute_test_client_api_query
from .. import models
from .. import schema

from app.settings.development import MEDIA_ROOT


class GQLOrganizationProduct(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_organizationproduct'
        self.permission_add = 'add_organizationproduct'
        self.permission_change = 'change_organizationproduct'
        self.permission_delete = 'delete_organizationproduct'

        self.organization_product = f.OrganizationProduct.create()

        self.variables_query_list = {
            "archived": False
        }

        self.variables_query_one = {
            "id": to_global_id("OrganizationProductNode", self.organization_product.id)
        }

        with open(os.path.join(os.getcwd(), "costasiella", "tests", "files", "test_image.txt"), 'r') as input_file:
            input_image = input_file.read().replace("\n", "")

            self.variables_create = {
                "input": {
                  "name": "a new product",
                  "description": "Product description",
                  "price": 12,
                  "financeTaxRate": to_global_id("FinanceTaxRateNode", self.organization_product.finance_tax_rate.id),
                  "financeGlaccount": to_global_id("FinanceGLAccountNode",
                                                   self.organization_product.finance_glaccount.id),
                  "financeCostcenter": to_global_id("FinanceCostcenterNode",
                                                   self.organization_product.finance_costcenter.id),
                  "imageFileName": "test_image.jpg",
                  "image": input_image
                }
            }

            self.variables_update = {
                "input": {
                    "id": to_global_id("OrganizationProductNode", self.organization_product.id),
                    "name": "an updated product",
                    "description": "Update description",
                    "price": 12,
                    "financeTaxRate": to_global_id("FinanceTaxRateNode", self.organization_product.finance_tax_rate.id),
                    "financeGlaccount": to_global_id("FinanceGLAccountNode",
                                                     self.organization_product.finance_glaccount.id),
                    "financeCostcenter": to_global_id("FinanceCostcenterNode",
                                                      self.organization_product.finance_costcenter.id),
                    "imageFileName": "test_image.jpg",
                    "image": input_image
                }
            }

        self.variables_archive = {
            "input": {
                "id": to_global_id('OrganizationProductNode', self.organization_product.id),
            }
        }

        self.organization_products_query = '''
  query OrganizationProducts($before:String, $after:String, $archived: Boolean) {
    organizationProducts(first: 100, before:$before, after:$after, archived: $archived) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          archived
          name
          description
          price
          urlImage
          urlImageThumbnailSmall
          financeTaxRate {
            id
            name
          }
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

        self.organization_product_query = '''
  query OrganizationProduct($id:ID!) {
    organizationProduct(id: $id) {
      id
      name
      description
      price
      urlImage
      urlImageThumbnailSmall
      financeTaxRate {
        id
        name
      }
      financeGlaccount {
        id 
        name
      }
      financeCostcenter {
        id
        name
      }
    }
    financeTaxRates(first: 100, archived: false) {
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
    financeGlaccounts(first: 100, archived: false) {
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
    financeCostcenters(first: 100, archived: false) {
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

        self.organization_product_create_mutation = ''' 
  mutation CreateOrganizationProduct($input:CreateOrganizationProductInput!) {
    createOrganizationProduct(input: $input) {
      organizationProduct {
        id
        description
        price
        urlImage
        urlImageThumbnailSmall
        financeTaxRate {
          id
        }
        financeGlaccount {
          id
        }
        financeCostcenter {
          id
        }
      }
    }
  }
'''

        self.organization_product_update_mutation = '''
  mutation UpdateOrganizationProduct($input:UpdateOrganizationProductInput!) {
    updateOrganizationProduct(input: $input) {
      organizationProduct {
        id
        description
        price
        urlImage
        urlImageThumbnailSmall
        financeTaxRate {
          id
        }
        financeGlaccount {
          id
        }
        financeCostcenter {
          id
        }
      }
    }
  }
'''

        self.organization_product_delete_mutation = '''
  mutation ArchiveOrganizationProduct($input: ArchiveOrganizationProductInput!) {
    archiveOrganizationProduct(input: $input) {
      organizationProduct {
        id
        archived
      }
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        clean_media()

    def test_query(self):
        """ Query list of organization products """
        query = self.organization_products_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['organizationProducts']['edges'][0]['node']['id'],
            to_global_id('OrganizationProductNode', self.organization_product.id)
        )
        self.assertEqual(data['organizationProducts']['edges'][0]['node']['description'],
                         self.organization_product.description)
        self.assertEqual(data['organizationProducts']['edges'][0]['node']['price'],
                         format(self.organization_product.price, ".2f"))
        self.assertEqual(
            data['organizationProducts']['edges'][0]['node']['financeTaxRate']['id'],
            to_global_id('FinanceTaxRateNode', self.organization_product.finance_tax_rate.id)
        )
        self.assertEqual(
            data['organizationProducts']['edges'][0]['node']['financeGlaccount']['id'],
            to_global_id('FinanceGLAccountNode', self.organization_product.finance_glaccount.id)
        )
        self.assertEqual(
            data['organizationProducts']['edges'][0]['node']['financeCostcenter']['id'],
            to_global_id('FinanceCostCenterNode', self.organization_product.finance_costcenter.id)
        )
        self.assertNotEqual(data['organizationProducts']['edges'][0]['node']['urlImage'], False)
        self.assertNotEqual(data['organizationProducts']['edges'][0]['node']['urlImageThumbnailSmall'], False)

    ##
    # No permission tests are required in this test, as there are no permission checks in the schema.
    # The listing of these documents is public, so users also don't need to be logged in.
    ##
    # def test_query_one(self):
    #     """ Query one schedule event media """
    #     query = self.organization_product_query
    # 
    #     executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_one)
    #     data = executed.get('data')
    # 
    #     self.assertEqual(data['scheduleEventMedia']['id'], self.variables_query_one['id'])
    # 
    # def test_create_organization_product(self):
    #     """ Create schedule event media """
    #     query = self.organization_product_create_mutation
    #     variables = self.variables_create
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    # 
    #     self.assertEqual(data['createScheduleEventMedia']['scheduleEventMedia']['sortOrder'],
    #                      variables['input']['sortOrder'])
    #     self.assertEqual(data['createScheduleEventMedia']['scheduleEventMedia']['description'],
    #                      variables['input']['description'])
    #     self.assertNotEqual(data['createScheduleEventMedia']['scheduleEventMedia']['urlImage'], "")
    # 
    #     organization_product = models.ScheduleEventMedia.objects.last()
    #     self.assertNotEqual(organization_product.image, None)
    # 
    # def test_create_organization_product_anon_user(self):
    #     """ Don't allow creating schedule event media for non-logged in users """
    #     query = self.organization_product_create_mutation
    #     variables = self.variables_create
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # def test_create_organization_product_permission_granted(self):
    #     """ Allow creating schedule event media for users with permissions """
    #     query = self.organization_product_create_mutation
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_add)
    #     user.user_permissions.add(permission)
    #     user.save()
    # 
    #     variables = self.variables_create
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['createScheduleEventMedia']['scheduleEventMedia']['sortOrder'],
    #                      variables['input']['sortOrder'])
    # 
    # def test_create_organization_product_permission_denied(self):
    #     """ Check create schedule event media permission denied error message """
    #     query = self.organization_product_create_mutation
    #     variables = self.variables_create
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    # 
    # def test_update_organization_product(self):
    #     """ Update schedule event media """
    #     query = self.organization_product_update_mutation
    #     variables = self.variables_update
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    # 
    #     data = executed.get('data')
    #     self.assertEqual(data['updateScheduleEventMedia']['scheduleEventMedia']['sortOrder'],
    #                      variables['input']['sortOrder'])
    #     self.assertEqual(data['updateScheduleEventMedia']['scheduleEventMedia']['description'],
    #                      variables['input']['description'])
    #     self.assertNotEqual(data['updateScheduleEventMedia']['scheduleEventMedia']['urlImage'], "")
    # 
    #     organization_product = models.ScheduleEventMedia.objects.last()
    #     self.assertNotEqual(organization_product.image, None)
    # 
    # def test_update_organization_product_anon_user(self):
    #     """ Don't allow updating schedule event media for non-logged in users """
    #     query = self.organization_product_update_mutation
    #     variables = self.variables_update
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # def test_update_organization_product_permission_granted(self):
    #     """ Allow updating schedule event media for users with permissions """
    #     query = self.organization_product_update_mutation
    #     variables = self.variables_update
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_change)
    #     user.user_permissions.add(permission)
    #     user.save()
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['updateScheduleEventMedia']['scheduleEventMedia']['sortOrder'],
    #                      variables['input']['sortOrder'])
    # 
    # def test_update_organization_product_permission_denied(self):
    #     """ Check update schedule event media permission denied error message """
    #     query = self.organization_product_update_mutation
    #     variables = self.variables_update
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
    # 
    # def test_delete_organization_product(self):
    #     """ Delete a schedule event media """
    #     query = self.organization_product_delete_mutation
    #     variables = self.variables_delete
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.admin_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    # 
    #     self.assertEqual(data['deleteScheduleEventMedia']['ok'], True)
    # 
    #     exists = models.OrganizationDocument.objects.exists()
    #     self.assertEqual(exists, False)
    # 
    # def test_delete_organization_product_anon_user(self):
    #     """ Delete a schedule event media """
    #     query = self.organization_product_delete_mutation
    #     variables = self.variables_delete
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         self.anon_user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')
    # 
    # def test_delete_organization_product_permission_granted(self):
    #     """ Allow deleting schedule event medias for users with permissions """
    #     query = self.organization_product_delete_mutation
    #     variables = self.variables_delete
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    #     permission = Permission.objects.get(codename=self.permission_delete)
    #     user.user_permissions.add(permission)
    #     user.save()
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     self.assertEqual(data['deleteScheduleEventMedia']['ok'], True)
    # 
    # def test_delete_organization_product_permission_denied(self):
    #     """ Check delete schedule event media permission denied error message """
    #     query = self.organization_product_delete_mutation
    #     variables = self.variables_delete
    # 
    #     # Create regular user
    #     user = f.RegularUserFactory.create()
    # 
    #     executed = execute_test_client_api_query(
    #         query,
    #         user,
    #         variables=variables
    #     )
    #     data = executed.get('data')
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')
