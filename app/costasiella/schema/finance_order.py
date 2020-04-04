from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, FinanceOrder
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..modules.finance_tools import display_float_as_amount

m = Messages()

class FinanceOrderInterface(graphene.Interface):
    id = graphene.GlobalID()
    subtotal_display = graphene.String()
    tax_display = graphene.String()
    total_display = graphene.String()
    paid_display = graphene.String()
    balance_display = graphene.String()


class FinanceOrderNode(DjangoObjectType):
    class Meta:
        model = FinanceOrder
        filter_fields = {
            'account': ['exact'],
            'invoice_number': ['icontains', 'exact'],
            'status': ['exact'],
            'date_sent': ['lte', 'gte'],
            'date_due': ['lte', 'gte'],
        }
        interfaces = (graphene.relay.Node, FinanceOrderInterface, )

    def resolve_subtotal_display(self, info):
        return display_float_as_amount(self.subtotal)

    def resolve_tax_display(self, info):
        return display_float_as_amount(self.tax)

    def resolve_total_display(self, info):
        return display_float_as_amount(self.total)

    def resolve_paid_display(self, info):
        return display_float_as_amount(self.paid)

    def resolve_balance_display(self, info):
        return display_float_as_amount(self.balance)        


    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeorder')

        return self._meta.model.objects.get(id=id)


class FinanceOrderQuery(graphene.ObjectType):
    finance_orders = DjangoFilterConnectionField(FinanceOrderNode)
    finance_order = graphene.relay.Node.Field(FinanceOrderNode)

    def resolve_finance_orders(self, info, archived=False, **kwargs):
        user = info.context.usetr
        require_login_and_permission(user, 'costasiella.view_financeorder')

        return FinanceOrder.objects.all().order_by('-pk')


# def validate_create_update_input(input, update=False):
#     """
#     Validate input
#     """ 
#     result = {}

#     # Fetch & check invoice group
#     if not update:
#         ## Create only
#         # invoice group
#         rid = get_rid(input['finance_invoice_group'])
#         finance_invoice_group = FinanceInvoiceGroup.objects.filter(id=rid.id).first()
#         result['finance_invoice_group'] = finance_invoice_group
#         if not finance_invoice_group:
#             raise Exception(_('Invalid Finance Invoice Group ID!'))

#         # account
#         rid = get_rid(input['account'])
#         account = Account.objects.filter(id=rid.id).first()
#         result['account'] = account
#         if not account:
#             raise Exception(_('Invalid Account ID!'))

#     # Check finance payment method
#     if 'finance_payment_method' in input:
#         if input['finance_payment_method']:
#             rid = get_rid(input['finance_payment_method'])
#             finance_payment_method = FinancePaymentMethod.objects.filter(id=rid.id).first()
#             result['finance_payment_method'] = finance_payment_method
#             if not finance_payment_method:
#                 raise Exception(_('Invalid Finance Payment Method ID!'))


#     return result


class CreateFinanceOrder(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        note = graphene.String(required=False, default_value="")
        
    finance_order = graphene.Field(FinanceOrderNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeorder')

        # validation_result = validate_create_update_input(input)
        # finance_invoice_group = validation_result['finance_invoice_group']

        finance_order = FinanceOrder(
            account = validation_result['account'],
        )

        if 'note' in input:
            finance_order.note = input['note']

        # Save order
        finance_order.save()

        return CreateFinanceOrder(finance_order=finance_order)


class UpdateFinanceOrder(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        status = graphene.String(required=False)
        note = graphene.String(required=False)

    finance_order = graphene.Field(FinanceOrderNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeinvoice')

        print(input)
        rid = get_rid(input['id'])

        finance_order = FinanceOrder.objects.filter(id=rid.id).first()
        if not finance_order:
            raise Exception('Invalid Finance Order ID!')

        validation_result = validate_create_update_input(input, update=True)

        if 'status' in input:
            finance_order.status = input['status']

        if 'note' in input:
            finance_order.note = input['note']

        finance_order.save()

        return UpdateFinanceOrder(finance_order=finance_order)


class DeleteFinanceOrder(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    
    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financeorder')

        rid = get_rid(input['id'])

        finance_order = FinanceOrder.objects.filter(id=rid.id).first()
        if not finance_order:
            raise Exception('Invalid Finance Order ID!')

        ok = finance_order.delete()

        return DeleteFinanceOrder(ok=ok)


class FinanceOrderMutation(graphene.ObjectType):
    delete_finance_order = DeleteFinanceInvoice.Field()
    create_finance_order = CreateFinanceInvoice.Field()
    update_finance_order = UpdateFinanceInvoice.Field()