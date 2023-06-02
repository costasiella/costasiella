from django.utils.translation import gettext as _
from django.db.models import Q, FilteredRelation, OuterRef, Subquery

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import FinanceInvoice, IntegrationLogMollie, SystemSetting
from ..modules.gql_tools import require_login_and_permission, require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages
from ..modules.finance_tools import get_currency


m = Messages()

import datetime


# ScheduleClassType
class FinanceInvoicePaymentLinkType(graphene.ObjectType):
    payment_link = graphene.String()


class CreateFinanceInvoicePaymentLink(graphene.Mutation):
    class Arguments:
        id = graphene.ID()  # FinanceInvoiceID

    finance_invoice_payment_link = graphene.Field(FinanceInvoicePaymentLinkType)

    @classmethod
    def mutate(self, root, info, id):
        from mollie.api.client import Client
        from mollie.api.error import Error as MollieError

        from ..dudes.mollie_dude import MollieDude


        user = info.context.user
        host = info.context.get_host()
        # https://docs.djangoproject.com/en/3.0/ref/request-response/
        # Check if the user owns this invoice
        rid = get_rid(id)
        finance_invoice = FinanceInvoice.objects.get(pk=rid.id)

        if finance_invoice.account.id != user.id:
            raise GraphQLError(
                m.finance_invoice_belongs_other_account, 
                extensions={'code': m.finance_invoice_belongs_other_account}
            )

        mollie_dude = MollieDude()

        mollie = Client()
        # mollie_api_key = get_sys_property('mollie_website_profile')
        mollie_api_key = mollie_dude.get_api_key()
        mollie.set_api_key(mollie_api_key)
        
        # Invoice information
        amount = finance_invoice.balance
        description = _("Invoice #") + str(finance_invoice.invoice_number)
        
        # Gather mollie payment info
        redirect_url = 'https://' + host + '/#/shop/account/invoice_payment_status/' + id
        # For development
        if "localhost" in redirect_url:
            redirect_url = redirect_url.replace("localhost:8000", "dev.costasiella.com:8000")

        mollie_customer_id = mollie_dude.get_account_mollie_customer_id(
          user,
          mollie
        )
        webhook_url = mollie_dude.get_webhook_url_from_request(info.context)
        # For development
        if "localhost" in webhook_url:
            webhook_url = webhook_url.replace("localhost:8000", "dev.costasiella.com:8000")

        # Check recurring or not
        invoice_contains_subscription = finance_invoice.items_contain_subscription()
        sequence_type = None
        if invoice_contains_subscription:
            # Check if we have a mandate
            mandates = mollie_dude.get_account_mollie_mandates(user, mollie)
            # set default sequence type, change to recurring if a valid mandate is found.
            sequence_type = 'first'
            if mandates['count'] > 0:
                # background payment
                valid_mandate = False
                for mandate in mandates['_embedded']['mandates']:
                    if mandate['status'] == 'valid':
                        valid_mandate = True
                        break

                if valid_mandate:
                    # Do a normal payment, probably an automatic payment failed somewhere in the process
                    # and customer should pay manually now
                    sequence_type = None

        # Fetch currency eg. EUR or USD, etc.
        currency = get_currency() or "EUR"
        payment = mollie.payments.create({
            'amount': {
                'currency': currency,
                'value': str(amount)
            },
            'description': description,
            'sequenceType': sequence_type,
            'customerId': mollie_customer_id,
            'redirectUrl': redirect_url,
            'webhookUrl': webhook_url,
            'metadata': {
                'invoice_id': finance_invoice.pk
            }
        })

        #  Log payment info
        log = IntegrationLogMollie(
            log_source="INVOICE_PAY",
            mollie_payment_id=payment['id'],
            recurring_type=sequence_type,
            webhook_url=webhook_url,
            finance_invoice=finance_invoice,
        )
        log.save()

        finance_invoice_payment_link = FinanceInvoicePaymentLinkType()
        finance_invoice_payment_link.payment_link = payment.checkout_url

        return CreateFinanceInvoicePaymentLink(
            finance_invoice_payment_link=finance_invoice_payment_link
        )


class FinanceInvoicePaymentLinkMutation(graphene.ObjectType):
    create_finance_invoice_payment_link = CreateFinanceInvoicePaymentLink.Field()


"""
mutation CreateFinanceInvoicePaymentLink($id: ID!) {
  createFinanceInvoicePaymentLink(id: $id) {
    financeInvoicePaymentLink {
      paymentLink
    }
  }
}

{
  "id": "RmluYW5jZU9yZGVyTm9kZTo1OQ=="
}

"""