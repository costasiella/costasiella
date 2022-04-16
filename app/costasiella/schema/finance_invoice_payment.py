from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, FinanceInvoice, FinanceInvoicePayment, FinancePaymentMethod
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..modules.finance_tools import display_float_as_amount

m = Messages()


class FinanceInvoicePaymentInterface(graphene.Interface):
    id = graphene.GlobalID()
    amount_display = graphene.String()


class FinanceInvoicePaymentNode(DjangoObjectType):
    class Meta:
        model = FinanceInvoicePayment
        fields = (
            'finance_invoice',
            'date',
            'amount',
            'finance_payment_method',
            'note',
            'online_payment_id',
            'online_refund_id',
            'online_chargeback_id'
        )
        filter_fields = {
            "id": ["exact"],
            "finance_invoice": ["exact"],
        }
        interfaces = (graphene.relay.Node, FinanceInvoicePaymentInterface, )

    def resolve_amount_display(self, info):
        return display_float_as_amount(self.amount)      


    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeinvoicepayment')

        return self._meta.model.objects.get(id=id)


class FinanceInvoicePaymentQuery(graphene.ObjectType):
    finance_invoice_payments = DjangoFilterConnectionField(FinanceInvoicePaymentNode)
    finance_invoice_payment = graphene.relay.Node.Field(FinanceInvoicePaymentNode)

    def resolve_finance_invoice_payments(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeinvoicepayment')

        return FinanceInvoicePayment.objects.all().order_by('date')


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    ## Create only
    if not update:
        # invoice
        rid = get_rid(input['finance_invoice'])
        finance_invoice = FinanceInvoice.objects.filter(id=rid.id).first()
        result['finance_invoice'] = finance_invoice
        if not finance_invoice:
            raise Exception(_('Invalid Finance Invoice ID!'))

    # Check finance payment method
    if 'finance_payment_method' in input:
        result['finance_payment_method'] = None
        if input['finance_payment_method']:
            rid = get_rid(input['finance_payment_method'])
            finance_payment_method = FinancePaymentMethod.objects.get(id=rid.id)
            result['finance_payment_method'] = finance_payment_method
            if not finance_payment_method:
                raise Exception(_('Invalid Finance Tax Rate ID!'))


    return result


class CreateFinanceInvoicePayment(graphene.relay.ClientIDMutation):
    class Input:
        finance_invoice = graphene.ID(required=True)
        date = graphene.types.datetime.Date(required=True)    
        amount = graphene.Decimal(required=True)
        finance_payment_method = graphene.ID(required=False, default_value=None)
        note = graphene.String(required=False, default_value="")
  
    finance_invoice_payment = graphene.Field(FinanceInvoicePaymentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeinvoicepayment')

        validation_result = validate_create_update_input(input)
        finance_invoice = validation_result['finance_invoice']

        finance_invoice_payment = FinanceInvoicePayment(
            finance_invoice = finance_invoice,
            amount = input['amount'],
            date = input['date'],
            note = input['note'] # Not required, but we set a default value
        )

        if 'finance_payment_method' in validation_result:
            finance_invoice_payment.finance_payment_method = validation_result['finance_payment_method']

        # Save invoice payment
        finance_invoice_payment.save()

        # Update invoice total amounts 
        finance_invoice.update_amounts()

        return CreateFinanceInvoicePayment(finance_invoice_payment=finance_invoice_payment)


class UpdateFinanceInvoicePayment(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        date = graphene.types.datetime.Date(required=False)
        amount = graphene.Decimal(required=False)
        finance_payment_method = graphene.ID(required=False)
        note = graphene.String(required=False)
        
    finance_invoice_payment = graphene.Field(FinanceInvoicePaymentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeinvoicepayment')

        rid = get_rid(input['id'])

        finance_invoice_payment = FinanceInvoicePayment.objects.filter(id=rid.id).first()
        if not finance_invoice_payment:
            raise Exception('Invalid Finance Invoice Payment  ID!')

        validation_result = validate_create_update_input(input, update=True)
        
        if 'amount' in input:
            finance_invoice_payment.amount = input['amount']

        if 'date' in input:
            finance_invoice_payment.date = input['date']

        if 'note' in input:
            finance_invoice_payment.note = input['note']

        if 'finance_payment_method' in validation_result:
            finance_invoice_payment.finance_payment_method = validation_result['finance_payment_method']

        finance_invoice_payment.save()

        # Update invoice total amounts 
        finance_invoice = finance_invoice_payment.finance_invoice
        finance_invoice.update_amounts()

        return UpdateFinanceInvoicePayment(finance_invoice_payment=finance_invoice_payment)


class DeleteFinanceInvoicePayment(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    
    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financeinvoicepayment')

        rid = get_rid(input['id'])

        finance_invoice_payment = FinanceInvoicePayment.objects.get(id=rid.id)
        if not finance_invoice_payment:
            raise Exception('Invalid Finance Invoice Payment ID!')

        finance_invoice = finance_invoice_payment.finance_invoice
        ok = bool(finance_invoice_payment.delete())
        
        # Update amounts
        finance_invoice.update_amounts()

        return DeleteFinanceInvoicePayment(ok=ok)


class FinanceInvoicePaymentMutation(graphene.ObjectType):
    delete_finance_invoice_payment = DeleteFinanceInvoicePayment.Field()
    create_finance_invoice_payment = CreateFinanceInvoicePayment.Field()
    update_finance_invoice_payment = UpdateFinanceInvoicePayment.Field()