# from graphql.error.located_error import GraphQLLocatedError
import graphql

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from graphene.test import Client

# Create your tests here.
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models
from .. import schema
from ..modules.finance_tools import display_float_as_amount
from ..modules.validity_tools import display_subscription_unit

from graphql_relay import to_global_id


class OrganizationSubscriptionModel(TestCase):
    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        pass

    def tearDown(self):
        # This is run after every test
        pass


    def test_get_price_on_date(self):
        """ Test getting price on date """
        today = timezone.now().date()

        subscription_price = f.OrganizationSubscriptionPriceFactory.create()
        subscription = subscription_price.organization_subscription
        
        self.assertEqual(subscription.organizationsubscriptionprice_set.first().price, subscription.get_price_on_date(today))
        self.assertEqual(
            display_float_as_amount(subscription.organizationsubscriptionprice_set.first().price), 
            subscription.get_price_on_date(today, display=True)
        )