# from graphql.error.located_error import GraphQLLocatedError
import graphql
import base64

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id

import datetime
from django.contrib.auth.models import AnonymousUser, Permission

from . import factories as f
from .. import models
from .. import schema

from ..tasks.finance.invoices.tasks import finance_invoices_mark_overdue


class TaskAccountSubscriptionInvoices(TestCase):
    fixtures = [
        'app_settings.json',
        'finance_invoice_group.json',
        'finance_invoice_group_defaults.json',
        'finance_payment_methods.json'
    ]

    # https://docs.djangoproject.com/en/2.1/topics/testing/overview/
    def setUp(self):
        # This is run before every test
        self.admin_user = f.AdminUserFactory.create()
        self.anon_user = AnonymousUser()

    def tearDown(self):
        # This is run after every test
        pass

    def test_finance_invoices_mark_as_overdue(self):
        """ Test marking sent invoices with date due < today as overdue """
        finance_invoice_item = f.FinanceInvoiceItemFactory.create()
        finance_invoice = finance_invoice_item.finance_invoice
        finance_invoice.status = 'SENT'
        finance_invoice.date_due = datetime.date(2000, 1, 1)
        finance_invoice.save()

        result = finance_invoices_mark_overdue()

        self.assertEqual("1" in result, True)
