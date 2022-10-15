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


class GQLBusiness(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_business'
        self.permission_add = 'add_business'
        self.permission_change = 'change_business'
        self.permission_delete = 'delete_business'

        self.business = f.BusinessB2BFactory.create()

        self.variables_create = {
            "input": {
                "b2b": True,
                "name": "New business",
                "address": "Street 1",
                "postcode": "5433BB",
                "city": "U-Town",
                "country": "BE",
                "phone": "1234",
                "phone2": "9876",
                "emailContact": "pietje@puk.nl",
                "emailBilling": "fnance@new_name.nl",
                "registration": "45656",
                "taxRegistration": "fglkj35555",
            }
        }

        self.variables_update = {
            "input": {
                "archived": True,
                "name": "New name",
                "address": "Street 1",
                "postcode": "5433BB",
                "city": "U-Town",
                "country": "BE",
                "phone": "1234",
                "phone2": "9876",
                "emailContact": "pietje@puk.nl",
                "emailBilling": "fnance@new_name.nl",
                "registration": "45656",
                "taxRegistration": "fglkj35555",
            }
        }

        self.variables_delete = {
            "input": {}
        }

        self.businesses_query = '''
  query Businesses($before:String, $after:String, $name:String, $archived: Boolean!) {
    businesses(first:100, before:$before, after:$after, b2b:true, name_Icontains:$name, archived:$archived) {
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
          b2b
          supplier
          vip
          name
          address
          postcode
          city
          country
          phone
          phone2
          emailContact
          emailBilling
          registration
          taxRegistration
          mollieCustomerId
        }
      }
    }
  }
'''

        self.business_query = '''
  query Business($id: ID!) {
    business(id:$id) {
      id
      archived
      vip
      name
      address
      postcode
      city
      country
      phone
      phone2
      emailContact
      emailBilling
      registration
      taxRegistration
      mollieCustomerId
    }
  }
'''

        self.business_create_mutation = ''' 
  mutation CreateBusiness($input:CreateBusinessInput!) {
    createBusiness(input: $input) {
      business {
        id
        archived
        b2b
        supplier
        vip
        name
        address
        postcode
        city
        country
        phone
        phone2
        emailContact
        emailBilling
        registration
        taxRegistration
      }
    }
  }
'''

        self.business_update_mutation = '''
  mutation UpdateBusiness($input:UpdateBusinessInput!) {
    updateBusiness(input: $input) {
      business {
        id
        archived
        b2b
        supplier
        vip
        name
        address
        postcode
        city
        country
        phone
        phone2
        emailContact
        emailBilling
        registration
        taxRegistration
      }
    }
  }
'''

        self.business_delete_mutation = '''
  mutation DeleteBusiness($input: DeleteBusinessInput!) {
    deleteBusiness(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass

    def test_query(self):
        """ Query list of businesses """
        query = self.businesses_query
        business = f.BusinessB2BFactory.create()
        variables = {
            'archived': False
        }      

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')

        self.assertEqual(data['businesses']['edges'][0]['node']['archived'], business.archived)
        self.assertEqual(data['businesses']['edges'][0]['node']['name'], business.name)
        self.assertEqual(data['businesses']['edges'][0]['node']['address'], business.address)
        self.assertEqual(data['businesses']['edges'][0]['node']['city'], business.city)
        self.assertEqual(data['businesses']['edges'][0]['node']['postcode'], business.postcode)
        self.assertEqual(data['businesses']['edges'][0]['node']['phone'], business.phone)
        self.assertEqual(data['businesses']['edges'][0]['node']['emailContact'], business.email_contact)
        self.assertEqual(data['businesses']['edges'][0]['node']['emailBilling'], business.email_billing)
        self.assertEqual(data['businesses']['edges'][0]['node']['registration'], business.registration)
        self.assertEqual(data['businesses']['edges'][0]['node']['taxRegistration'], business.tax_registration)

    def test_query_permission_denied(self):
        """ Query list of businesses - check permission denied """
        query = self.businesses_query
        business = f.BusinessB2BFactory.create()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        executed = execute_test_client_api_query(query, user, variables=variables)

        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of businesses with view permission """
        query = self.businesses_query
        business = f.BusinessB2BFactory.create()

        variables = {
            'archived': False
        }

        # Create regular user
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_business')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # Data should be returned
        self.assertEqual(data['businesses']['edges'][0]['node']['name'], business.name)

    def test_query_anon_user(self):
        """ Query list of businesses - anon user """
        query = self.businesses_query
        business = f.BusinessB2BFactory.create()

        variables = {
            'archived': False
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one business as admin """
        business = f.BusinessB2BFactory.create()

        variables = {
          "id": to_global_id("BusinessNode", business.pk),
        }

        # Now query single business and check
        executed = execute_test_client_api_query(self.business_query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['business']['archived'], business.archived)
        self.assertEqual(data['business']['name'], business.name)
        self.assertEqual(data['business']['address'], business.address)
        self.assertEqual(data['business']['postcode'], business.postcode)
        self.assertEqual(data['business']['city'], business.city)
        self.assertEqual(data['business']['country'], business.country)
        self.assertEqual(data['business']['phone'], business.phone)
        self.assertEqual(data['business']['phone2'], business.phone_2)
        self.assertEqual(data['business']['emailContact'], business.email_contact)
        self.assertEqual(data['business']['emailBilling'], business.email_billing)
        self.assertEqual(data['business']['registration'], business.registration)
        self.assertEqual(data['business']['taxRegistration'], business.tax_registration)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one business """
        business = f.BusinessB2BFactory.create()

        variables = {
          "id": to_global_id("BusinessNode", business.pk),
        }

        # Now query single businesses and check
        executed = execute_test_client_api_query(self.business_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """
        # Create regular user
        user = f.RegularUserFactory.create()
        business = f.BusinessB2BFactory.create()

        variables = {
          "id": to_global_id("BusinessNode", business.pk),
        }

        # Now query single businesses and check
        executed = execute_test_client_api_query(self.business_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename='view_business')
        user.user_permissions.add(permission)
        user.save()
        business = f.BusinessB2BFactory.create()

        variables = {
          "id": to_global_id("BusinessNode", business.pk),
        }

        # Now query single location and check
        executed = execute_test_client_api_query(self.business_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(data['business']['name'], business.name)

    def test_create_businesses(self):
        """ Create a businesses """
        query = self.business_create_mutation
        variables = self.variables_create

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )

        data = executed.get('data')
        self.assertEqual(data['createBusiness']['business']['archived'], False)
        self.assertEqual(data['createBusiness']['business']['b2b'],
                         variables['input']['b2b'])
        self.assertEqual(data['createBusiness']['business']['name'],
                         variables['input']['name'])
        self.assertEqual(data['createBusiness']['business']['address'],
                         variables['input']['address'])
        self.assertEqual(data['createBusiness']['business']['postcode'],
                         variables['input']['postcode'])
        self.assertEqual(data['createBusiness']['business']['city'],
                         variables['input']['city'])
        self.assertEqual(data['createBusiness']['business']['country'],
                         variables['input']['country'])
        self.assertEqual(data['createBusiness']['business']['phone'],
                         variables['input']['phone'])
        self.assertEqual(data['createBusiness']['business']['phone2'],
                         variables['input']['phone2'])
        self.assertEqual(data['createBusiness']['business']['emailContact'],
                         variables['input']['emailContact'])
        self.assertEqual(data['createBusiness']['business']['emailBilling'],
                         variables['input']['emailBilling'])
        self.assertEqual(data['createBusiness']['business']['registration'],
                         variables['input']['registration'])
        self.assertEqual(data['createBusiness']['business']['taxRegistration'],
                         variables['input']['taxRegistration'])

    def test_create_businesses_anon_user(self):
        """ Don't allow creating businesses for non-logged in users """
        query = self.business_create_mutation
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
        """ Allow creating business for users with permissions """
        query = self.business_create_mutation
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
        self.assertEqual(data['createBusiness']['business']['name'],
                         variables['input']['name'])

    def test_create_businesses_permission_denied(self):
        """ Check create businesses permission denied error message """
        query = self.business_create_mutation
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

    def test_update_businesses(self):
        """ Update a businesses """
        query = self.business_update_mutation
        business = f.BusinessB2BFactory.create()

        variables = self.variables_update
        variables['input']['id'] = to_global_id("BusinessNode", business.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(data['updateBusiness']['business']['archived'],
                         variables['input']['archived'])
        self.assertEqual(data['updateBusiness']['business']['b2b'], True)
        self.assertEqual(data['updateBusiness']['business']['name'],
                         variables['input']['name'])
        self.assertEqual(data['updateBusiness']['business']['address'],
                         variables['input']['address'])
        self.assertEqual(data['updateBusiness']['business']['postcode'],
                         variables['input']['postcode'])
        self.assertEqual(data['updateBusiness']['business']['city'],
                         variables['input']['city'])
        self.assertEqual(data['updateBusiness']['business']['country'],
                         variables['input']['country'])
        self.assertEqual(data['updateBusiness']['business']['phone'],
                         variables['input']['phone'])
        self.assertEqual(data['updateBusiness']['business']['phone2'],
                         variables['input']['phone2'])
        self.assertEqual(data['updateBusiness']['business']['emailContact'],
                         variables['input']['emailContact'])
        self.assertEqual(data['updateBusiness']['business']['emailBilling'],
                         variables['input']['emailBilling'])
        self.assertEqual(data['updateBusiness']['business']['registration'],
                         variables['input']['registration'])
        self.assertEqual(data['updateBusiness']['business']['taxRegistration'],
                         variables['input']['taxRegistration'])

    def test_update_businesses_anon_user(self):
        """ Don't allow updating businesses for non-logged in users """
        query = self.business_update_mutation
        business = f.BusinessB2BFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("BusinessNode", business.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_businesses_permission_granted(self):
        """ Allow updating businesses for users with permissions """
        query = self.business_update_mutation
        business = f.BusinessB2BFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("BusinessNode", business.pk)

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
        self.assertEqual(data['updateBusiness']['business']['name'], variables['input']['name'])

    def test_update_businesses_permission_denied(self):
        """ Check update businesses permission denied error message """
        query = self.business_update_mutation
        business = f.BusinessB2BFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id("BusinessNode", business.pk)

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

    def test_delete_businesses(self):
        """ Archive a businesses """
        query = self.business_delete_mutation
        business = f.BusinessB2BFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("BusinessNode", business.pk)

        executed = execute_test_client_api_query(
            query,
            self.admin_user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteBusiness']['ok'], True)
        
    def test_delete_businesses_anon_user(self):
        """ Archive businesses denied for anon user """
        query = self.business_delete_mutation
        business = f.BusinessB2BFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("BusinessNode", business.pk)

        executed = execute_test_client_api_query(
            query,
            self.anon_user,
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_businesses_permission_granted(self):
        """ Allow archiving businesses for users with permissions """
        query = self.business_delete_mutation
        business = f.BusinessB2BFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("BusinessNode", business.pk)

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
        self.assertEqual(data['deleteBusiness']['ok'], True)

    def test_delete_businesses_permission_denied(self):
        """ Check archive businesses permission denied error message """
        query = self.business_delete_mutation
        business = f.BusinessB2BFactory.create()
        variables = self.variables_delete
        variables['input']['id'] = to_global_id("BusinessNode", business.pk)

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
