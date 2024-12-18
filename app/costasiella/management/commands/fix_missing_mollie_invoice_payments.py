from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models import Q
from itertools import chain
from optparse import make_option
import datetime
import logging
import os
import shutil
import sys

import costasiella.models as m
from ...dudes.mollie_dude import MollieDude
from ...views.integration.mollie_webhook import webhook_invoice_paid

from mollie.api.client import Client
from mollie.api.error import Error as MollieError


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def _yes_or_no(self, question, exit_on_no=True):
        """
        A simple yes or no confirmation question
        :param question: String - question text
        :return: input asking a y/n question
        """
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            if exit_on_no:
                self.stdout.write("Missing Mollie invoice payments fix stopped.")
                sys.exit(1)
            else:
                return False
        else:
            return self._yes_or_no("Please enter y or n")

    def handle(self, **options):
        start_fix = self._yes_or_no(
            "\r\nCheck mollie payments for open invoices?"
        )

        if start_fix:
            # Configure mollie client
            mollie = self._get_mollie_client()

            # Get invoices with a mollie payment id, but no payments, after aug 1 2024.
            finance_invoices = m.FinanceInvoice.objects.filter(
                (Q(status="SENT") | Q(status="OVERDUE")),
                Q(date_sent__gte=datetime.date(2024, 9, 1))
            )

            for finance_invoice in finance_invoices:
                logger.debug("Processing invoice %s", finance_invoice.invoice_number)
                # Get mollie payment id from integration log mollie
                integration_log_entry = m.IntegrationLogMollie.objects.filter(finance_invoice=finance_invoice).first()
                if integration_log_entry:
                    mollie_payment_id = integration_log_entry.mollie_payment_id
                    # Check there are no payments already for the invoice
                    mollie_payments_found = \
                        m.FinanceInvoicePayment.objects.filter(online_payment_id=mollie_payment_id).exists()

                    if mollie_payments_found:
                        # Process next item, this one seems ok
                        logger.warning("A Mollie payment %s for invoice %s exists",
                                       mollie_payment_id, finance_invoice.invoice_number)
                        continue

                    # Fetch payment
                    mollie_payment = mollie.payments.get(mollie_payment_id)
                    finance_invoice_id = mollie_payment['metadata'].get("invoice_id", None)

                    # Doublecheck we have the correct payment
                    if finance_invoice.id != finance_invoice_id:
                        logger.warning("A Mollie payment %s, invoice ID mismatch (mollie: %s, costasiella: %s, %s)",
                                       mollie_payment_id,
                                       finance_invoice_id,
                                       finance_invoice.id,
                                       finance_invoice.invoice_number)
                        continue

                    logger.info("Added mollie payment for invoice %s", finance_invoice.invoice_number)

                    if mollie_payment.is_paid():
                        logger.info("Mollie payment %s is paid", mollie_payment_id)
                        payment_amount = float(mollie_payment.amount['value'])
                        payment_date = datetime.datetime.strptime(mollie_payment.paid_at.split('+')[0],
                                                                  '%Y-%m-%dT%H:%M:%S').date()

                        webhook_invoice_paid(finance_invoice_id, payment_amount, payment_date, mollie_payment_id)


    @staticmethod
    def _get_mollie_client():
        mollie_dude = MollieDude()

        # Setup API client
        mollie = Client()
        mollie_api_key = mollie_dude.get_api_key()
        mollie.set_api_key(mollie_api_key)

        return mollie