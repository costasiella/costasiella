# from graphql.error.located_error import GraphQLLocatedError
import graphql
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

# Create your tests here.
from django.contrib.auth.models import AnonymousUser, Permission

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema


class GQLAccountClasspass(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['finance_invoice_group.json', 'finance_invoice_group_defaults.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountclasspass'
        self.permission_add = 'add_accountclasspass'
        self.permission_change = 'change_accountclasspass'
        self.permission_delete = 'delete_accountclasspass'

        self.variables_create = {
            "input": {
                "dateStart": "2019-01-01",
                "note": "creation note",
            }
        }

        self.variables_update = {
            "input": {
                "dateStart": "2017-01-01",
                "dateEnd": "2020-12-31",
                "note": "Update note",
            }
        }

        self.classpasses_query = '''
  query AccountClasspasses($after: String, $before: String, $accountId: ID!) {
    accountClasspasses(first: 15, before: $before, after: $after, account: $accountId) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
        hasPreviousPage
      }
      edges {
        node {
          id
          organizationClasspass {
            id
            name
          }
          dateStart
          dateEnd
          note
          classesRemainingDisplay
          isExpired
          createdAt
        }
      }
    }
  }
'''

        self.classpass_query = '''
  query AccountClasspass($id: ID!, $after: String, $before: String, $archived: Boolean!) {
    accountClasspass(id:$id) {
      id
      account {
          id
      }
      organizationClasspass {
        id
        name
      }
      dateStart
      dateEnd
      note
      createdAt
    }
    organizationClasspasses(first: 100, before: $before, after: $after, archived: $archived) {
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
  }
'''

        self.classpass_create_mutation = ''' 
  mutation CreateAccountClasspass($input: CreateAccountClasspassInput!) {
    createAccountClasspass(input: $input) {
      accountClasspass {
        id
        account {
          id
          firstName
          lastName
          email
        }
        organizationClasspass {
          id
          name
        }
        dateStart
        dateEnd
        note
      }
    }
  }
'''

        self.classpass_update_mutation = '''
  mutation UpdateAccountClasspass($input: UpdateAccountClasspassInput!) {
    updateAccountClasspass(input: $input) {
      accountClasspass {
        id
        account {
          id
          firstName
          lastName
          email
        }
        organizationClasspass {
          id
          name
        }
        dateStart
        dateEnd
        note
      }
    }
  }
'''

        self.classpass_delete_mutation = '''
  mutation DeleteAccountClasspass($input: DeleteAccountClasspassInput!) {
    deleteAccountClasspass(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of account classpasses """
        query = self.classpasses_query
        classpass = f.AccountClasspassFactory.create()
        variables = {
            'accountId': to_global_id('AccountClasspassNode', classpass.account.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountClasspasses']['edges'][0]['node']['organizationClasspass']['id'], 
            to_global_id("OrganizationClasspassNode", classpass.organization_classpass.id)
        )
        self.assertEqual(data['accountClasspasses']['edges'][0]['node']['dateStart'], str(classpass.date_start))
        self.assertEqual(data['accountClasspasses']['edges'][0]['node']['dateEnd'], str(classpass.date_end))
        self.assertEqual(data['accountClasspasses']['edges'][0]['node']['note'], classpass.note)
        self.assertEqual(data['accountClasspasses']['edges'][0]['node']['classesRemainingDisplay'],
                         str(classpass.classes_remaining))
        self.assertEqual(data['accountClasspasses']['edges'][0]['node']['isExpired'], True)


    def test_query_unlimited(self):
        """ Classes Remaining display should be Unlimited when oranization pass unlimited = True """
        query = self.classpasses_query
        classpass = f.AccountClasspassFactory.create()
        organization_classpass = classpass.organization_classpass
        organization_classpass.unlimited = True
        organization_classpass.save()

        variables = {
            'accountId': to_global_id('AccountClasspassNode', classpass.account.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountClasspasses']['edges'][0]['node']['organizationClasspass']['id'], 
            to_global_id("OrganizationClasspassNode", classpass.organization_classpass.id)
        )
        self.assertEqual(data['accountClasspasses']['edges'][0]['node']['classesRemainingDisplay'], "Unlimited")

    def test_query_permission_denied(self):
        """ Query list of account classpass - check permission denied
        A user can query the class passes linked to their account, so an error will never be thrown
        But a user shouldn't be able to view orders from other accounts without additional permission
        """
        query = self.classpasses_query
        classpass = f.AccountClasspassFactory.create()
        variables = {
            'accountId': to_global_id('AccountClasspassNode', classpass.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=classpass.account.id)
        other_user = f.InstructorFactory.create()
        executed = execute_test_client_api_query(query, other_user, variables=variables)
        data = executed.get('data')

        for item in data['accountClasspasses']['edges']:
            node = item['node']
            self.assertNotEqual(node['account']['id'], to_global_id("AccountNode", user.id))

    def test_query_permission_granted(self):
        """ Query list of account classpasses with view permission """
        query = self.classpasses_query
        classpass = f.AccountClasspassFactory.create()
        variables = {
            'accountId': to_global_id('AccountClasspassNode', classpass.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=classpass.account.id)
        permission = Permission.objects.get(codename='view_accountclasspass')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        # List all classpasses
        self.assertEqual(
            data['accountClasspasses']['edges'][0]['node']['organizationClasspass']['id'], 
            to_global_id("OrganizationClasspassNode", classpass.organization_classpass.id)
        )

    def test_query_anon_user(self):
        """ Query list of account classpasses - anon user """
        query = self.classpasses_query
        classpass = f.AccountClasspassFactory.create()
        variables = {
            'accountId': to_global_id('AccountClasspassNode', classpass.account.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one account classpass as admin """   
        classpass = f.AccountClasspassFactory.create()
        
        variables = {
            "id": to_global_id("AccountClasspassNode", classpass.id),
            "archived": False,
        }

        # Now query single classpass and check
        executed = execute_test_client_api_query(self.classpass_query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountClasspass']['account']['id'], 
            to_global_id('AccountNode', classpass.account.id)
        )
        self.assertEqual(
            data['accountClasspass']['organizationClasspass']['id'], 
            to_global_id('OrganizationClasspassNode', classpass.organization_classpass.id)
        )
        self.assertEqual(data['accountClasspass']['dateStart'], str(classpass.date_start))
        self.assertEqual(data['accountClasspass']['dateEnd'], str(classpass.date_end))
        self.assertEqual(data['accountClasspass']['note'], classpass.note)

    def test_query_one_anon_user(self):
        """ Deny permission for anon users Query one account classpass """   
        classpass = f.AccountClasspassFactory.create()

        variables = {
            "id": to_global_id("AccountClasspassNode", classpass.id),
            "archived": False,
        }

        # Now query single classpass and check
        executed = execute_test_client_api_query(self.classpass_query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one_permission_denied(self):
        """ Permission denied message when user lacks authorization """   
        # Create regular user
        classpass = f.AccountClasspassFactory.create()
        user = classpass.account

        variables = {
            "id": to_global_id("AccountClasspassNode", classpass.id),
            "archived": False,
        }

        # Now query single classpass and check
        executed = execute_test_client_api_query(self.classpass_query, user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_one_permission_granted(self):
        """ Respond with data when user has permission """   
        classpass = f.AccountClasspassFactory.create()
        user = classpass.account
        permission = Permission.objects.get(codename='view_accountclasspass')
        user.user_permissions.add(permission)
        user.save()

        variables = {
            "id": to_global_id("AccountClasspassNode", classpass.id),
            "archived": False,
        }

        # Now query single classpass and check   
        executed = execute_test_client_api_query(self.classpass_query, user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountClasspass']['organizationClasspass']['id'], 
            to_global_id('OrganizationClasspassNode', classpass.organization_classpass.id)
        )

    def test_create_classpass(self):
        """ Create an account classpass """
        query = self.classpass_create_mutation

        account = f.RegularUserFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_classpass.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountClasspass']['accountClasspass']['account']['id'], 
            variables['input']['account']
        )
        self.assertEqual(
            data['createAccountClasspass']['accountClasspass']['organizationClasspass']['id'], 
            variables['input']['organizationClasspass']
        )
        self.assertEqual(data['createAccountClasspass']['accountClasspass']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['createAccountClasspass']['accountClasspass']['note'], variables['input']['note'])

        account_classpass = models.AccountClasspass.objects.all().first()
        finance_invoice = models.FinanceInvoice.objects.all().first()
        self.assertEqual(finance_invoice.summary, "Class pass %s" % account_classpass.id)

        first_invoice_item = finance_invoice.items.all().first()
        self.assertEqual(first_invoice_item.product_name, "Class pass")
        self.assertEqual(first_invoice_item.description,
                         'Class pass %s\n%s' % (str(account_classpass.pk), organization_classpass.name))
        self.assertEqual(int(first_invoice_item.quantity), 1)
        self.assertEqual(first_invoice_item.total, organization_classpass.price)
        self.assertEqual(first_invoice_item.account_classpass, account_classpass)
        self.assertEqual(first_invoice_item.finance_tax_rate, organization_classpass.finance_tax_rate)
        self.assertEqual(first_invoice_item.finance_glaccount, organization_classpass.finance_glaccount)
        self.assertEqual(first_invoice_item.finance_costcenter, organization_classpass.finance_costcenter)

    def test_create_classpass_valid_3_days(self):
        """ End date should be set 3 days from start """
        query = self.classpass_create_mutation

        account = f.RegularUserFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create()
        organization_classpass.validity_unit = 'DAYS'
        organization_classpass.validity = 3
        organization_classpass.save()

        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_classpass.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountClasspass']['accountClasspass']['dateEnd'], 
            str(datetime.date(2019, 1, 1) + datetime.timedelta(days=2))
        )

    def test_create_classpass_valid_2_weeks(self):
        """ End date should be set 2 weeks from start """
        query = self.classpass_create_mutation

        account = f.RegularUserFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create()
        organization_classpass.validity_unit = 'WEEKS'
        organization_classpass.validity = 2
        organization_classpass.save()

        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_classpass.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountClasspass']['accountClasspass']['dateEnd'], 
            str(datetime.date(2019, 1, 1) + datetime.timedelta(days=13))
        )

    def test_create_classpass_valid_2_months(self):
        """ End date should be set 2 weeks from start """
        query = self.classpass_create_mutation

        account = f.RegularUserFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create()
        organization_classpass.validity_unit = 'MONTHS'
        organization_classpass.validity = 2
        organization_classpass.save()

        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_classpass.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
            data['createAccountClasspass']['accountClasspass']['dateEnd'], 
            str(datetime.date(2019, 2, 28))
        )

    def test_create_classpass_anon_user(self):
        """ Don't allow creating account classpasses for non-logged in users """
        query = self.classpass_create_mutation
        
        account = f.RegularUserFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_classpass.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_create_classpass_permission_granted(self):
        """ Allow creating classpasses for users with permissions """
        query = self.classpass_create_mutation

        account = f.RegularUserFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_classpass.id)

        # Create regular user
        user = account
        permission = Permission.objects.get(codename=self.permission_add)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(
            data['createAccountClasspass']['accountClasspass']['organizationClasspass']['id'], 
            variables['input']['organizationClasspass']
        )

    def test_create_classpass_permission_denied(self):
        """ Check create classpass permission denied error message """
        query = self.classpass_create_mutation
        account = f.RegularUserFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_create
        variables['input']['account'] = to_global_id('AccountNode', account.id)
        variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_classpass.id)

        # Create regular user
        user = account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_update_classpass(self):
        """ Update a classpass """
        query = self.classpass_update_mutation
        classpass = f.AccountClasspassFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountClasspassNode', classpass.id)
        variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_classpass.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')

        self.assertEqual(
          data['updateAccountClasspass']['accountClasspass']['organizationClasspass']['id'], 
          variables['input']['organizationClasspass']
        )
        self.assertEqual(data['updateAccountClasspass']['accountClasspass']['dateStart'], variables['input']['dateStart'])
        self.assertEqual(data['updateAccountClasspass']['accountClasspass']['dateEnd'], variables['input']['dateEnd'])
        self.assertEqual(data['updateAccountClasspass']['accountClasspass']['note'], variables['input']['note'])

    def test_update_classpass_anon_user(self):
        """ Don't allow updating classpasses for non-logged in users """
        query = self.classpass_update_mutation
        classpass = f.AccountClasspassFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountClasspassNode', classpass.id)
        variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_classpass.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_update_classpass_permission_granted(self):
        """ Allow updating classpasses for users with permissions """
        query = self.classpass_update_mutation
        classpass = f.AccountClasspassFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountClasspassNode', classpass.id)
        variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_classpass.id)

        user = classpass.account
        permission = Permission.objects.get(codename=self.permission_change)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['updateAccountClasspass']['accountClasspass']['dateStart'], variables['input']['dateStart'])

    def test_update_classpass_permission_denied(self):
        """ Check update classpass permission denied error message """
        query = self.classpass_update_mutation
        classpass = f.AccountClasspassFactory.create()
        organization_classpass = f.OrganizationClasspassFactory.create()
        variables = self.variables_update
        variables['input']['id'] = to_global_id('AccountClasspassNode', classpass.id)
        variables['input']['organizationClasspass'] = to_global_id('OrganizationClasspassNode', organization_classpass.id)

        user = classpass.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_delete_classpass(self):
        """ Delete an account classpass """
        query = self.classpass_delete_mutation
        classpass = f.AccountClasspassFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('AccountClasspassNode', classpass.id)

        executed = execute_test_client_api_query(
            query, 
            self.admin_user, 
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountClasspass']['ok'], True)

    def test_delete_classpass_anon_user(self):
        """ Delete classpass denied for anon user """
        query = self.classpass_delete_mutation
        classpass = f.AccountClasspassFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('AccountClasspassNode', classpass.id)

        executed = execute_test_client_api_query(
            query, 
            self.anon_user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_delete_classpass_permission_granted(self):
        """ Allow deleting classpasses for users with permissions """
        query = self.classpass_delete_mutation
        classpass = f.AccountClasspassFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('AccountClasspassNode', classpass.id)

        # Give permissions
        user = classpass.account
        permission = Permission.objects.get(codename=self.permission_delete)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(
            query, 
            user,
            variables=variables
        )
        data = executed.get('data')
        self.assertEqual(data['deleteAccountClasspass']['ok'], True)

    def test_delete_classpass_permission_denied(self):
        """ Check delete classpass permission denied error message """
        query = self.classpass_delete_mutation
        classpass = f.AccountClasspassFactory.create()
        variables = {"input":{}}
        variables['input']['id'] = to_global_id('AccountClasspassNode', classpass.id)
        
        user = classpass.account

        executed = execute_test_client_api_query(
            query, 
            user, 
            variables=variables
        )
        data = executed.get('data')
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Permission denied!')
