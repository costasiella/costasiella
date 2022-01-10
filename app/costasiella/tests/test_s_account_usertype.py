import graphene
import os
from django.test import TestCase
from graphene.test import Client
from django.contrib.auth.models import AnonymousUser, Permission
from django.contrib.auth import get_user_model

# Create your tests here.
from graphql_relay import to_global_id
from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema
from ..modules.gql_tools import get_rid

from .factories import AdminUserFactory

# Allauth model
from allauth.account.models import EmailAddress


class GQLAccount(TestCase):
    # https://docs.djangoproject.com/en/2.2/topics/testing/overview/

    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

        self.user_type_query = '''
  query User {
    user {
      id
      accountId
      firstName
      lastName
      fullName
      email
      gender
      dateOfBirth
      address
      postcode
      city
      country
      phone
      mobile
      emergency
      instructor
      employee
      hasBankAccountInfo
    }
  }
'''

    def tearDown(self):
        # This is run after every test
        # pass
        # Clean up accounts in costasiella_account table
        get_user_model().objects.all().delete()

    def test_query(self):
        """ Query current user """
        query = self.user_type_query
        account = f.RegularUserFactory()

        executed = execute_test_client_api_query(query, account)
        data = executed.get('data')

        self.assertEqual(data['user']['id'], str(account.id))
        self.assertEqual(data['user']['accountId'], to_global_id('AccountNode', account.id))
        self.assertEqual(data['user']['hasBankAccountInfo'], False)

    def test_query_has_bank_account_info(self):
        """ Query current user """
        query = self.user_type_query
        account_bank_account = f.AccountBankAccountFactory()
        account = account_bank_account.account

        executed = execute_test_client_api_query(query, account)
        data = executed.get('data')

        self.assertEqual(data['user']['id'], str(account.id))
        self.assertEqual(data['user']['accountId'], to_global_id('AccountNode', account.id))
        self.assertEqual(data['user']['hasBankAccountInfo'], True)
