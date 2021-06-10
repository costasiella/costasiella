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



class GQLAccountAcceptedDocument(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    fixtures = ['finance_invoice_group.json', 'finance_invoice_group_defaults.json']

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.permission_view = 'view_accountaccepteddocument'
        self.permission_add = 'add_accountaccepteddocument'
        self.permission_change = 'change_accountaccepteddocument'
        self.permission_delete = 'delete_accountaccepteddocument'


        self.accepted_documents = '''
  query AccountAcceptedDocuments($after: String, $before: String, $account: ID!) {
    accountAcceptedDocuments(first: 15, before:$before, after:$after, account: $account) {
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
      edges {
        node {
          id
          account {
            id
          }
          document {
            id
            documentType
            version
            urlDocument
          }
          dateAccepted
          clientIp
        }
      }
    }
  }
'''


    def tearDown(self):
        # This is run after every test
        pass


    def test_query(self):
        """ Query list of account accepted_documents """
        query = self.accepted_documents
        accepted_document = f.AccountAcceptedDocumentFactory.create()
        variables = {
            "account": to_global_id("AccountNode", accepted_document.account.id)
        }

        executed = execute_test_client_api_query(query, self.admin_user, variables=variables)
        data = executed.get('data')
        self.assertEqual(
            data['accountAcceptedDocuments']['edges'][0]['node']['account']['id'], 
            variables['account']
        )
        self.assertEqual(
            data['accountAcceptedDocuments']['edges'][0]['node']['document']['id'], 
            to_global_id('OrganizationDocumentNode', accepted_document.document.id)
        )
        self.assertEqual(data['accountAcceptedDocuments']['edges'][0]['node']['dateAccepted'], str(accepted_document.date_accepted).replace(' ', 'T'))


    def test_query_permission_denied(self):
        """ Query list of account accepted_documents - check permission denied """
        query = self.accepted_documents
        accepted_document = f.AccountAcceptedDocumentFactory.create()
        variables = {
            "account": to_global_id("AccountNode", accepted_document.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=accepted_document.account.id)
        executed = execute_test_client_api_query(query, user, variables=variables)
        errors = executed.get('errors')

        self.assertEqual(errors[0]['message'], 'Permission denied!')


    def test_query_permission_granted(self):
        """ Query list of account accepted_documents with view permission """
        query = self.accepted_documents
        accepted_document = f.AccountAcceptedDocumentFactory.create()
        variables = {
            "account": to_global_id("AccountNode", accepted_document.account.id)
        }

        # Create regular user
        user = get_user_model().objects.get(pk=accepted_document.account.id)
        permission = Permission.objects.get(codename='view_accountaccepteddocument')
        user.user_permissions.add(permission)
        user.save()

        executed = execute_test_client_api_query(query, user, variables=variables)
        data = executed.get('data')

        self.assertEqual(
            data['accountAcceptedDocuments']['edges'][0]['node']['document']['id'], 
            to_global_id('OrganizationDocumentNode', accepted_document.document.id)
        )


    def test_query_anon_user(self):
        """ Query list of account accepted_documents - anon user """
        query = self.accepted_documents
        accepted_document = f.AccountAcceptedDocumentFactory.create()
        variables = {
            "account": to_global_id("AccountNode", accepted_document.account.id)
        }

        executed = execute_test_client_api_query(query, self.anon_user, variables=variables)
        errors = executed.get('errors')
        self.assertEqual(errors[0]['message'], 'Not logged in!')


    ##
    # These tests are not immediately required, will be added when needed (05-10-2019)
    ##

    # def test_query_one(self):
    #     """ Query one account accepted_document as admin """   
    #     accepted_document = f.AccountClasspassFactory.create()
        
    #     variables = {
    #         "id": to_global_id("AccountClasspassNode", accepted_document.id),
    #         "archived": False,
    #     }

    #     # Now query single accepted_document and check
    #     executed = execute_test_client_api_query(self.accepted_document_query, self.admin_user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['accountClasspass']['account']['id'], 
    #         to_global_id('AccountNode', accepted_document.account.id)
    #     )
    #     self.assertEqual(
    #         data['accountClasspass']['organizationClasspass']['id'], 
    #         to_global_id('OrganizationClasspassNode', accepted_document.organization_accepted_document.id)
    #     )
    #     self.assertEqual(data['accountClasspass']['dateStart'], str(accepted_document.date_start))
    #     self.assertEqual(data['accountClasspass']['dateEnd'], str(accepted_document.date_end))
    #     self.assertEqual(data['accountClasspass']['note'], accepted_document.note)


    # def test_query_one_anon_user(self):
    #     """ Deny permission for anon users Query one account accepted_document """   
    #     accepted_document = f.AccountClasspassFactory.create()

    #     variables = {
    #         "id": to_global_id("AccountClasspassNode", accepted_document.id),
    #         "archived": False,
    #     }

    #     # Now query single accepted_document and check
    #     executed = execute_test_client_api_query(self.accepted_document_query, self.anon_user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Not logged in!')


    # def test_query_one_permission_denied(self):
    #     """ Permission denied message when user lacks authorization """   
    #     # Create regular user
    #     accepted_document = f.AccountClasspassFactory.create()
    #     user = accepted_document.account

    #     variables = {
    #         "id": to_global_id("AccountClasspassNode", accepted_document.id),
    #         "archived": False,
    #     }

    #     # Now query single accepted_document and check
    #     executed = execute_test_client_api_query(self.accepted_document_query, user, variables=variables)
    #     errors = executed.get('errors')
    #     self.assertEqual(errors[0]['message'], 'Permission denied!')


    # def test_query_one_permission_granted(self):
    #     """ Respond with data when user has permission """   
    #     accepted_document = f.AccountClasspassFactory.create()
    #     user = accepted_document.account
    #     permission = Permission.objects.get(codename='view_accountaccepteddocument')
    #     user.user_permissions.add(permission)
    #     user.save()
        

    #     variables = {
    #         "id": to_global_id("AccountClasspassNode", accepted_document.id),
    #         "archived": False,
    #     }

    #     # Now query single accepted_document and check   
    #     executed = execute_test_client_api_query(self.accepted_document_query, user, variables=variables)
    #     data = executed.get('data')
    #     self.assertEqual(
    #         data['accountClasspass']['organizationClasspass']['id'], 
    #         to_global_id('OrganizationClasspassNode', accepted_document.organization_accepted_document.id)
    #     )

