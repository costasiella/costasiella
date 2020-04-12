from django.utils.translation import gettext as _
from django.db.models import Q, FilteredRelation, OuterRef, Subquery

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import FinanceOrder, IntegrationLogMollie
from ..modules.gql_tools import require_login_and_permission, require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages


m = Messages()

import datetime


# ScheduleClassType
class FinanceOrderPaymentLinkType(graphene.ObjectType):
    payment_link = graphene.String()


class CreateFinanceOrderPaymentLink(graphene.Mutation):
    class Arguments:
        id = graphene.ID() # FinanceOrderID

    finance_order_payment_link = graphene.Field(FinanceOrderPaymentLinkType)

    @classmethod
    def mutate(self, root, info, id):
        from mollie.api.client import Client
        from mollie.api.error import Error as MollieError

        from ..dudes.mollie_dude import MollieDude

        print(info.context)
        # print(info.context.build_absolute_uri())
        
        user = info.context.user
        host = info.context.get_host()
        # https://docs.djangoproject.com/en/3.0/ref/request-response/
        # Check if the user owns this order
        print(id)

        rid = get_rid(id)
        finance_order = FinanceOrder.objects.get(pk=rid.id)
        if finance_order.account != user:
            raise GraphQLError(
                m.finance_order_belongs_other_account, 
                extensions={'code': FINANCE_ORDER_OTHER_ACCOUNT}
            )

        mollie_dude = MollieDude()

        mollie = Client()
        # mollie_api_key = get_sys_property('mollie_website_profile')
        mollie_api_key = "test_kBdWS2sfs2k9HcSCfx7cQkCbc3f5VQ"
        mollie.set_api_key(mollie_api_key)
        
        # Order information
        amount = finance_order.total
        description = _("Order #") + str(finance_order.id)

        
        # Gather mollie payment info
        recurring_type = None
        redirect_url = 'https://' + host + '/#/shop/checkout/complete/' + id
        print(redirect_url)
        mollie_customer_id = mollie_dude.get_account_mollie_customer_id(
          user,
          mollie
        )
        print(mollie_customer_id)
        webhook_url = mollie_dude.get_webhook_url(info.context)
        print(webhook_url)

        #TODO: Fetch currency eg. EUR or USD, etc.

        payment = mollie.payments.create({
            'amount': {
                'currency': "EUR",
                'value': str(amount)
            },
            'description': description,
            'sequenceType': recurring_type,
            'customerId': mollie_customer_id,
            'redirectUrl': redirect_url,
            'webhookUrl': webhook_url,
            'metadata': {
                'customers_orders_id': finance_order.pk
            }
        })

        print(payment)

        #  Log payment info
        log = IntegrationLogMollie(
            mollie_payment_id = payment['id'],
            recurring_type = recurring_type,
            webhook_url = webhook_url,
            finance_order = finance_order,
        )
        log.save()

        finance_order_payment_link = FinanceOrderPaymentLinkType()
        finance_order_payment_link.payment_link = payment.checkout_url

        return CreateFinanceOrderPaymentLink(
            finance_order_payment_link=finance_order_payment_link
        )


class FinanceOrderPaymentLinkMutation(graphene.ObjectType):
    create_finance_order_payment_link = CreateFinanceOrderPaymentLink.Field()


"""
mutation CreateFinanceOrderPaymentLink($id: ID!) {
  createFinanceOrderPaymentLink(id: $id) {
    financeOrderPaymentLink {
      paymentLink
    }
  }
}

{
  "id": "RmluYW5jZU9yZGVyTm9kZTo1OQ=="
}

"""