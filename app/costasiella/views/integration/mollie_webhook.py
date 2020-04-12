import io

from django.utils.translation import gettext as _
from django.utils import timezone
from django.shortcuts import redirect, render
from django.http import Http404, HttpResponse, FileResponse
from django.db.models import Q
from django.template.loader import get_template, render_to_string


# from django.template.loader import render_to_string
# rendered = render_to_string('my_template.html', {'foo': 'bar'})

from ..models import FinanceInvoice, FinanceOrder, IntegrationLogMollie
from ..modules.gql_tools import require_login_and_permission, get_rid

from ...dudes.mollie_dude import MollieDude


def webhook(request, id):
    """
    Webhook called by mollie
    """
    log = IntegrationLogMollie(
        log_source = "WEBHOOK",
        mollie_payment_id = id,
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
        payment_id = id
        payment = mollie.payments.get(payment_id)

        # Log payment data
        log.payment_data = str(payment)
        log.save()

        # Determine what to do
        finance_invoice_id = payment['metadata']['invoice_id']
        finance_order_id = payment['metadata']['order_id'] 

        if payment.is_paid():
            #
            # At this point you'd probably want to start the process of delivering the
            # product to the customer.
            #
            payment_amount = float(payment.amount['value'])
            payment_date = datetime.datetime.strptime(payment.paid_at.split('+')[0],
                                                      '%Y-%m-%dT%H:%M:%S').date()

            print(payment_date)


            # # Process refunds
            # if payment.refunds:
            #     webook_payment_is_paid_process_refunds(coID, iID, payment.refunds)

            # # Process chargebacks
            # if payment.chargebacks:
            #     webhook_payment_is_paid_process_chargeback(coID, iID, payment)

            # if coID == 'invoice':
            #     # add payment to invoice
            #     webhook_invoice_paid(iID, payment_amount, payment_date, payment_id)
            # else:
            #     # Deliver order
            #     webhook_order_paid(coID, payment_amount, payment_date, payment_id, payment=payment)

            return 'Paid'
        elif payment.is_pending():
            #
            # The payment has started but is not complete yet.
            #
            return 'Pending'
        elif payment.is_open():
            #
            # The payment has not started yet. Wait for it.
            #
            return 'Open'
        else:
            #
            # The payment isn't paid, pending nor open. We can assume it was aborted.
            #
            return 'Cancelled'
    except MollieError as e:
        return 'API call failed: {error}'.format(error=e)
