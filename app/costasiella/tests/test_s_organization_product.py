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

        self.organization_product = f.OrganizationProductFactory.create()

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
                  "price": "12",
                  "financeTaxRate": to_global_id("FinanceTaxRateNode", self.organization_product.finance_tax_rate.id),
                  "financeGlaccount": to_global_id("FinanceGLAccountNode",
                                                   self.organization_product.finance_glaccount.id),
                  "financeCostcenter": to_global_id("FinanceCostCenterNode",
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
                    "price": "12",
                    "financeTaxRate": to_global_id("FinanceTaxRateNode", self.organization_product.finance_tax_rate.id),
                    "financeGlaccount": to_global_id("FinanceGLAccountNode",
                                                     self.organization_product.finance_glaccount.id),
                    "financeCostcenter": to_global_id("FinanceCostCenterNode",
                                                      self.organization_product.finance_costcenter.id),
                    "imageFileName": "test_image.jpg",
                    "image": input_image
                }
            }

        self.variables_archive = {
            "input": {
                "id": to_global_id('OrganizationProductNode', self.organization_product.id),
                "archived": False
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
        name
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
        name
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

        self.organization_product_archive_mutation = '''
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

    def test_query_permission_denied(self):
        """ Query list of products as user without permissions """
        query = self.organization_products_query

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of products with view permission """
        query = self.organization_products_query

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query_list)
        data = executed.get('data')

        self.assertEqual(
            data['organizationProducts']['edges'][0]['node']['id'],
            to_global_id('OrganizationProductNode', self.organization_product.id)
        )

    def test_query_anon_user(self):
        """ Query list of products as anon user """
        query = self.organization_products_query

        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_list)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one organization prodict """
        query = self.organization_product_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['organizationProduct']['id'], self.variables_query_one['id'])
        self.assertEqual(data['organizationProduct']['name'], self.organization_product.name)
        self.assertEqual(data['organizationProduct']['description'], self.organization_product.description)
        self.assertEqual(data['organizationProduct']['price'], format(self.organization_product.price, ".2f"))
        self.assertEqual(data['organizationProduct']['financeTaxRate']['id'],
                         to_global_id("FinanceTaxRateNode", self.organization_product.finance_tax_rate.id))
        self.assertEqual(data['organizationProduct']['financeGlaccount']['id'],
                         to_global_id("FinanceGLAccountNode", self.organization_product.finance_glaccount.id))
        self.assertEqual(data['organizationProduct']['financeCostcenter']['id'],
                         to_global_id("FinanceCostCenterNode", self.organization_product.finance_costcenter.id))

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one organization product """
        query = self.organization_product_query
        executed = execute_test_client_api_query(query, self.anon_user, variables=self.variables_query_one)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        query = self.organization_product_query

        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=self.variables_query_one)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        query = self.organization_product_query
        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=self.variables_query_one)
        data = executed.get('data')
        self.assertEqual(data['organizationProduct']['id'], self.variables_query_one['id'])

    def test_create_organization_product(self):
        """ Create organization product """
        query = self.organization_product_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['createOrganizationProduct']['organizationProduct']['name'],
                         variables['input']['name'])
        self.assertEqual(data['createOrganizationProduct']['organizationProduct']['description'],
                         variables['input']['description'])
        self.assertEqual(data['createOrganizationProduct']['organizationProduct']['price'],
                         variables['input']['price'])
        self.assertEqual(data['createOrganizationProduct']['organizationProduct']['financeTaxRate']['id'],
                         variables['input']['financeTaxRate'])
        self.assertEqual(data['createOrganizationProduct']['organizationProduct']['financeGlaccount']['id'],
                         variables['input']['financeGlaccount'])
        self.assertEqual(data['createOrganizationProduct']['organizationProduct']['financeCostcenter']['id'],
                         variables['input']['financeCostcenter'])
        self.assertNotEqual(data['createOrganizationProduct']['organizationProduct']['urlImage'], "")

        organization_product = models.OrganizationProduct.objects.last()
        self.assertNotEqual(organization_product.image, None)

    def test_create_organization_product_anon_user(self):
        """ Don't allow creating organization product for non-logged in users """
        query = self.organization_product_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_organization_product_permission_granted(self):
        """ Allow creating organization product for users with permissions """
        query = self.organization_product_create_mutation

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
        self.assertEqual(data['createOrganizationProduct']['organizationProduct']['name'],
                         variables['input']['name'])

    def test_create_organization_product_permission_denied(self):
        """ Check create organization product permission denied error message """
        query = self.organization_product_create_mutation
        variables = self.variables_create

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_organization_product(self):
        """ Update organization product """
        query = self.organization_product_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['updateOrganizationProduct']['organizationProduct']['name'],
                         variables['input']['name'])
        self.assertEqual(data['updateOrganizationProduct']['organizationProduct']['description'],
                         variables['input']['description'])
        self.assertEqual(data['updateOrganizationProduct']['organizationProduct']['price'],
                         variables['input']['price'])
        self.assertEqual(data['updateOrganizationProduct']['organizationProduct']['financeTaxRate']['id'],
                         variables['input']['financeTaxRate'])
        self.assertEqual(data['updateOrganizationProduct']['organizationProduct']['financeGlaccount']['id'],
                         variables['input']['financeGlaccount'])
        self.assertEqual(data['updateOrganizationProduct']['organizationProduct']['financeCostcenter']['id'],
                         variables['input']['financeCostcenter'])
        self.assertNotEqual(data['updateOrganizationProduct']['organizationProduct']['urlImage'], "")

    def test_update_organization_product_anon_user(self):
        """ Don't allow updating organization product for non-logged in users """
        query = self.organization_product_update_mutation
        variables = self.variables_update

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_organization_product_permission_granted(self):
        """ Allow updating organization product for users with permissions """
        query = self.organization_product_update_mutation
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
        self.assertEqual(data['updateOrganizationProduct']['organizationProduct']['name'],
                         variables['input']['name'])

    def test_update_organization_product_permission_denied(self):
        """ Check update organization product permission denied error message """
        query = self.organization_product_update_mutation
        variables = self.variables_update

        # Create regular user
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_archive_organization_product(self):
        """ Archive an organization product """
        query = self.organization_product_archive_mutation
        variables = self.variables_archive

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['archiveOrganizationProduct']['organizationProduct']['archived'],
                         self.variables_archive['input']['archived'])

    def test_archive_organization_product_anon_user(self):
        """ Archive an organization product """
        query = self.organization_product_archive_mutation
        variables = self.variables_archive

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_organization_product_permission_granted(self):
        """ Allow deleting organization products for users with permissions """
        query = self.organization_product_archive_mutation
        variables = self.variables_archive

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
        self.assertEqual(data['archiveOrganizationProduct']['organizationProduct']['archived'],
                         self.variables_archive['input']['archived'])

    def test_delete_organization_product_permission_denied(self):
        """ Check delete organization product permission denied error message """
        query = self.organization_product_archive_mutation
        variables = self.variables_archive

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(
            query,
            user,
            variables=variables
        )
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
