# This file holds tests for the finance invoice model as it has code to create invoice items
# These invoice items will change depending on values set in the database and should therefore be tested to be sure
# that the correct values are being set for the new invoice items.

# from graphql.error.located_error import GraphQLLocatedError
from django.utils.translation import gettext as _

import graphql
import base64
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client
from graphql_relay import to_global_id
from ..modules.date_tools import last_day_month

# Create your tests here.
from django.db.models import Sum
from django.contrib.auth.models import AnonymousUser, Permission
from django.utils import timezone

from . import factories as f
from .helpers import execute_test_client_api_query
from .. import models


class TestModelFinancePaymentBatch(TestCase):
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

    def test_generate_items_invoices(self):
        """ Test generating batch items for an invoices batch """
        direct_debit = models.FinancePaymentMethod.objects.get(pk=103)
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        account_bank_account = account_bank_account_mandate.account_bank_account
        account = account_bank_account.account
        finance_invoice = f.FinanceInvoiceFactory(account=account)
        finance_invoice.account = account
        finance_invoice.status = 'SENT'
        finance_invoice.finance_payment_method = direct_debit
        finance_invoice.save()
        finance_invoice_item = f.FinanceInvoiceItemFactory.create(finance_invoice=finance_invoice)
        finance_invoice.update_amounts()

        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        finance_payment_batch.generate_items()

        qs = models.FinancePaymentBatchItem.objects.all()
        finance_payment_batch_item = qs.first()

        self.assertEqual(finance_payment_batch_item.finance_payment_batch, finance_payment_batch)
        self.assertEqual(finance_payment_batch_item.account, account)
        self.assertEqual(finance_payment_batch_item.finance_invoice, finance_invoice)
        self.assertEqual(finance_payment_batch_item.account_holder, account_bank_account.holder)
        self.assertEqual(finance_payment_batch_item.account_number, account_bank_account.number)
        self.assertEqual(finance_payment_batch_item.account_bic, account_bank_account.bic)
        self.assertEqual(finance_payment_batch_item.mandate_signature_date, account_bank_account_mandate.signature_date)
        self.assertEqual(finance_payment_batch_item.mandate_reference, account_bank_account_mandate.reference)
        self.assertEqual(finance_payment_batch_item.amount, finance_invoice.total)
        self.assertEqual(finance_payment_batch_item.currency, "EUR")
        self.assertEqual(finance_payment_batch_item.description, finance_invoice.summary)

    def test_generate_items_category(self):
        """ Test generating batch items for an category batch """
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        account_bank_account = account_bank_account_mandate.account_bank_account
        account = account_bank_account.account

        finance_payment_batch = f.FinancePaymentBatchCollectionCategoryFactory.create()
        account_batch_item = f.AccountFinancePaymentBatchCategoryItemFactory.create(
            account=account,
            finance_payment_batch_category = finance_payment_batch.finance_payment_batch_category,
        )

        finance_payment_batch.generate_items()

        qs = models.FinancePaymentBatchItem.objects.all()
        finance_payment_batch_item = qs.first()

        self.assertEqual(finance_payment_batch_item.finance_payment_batch, finance_payment_batch)
        self.assertEqual(finance_payment_batch_item.account, account)
        self.assertEqual(finance_payment_batch_item.account_holder, account_bank_account.holder)
        self.assertEqual(finance_payment_batch_item.account_number, account_bank_account.number)
        self.assertEqual(finance_payment_batch_item.account_bic, account_bank_account.bic)
        self.assertEqual(finance_payment_batch_item.mandate_signature_date, account_bank_account_mandate.signature_date)
        self.assertEqual(finance_payment_batch_item.mandate_reference, account_bank_account_mandate.reference)
        self.assertEqual(finance_payment_batch_item.amount, account_batch_item.amount)
        self.assertEqual(finance_payment_batch_item.currency, "EUR")
        self.assertEqual(finance_payment_batch_item.description, account_batch_item.description)

    def test_add_invoice_payments(self):
        """ Check if invoice payments are added when the add_invoice_payments function is called """
        direct_debit = models.FinancePaymentMethod.objects.get(pk=103)
        account_bank_account_mandate = f.AccountBankAccountMandateFactory.create()
        account_bank_account = account_bank_account_mandate.account_bank_account
        account = account_bank_account.account
        finance_invoice = f.FinanceInvoiceFactory(account=account)
        finance_invoice.account = account
        finance_invoice.status = 'SENT'
        finance_invoice.finance_payment_method = direct_debit
        finance_invoice.save()
        finance_invoice_item = f.FinanceInvoiceItemFactory.create(finance_invoice=finance_invoice)
        finance_invoice.update_amounts()

        finance_payment_batch = f.FinancePaymentBatchCollectionInvoicesFactory.create()
        finance_payment_batch.generate_items()
        finance_payment_batch.add_invoice_payments()

        finance_invoice_payment = finance_invoice.payments.all().first()

        self.assertEqual(finance_invoice_payment.finance_invoice, finance_invoice)
        self.assertEqual(finance_invoice_payment.date, finance_payment_batch.execution_date)
        # Like this we know the value flowed correctly from invoice > batch item > invoice payment
        self.assertEqual(finance_invoice_payment.amount, finance_invoice.total)
        self.assertEqual(finance_invoice_payment.finance_payment_method, direct_debit)
        self.assertEqual(finance_invoice_payment.note, _("Paid in batch: %s") % finance_payment_batch.name)
