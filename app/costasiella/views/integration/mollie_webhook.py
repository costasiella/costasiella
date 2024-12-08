import datetime
import logging

from django.utils.translation import gettext as _
from django.utils import timezone
from django.shortcuts import redirect, render
from django.http import Http404, HttpResponse, FileResponse
from django.db.models import Q
from django.template.loader import get_template, render_to_string

from ...models import \
    FinanceInvoice, \
    FinanceInvoicePayment, \
    FinanceOrder, \
    FinancePaymentMethod, \
    IntegrationLogMollie

from ...dudes.mollie_dude import MollieDude

from mollie.api.client import Client
from mollie.api.error import Error as MollieError


logger = logging.getLogger(__name__)


def mollie_webhook(request):
    """
    Webhook called by mollie
    """
    mollie_id = request.POST.get('id', None)
    logger.info("Mollie webhook called with id %s", mollie_id)

    log = IntegrationLogMollie(
        log_source="WEBHOOK",
        mollie_payment_id=mollie_id,
    )
    log.save()

    # try to get payment
    try:
        mollie_dude = MollieDude()
        
        # Setup API client
        mollie = Client()
        mollie_api_key = mollie_dude.get_api_key()
        mollie.set_api_key(mollie_api_key)

        # Fetch payment
        payment_id = mollie_id
        payment = mollie.payments.get(payment_id)

        # Log payment data
        log.payment_data = str(payment)
        log.save()

        # Determine what to do
        finance_invoice_id = payment['metadata'].get("invoice_id", None)
        finance_order_id = payment['metadata'].get("order_id", None)

        if payment.is_paid():
            #
            # At this point you'd probably want to start the process of delivering the
            # product to the customer.
            #
            logger.info("Mollie payment %s is paid", payment_id)
            payment_amount = float(payment.amount['value'])
            payment_date = datetime.datetime.strptime(payment.paid_at.split('+')[0],
                                                      '%Y-%m-%dT%H:%M:%S').date()

            # Process order payment
            if finance_order_id:
                logger.info("Mollie payment %s is for order %s", payment_id, finance_order_id)
                webhook_deliver_order(
                    finance_order_id=finance_order_id,
                    payment_amount=payment_amount,
                    payment_date=payment_date,
                    payment_id=payment_id
                )

            if finance_invoice_id:
                logger.info("Mollie payment %s is for invoice %s", payment_id, finance_invoice_id)
                webhook_invoice_paid(
                    finance_invoice_id=finance_invoice_id,
                    payment_amount=payment_amount,
                    payment_date=payment_date,
                    payment_id=payment_id
                )

            # Process refunds
            if payment.refunds:
                logger.info("Mollie payment %s contains refunds", payment_id)
                webhook_payment_is_paid_process_refunds(
                    finance_invoice_id,
                    finance_order_id,
                    payment
                )

            # Process chargebacks
            if payment.chargebacks:
                logger.info("Mollie payment %s contains chargebacks", payment_id)
                webhook_payment_is_paid_process_chargebacks(
                    finance_invoice_id,
                    finance_order_id,
                    payment
                )

            return HttpResponse('Paid')
        elif payment.is_pending():
            #
            # The payment has started but is not complete yet.
            #
            logger.info("Mollie payment %s is pending", payment_id)
            return HttpResponse('Pending')
        elif payment.is_open():
            #
            # The payment has not started yet. Wait for it.
            #
            logger.info("Mollie payment %s is open", payment_id)
            return HttpResponse('Open')
        else:
            #
            # The payment isn't paid, pending nor open. We can assume it was aborted.
            #
            logger.info("Mollie payment %s is cancelled", payment_id)
            return HttpResponse('Cancelled')
    except MollieError as e:
        logger.error("Mollie payment %s error: %s", payment_id, str(e))
        return HttpResponse('API call failed: {error}'.format(error=e))


def webhook_deliver_order(finance_order_id, payment_amount, payment_date, payment_id):
    """
    Deliver order when payment for an order is received
    :param finance_order_id: models.finance_order.id
    :return:
    """
    finance_order = FinanceOrder.objects.get(id=finance_order_id)
    # Deliver order
    result = finance_order.deliver()
    if result is not None:
        finance_invoice = result['finance_invoice']
        finance_payment_method = FinancePaymentMethod.objects.get(pk=100)  # Mollie

        # Add payment to invoice if an invoice is found
        if finance_invoice:
            finance_invoice_payment = FinanceInvoicePayment(
                finance_invoice=finance_invoice,
                amount=payment_amount,
                date=payment_date,
                finance_payment_method=finance_payment_method,
                online_payment_id=payment_id
            )
            finance_invoice_payment.save()

            # Check if the invoice has been paid in full and whether we should update it's status
            finance_invoice.is_paid()


def webhook_invoice_paid(finance_invoice_id, payment_amount, payment_date, payment_id):
    """
    Process receiving payment for an invoice
    :param finance_invoice_id: finance_invoice.id
    :param payment_amount: amount paid
    :param payment_date: date of payment
    :param payment_id: mollie payment id
    :return:
    """
    finance_invoice = FinanceInvoice.objects.get(id=finance_invoice_id)
    # Check that the payment hasn't been added yet to prevent processing it twice
    qs = FinanceInvoicePayment.objects.filter(
        online_payment_id=payment_id
    )

    if not qs.exists() and finance_invoice:
        finance_payment_method = FinancePaymentMethod.objects.get(pk=100) # Mollie

        finance_invoice_payment = FinanceInvoicePayment(
            finance_invoice=finance_invoice,
            date=payment_date,
            amount=payment_amount,
            finance_payment_method=finance_payment_method,
            note="",
            online_payment_id=payment_id
        )
        finance_invoice_payment.save()

        # Check if the status of the invoice should be changed
        finance_invoice.is_paid()


def webhook_payment_is_paid_process_refunds(finance_invoice_id, finance_order_id, payment):
    """
    :param finance_invoice_id:
    :param finance_order_id:
    :param payment:
    :return:
    """
    finance_invoice = None
    if finance_order_id:
        finance_order = FinanceOrder.objects.get(pk=finance_order_id)
        finance_invoice = finance_order.finance_invoice

    if finance_invoice_id:
        finance_invoice = FinanceInvoice.objects.get(pk=finance_invoice_id)

    refunds = payment.refunds
    if refunds['count']:
        for refund in refunds['_embedded']['refunds']:
            refund_id = refund['id']
            amount = float(refund['settlementAmount']['value'])
            refund_date = datetime.datetime.strptime(refund['createdAt'].split('+')[0],
                                                     '%Y-%m-%dT%H:%M:%S').date()

            description = refund.get('description', "")
            refund_description = "Mollie refund(%s) - %s" % (refund_id, description)

            qs_refund = FinanceInvoicePayment.objects.filter(
                online_refund_id=refund_id
            )

            if not qs_refund.exists() and finance_invoice:
                webhook_invoice_refund(
                    finance_invoice,
                    amount,
                    refund_date,
                    refund['paymentId'],
                    refund['id'],
                    refund_description
                )


def webhook_invoice_refund(finance_invoice,
                           amount,
                           date,
                           payment_id,
                           refund_id,
                           refund_description):
    """
    :param finance_invoice: FinanceInvoice object
    :param amount: amount to be refunded
    :param date: refund date
    :param payment_id: mollie payment id
    :param refund_id: mollie refund id
    :param refund_description: Refund description
    :return: None
    """
    finance_payment_method = FinancePaymentMethod.objects.get(pk=100)  # Mollie

    finance_invoice_payment = FinanceInvoicePayment(
        finance_invoice=finance_invoice,
        date=date,
        amount=amount,
        finance_payment_method=finance_payment_method,
        note=refund_description,
        online_payment_id=payment_id,
        online_refund_id=refund_id
    )

    finance_invoice_payment.save()
    finance_invoice.is_paid()


def webhook_payment_is_paid_process_chargebacks(finance_invoice_id, finance_order_id, payment):
    """
    :param finance_invoice_id:
    :param finance_order_id:
    :param payment:
    :return:
    """
    finance_invoice = None
    if finance_order_id:
        finance_order = FinanceOrder.objects.get(pk=finance_order_id)
        finance_invoice = finance_order.finance_invoice

    if finance_invoice_id:
        finance_invoice = FinanceInvoice.objects.get(pk=finance_invoice_id)

    chargebacks = payment.chargebacks
    if chargebacks['count']:
        for chargeback in chargebacks['_embedded']['chargebacks']:
            chargeback_id = chargeback['id']
            amount = float(chargeback['settlementAmount']['value'])
            chargeback_date = datetime.datetime.strptime(chargeback['createdAt'].split('+')[0],
                                                         '%Y-%m-%dT%H:%M:%S').date()
            try:
                chargeback_description = "Failure reason: %s (Bank reason code: %s)" % (
                    payment['details']['bankReason'],
                    payment['details']['bankReasonCode']
                )
            except AttributeError:
                chargeback_description = ''

            qs_chargeback = FinanceInvoicePayment.objects.filter(
                online_chargeback_id=chargeback_id
            )

            if not qs_chargeback.exists() and finance_invoice:
                # Only process the chargeback if it hasn't been processed already
                webhook_invoice_add_chargeback_payment(
                    finance_invoice,
                    amount,
                    chargeback_date,
                    chargeback['paymentId'],
                    chargeback['id'],
                    chargeback_description
                )


def webhook_invoice_add_chargeback_payment(finance_invoice,
                                           amount,
                                           date,
                                           payment_id,
                                           chargeback_id,
                                           chargeback_description):
    """
    :param finance_invoice: FinanceInvoice object
    :param amount: amount to be refunded
    :param date: refund date
    :param payment_id: mollie payment id
    :param chargeback_id: mollie refund id
    :param chargeback_description: Refund description
    :return: None
    """
    finance_payment_method = FinancePaymentMethod.objects.get(pk=100)  # Mollie

    finance_invoice_payment = FinanceInvoicePayment(
        finance_invoice=finance_invoice,
        date=date,
        amount=amount,
        finance_payment_method=finance_payment_method,
        note=chargeback_description,
        online_payment_id=payment_id,
        online_chargeback_id=chargeback_id
    )

    finance_invoice_payment.save()
    finance_invoice.is_paid()

    #TODO: Notify customer of failed recurring payment
