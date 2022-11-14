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


class GQLFinanceExpense(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_financeexpense'
        self.permission_add = 'add_financeexpense'
        self.permission_change = 'change_financeexpense'
        self.permission_delete = 'delete_financeexpense'

        self.finance_expense = f.FinanceExpenseFactory.create()

        self.variables_query_one = {
            "id": to_global_id("FinanceExpenseNode", self.finance_expense.id)
        }

        with open(os.path.join(os.getcwd(), "costasiella", "tests", "files", "test_image.txt"), 'r') as input_file:
            input_image = input_file.read().replace("\n", "")

            self.variables_create = {
                "input": {
                  "date": "2022-01-01",
                  "summary": "test summary",
                  "description": "test description",
                  "amount": 10,
                  "tax": 2.1,
                  "supplier": to_global_id("BusinessNode", self.finance_expense.supplier.id),
                  "financeGlaccount": to_global_id("FinanceGLAccountNode",
                                                   self.finance_expense.finance_glaccount.id),
                  "financeCostcenter": to_global_id("FinanceCostCenterNode",
                                                    self.finance_expense.finance_costcenter.id),
                  "documentFileName": "test_image.jpg",
                  "document": input_image
                }
            }

            self.variables_update = {
                "input": {
                  "id": to_global_id("FinanceExpenseNode", self.finance_expense.id),
                  "date": "2022-01-01",
                  "summary": "test summary",
                  "description": "test description",
                  "amount": 10,
                  "tax": 2.1,
                  "supplier": to_global_id("BusinessNode", self.finance_expense.supplier.id),
                  "financeGlaccount": to_global_id("FinanceGLAccountNode",
                                                   self.finance_expense.finance_glaccount.id),
                  "financeCostcenter": to_global_id("FinanceCostCenterNode",
                                                    self.finance_expense.finance_costcenter.id),
                  "documentFileName": "test_image.jpg",
                  "document": input_image
                }
            }

        self.variables_delete = {
            "input": {
                "id": to_global_id("FinanceExpenseNode", self.finance_expense.id),
            }
        }

        self.finance_expenses_query = '''
  query FinanceExpenses($after: String, $before: String) {
    financeExpenses(first: 15, before: $before, after: $after) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          date
          summary
          description
          amount
          tax
          total
          supplier {
            id
            name
          }
          financeGlaccount {
            id
            name
            code
          }
          financeCostcenter {
            id
            name
            code
          }
          document
        }
      }
    }
  }
'''

        self.finance_expense_query = '''
  query FinanceExpense($id: ID!) {
    financeExpense(id:$id) {
      id
      date
      summary
      description
      amount
      tax
      total
      supplier {
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
      document
    }
 }
'''

        self.finance_expense_create_mutation = ''' 
  mutation CreateFinanceExpense($input: CreateFinanceExpenseInput!) {
    createFinanceExpense(input: $input) {
      financeExpense {
        id
        date
        summary
        description
        amount
        tax
        total
        supplier {
          id
        }
        financeGlaccount {
          id
        }
        financeCostcenter {
          id
        }
        document
      }
    }
  }
'''

        self.finance_expense_update_mutation = '''
  mutation UpdateFinanceExpense($input: UpdateFinanceExpenseInput!) {
    updateFinanceExpense(input: $input) {
      financeExpense {
        id
        date
        summary
        description
        amount
        tax
        total
        supplier {
          id
        }
        financeGlaccount {
          id
        }
        financeCostcenter {
          id
        }
        document
    }
  }
'''

        self.finance_expense_delete_mutation = '''
  mutation DeleteFinanceExpense($input: DeleteFinanceExpenseInput!) {
    deleteFinanceExpense(input: $input) {
      ok
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        clean_media()

    def test_query(self):
        """ Query list of finance expenses """
        query = self.finance_expenses_query

        executed = execute_test_client_api_query(query, self.admin_user)
        data = executed.get('data')

        self.assertEqual(
            data['financeExpenses']['edges'][0]['node']['id'],
            to_global_id('FinanceExpenseNode', self.finance_expense.id)
        )
        self.assertEqual(
            data['financeExpenses']['edges'][0]['node']['date'],
            str(self.finance_expense.date)
        )
        self.assertEqual(
            data['financeExpenses']['edges'][0]['node']['summary'],
            self.finance_expense.summary
        )
        self.assertEqual(
            data['financeExpenses']['edges'][0]['node']['description'],
            self.finance_expense.description
        )
        self.assertEqual(
            data['financeExpenses']['edges'][0]['node']['amount'],
            format(self.finance_expense.amount, ".2f")
        )
        self.assertEqual(
            data['financeExpenses']['edges'][0]['node']['tax'],
            format(self.finance_expense.tax, ".2f")
        )
        self.assertEqual(
            data['financeExpenses']['edges'][0]['node']['total'],
            format(self.finance_expense.total, ".2f")
        )
        self.assertEqual(
            data['financeExpenses']['edges'][0]['node']['supplier']['id'],
            to_global_id("BusinessNode", self.finance_expense.supplier.id)
        )
        self.assertEqual(
            data['financeExpenses']['edges'][0]['node']['financeGlaccount']['id'],
            to_global_id("FinanceGLAccountNode", self.finance_expense.finance_glaccount.id)
        )
        self.assertEqual(
            data['financeExpenses']['edges'][0]['node']['financeCostcenter']['id'],
            to_global_id("FinanceCostCenterNode", self.finance_expense.finance_costcenter.id)
        )
        self.assertNotEqual(
            data['financeExpenses']['edges'][0]['node']['document'],
            None
        )

    def test_query_permission_denied(self):
        """ Query list of finance expenses - check permission denied """
        query = self.finance_expenses_query
        user = f.RegularUserFactory.create()

        executed = execute_test_client_api_query(query, user)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')

    def test_query_permission_granted(self):
        """ Query list of finance expenses - check permission granted """
        query = self.finance_expenses_query
        user = f.RegularUserFactory.create()
        permission = Permission.objects.get(codename=self.permission_view)
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user)
        data = executed.get('data')

        self.assertEqual(
            data['financeExpenses']['edges'][0]['node']['id'],
            to_global_id('FinanceExpenseNode', self.finance_expense.id)
        )

    def test_query_anon_user(self):
        """ Query list of finance expenses - anon user """
        query = self.finance_expenses_query

        executed = execute_test_client_api_query(query, self.anon_user)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')

    def test_query_one(self):
        """ Query one finance expense """
        query = self.finance_expense_query

        executed = execute_test_client_api_query(query, self.admin_user, variables=self.variables_query_one)
        data = executed.get('data')

        self.assertEqual(data['financeExpense']['id'], self.variables_query_one['id'])
        self.assertEqual(data['financeExpense']['date'], str(self.finance_expense.date))
        self.assertEqual(data['financeExpense']['summary'], self.finance_expense.summary)
        self.assertEqual(data['financeExpense']['description'], self.finance_expense.description)
        self.assertEqual(data['financeExpense']['amount'], format(self.finance_expense.amount, ".2f"))
        self.assertEqual(data['financeExpense']['tax'], format(self.finance_expense.tax, ".2f"))
        self.assertEqual(data['financeExpense']['total'], format(self.finance_expense.total, ".2f"))
        self.assertEqual(data['financeExpense']['supplier']['id'],
                         to_global_id("BusinessNode", self.finance_expense.supplier.id))
        self.assertEqual(data['financeExpense']['financeGlaccount']['id'],
                         to_global_id("FinanceGLAccountNode", self.finance_expense.finance_glaccount.id))
        self.assertEqual(data['financeExpense']['financeCostcenter']['id'],
                         to_global_id("FinanceCostCenterNode", self.finance_expense.finance_costcenter.id))
        self.assertNotEqual(data['financeExpense']['document'], None)
    #
    # def test_create_schedule_event_media(self):
    #     """ Create schedule event media """
    #     query = self.schedule_event_media_create_mutation
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
    #     schedule_event_media = models.ScheduleEventMedia.objects.last()
    #     self.assertNotEqual(schedule_event_media.image, None)
    #
    # def test_create_schedule_event_media_anon_user(self):
    #     """ Don't allow creating schedule event media for non-logged in users """
    #     query = self.schedule_event_media_create_mutation
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
    # def test_create_schedule_event_media_permission_granted(self):
    #     """ Allow creating schedule event media for users with permissions """
    #     query = self.schedule_event_media_create_mutation
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
    # def test_create_schedule_event_media_permission_denied(self):
    #     """ Check create schedule event media permission denied error message """
    #     query = self.schedule_event_media_create_mutation
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
    # def test_update_schedule_event_media(self):
    #     """ Update schedule event media """
    #     query = self.schedule_event_media_update_mutation
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
    #     schedule_event_media = models.ScheduleEventMedia.objects.last()
    #     self.assertNotEqual(schedule_event_media.image, None)
    #
    # def test_update_schedule_event_media_anon_user(self):
    #     """ Don't allow updating schedule event media for non-logged in users """
    #     query = self.schedule_event_media_update_mutation
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
    # def test_update_schedule_event_media_permission_granted(self):
    #     """ Allow updating schedule event media for users with permissions """
    #     query = self.schedule_event_media_update_mutation
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
    # def test_update_schedule_event_media_permission_denied(self):
    #     """ Check update schedule event media permission denied error message """
    #     query = self.schedule_event_media_update_mutation
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
    # def test_delete_schedule_event_media(self):
    #     """ Delete a schedule event media """
    #     query = self.schedule_event_media_delete_mutation
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
    # def test_delete_schedule_event_media_anon_user(self):
    #     """ Delete a schedule event media """
    #     query = self.schedule_event_media_delete_mutation
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
    # def test_delete_schedule_event_media_permission_granted(self):
    #     """ Allow deleting schedule event medias for users with permissions """
    #     query = self.schedule_event_media_delete_mutation
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
    # def test_delete_schedule_event_media_permission_denied(self):
    #     """ Check delete schedule event media permission denied error message """
    #     query = self.schedule_event_media_delete_mutation
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
