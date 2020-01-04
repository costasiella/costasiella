from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django_filters import FilterSet, OrderingFilter
from graphql import GraphQLError

from ..models import Account, FinanceInvoice, FinanceInvoiceItem, FinancePaymentMethod, FinanceTaxRate, FinanceGLAccount, FinanceCostCenter
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..modules.finance_tools import display_float_as_amount

m = Messages()


class FinanceInvoiceItemInterface(graphene.Interface):
    id = graphene.GlobalID()
    price_display = graphene.String()
    subtotal_display = graphene.String()
    tax_display = graphene.String()
    total_display = graphene.String()
    paid_display = graphene.String()
    balance_display = graphene.String()


class FinanceInvoiceItemFilter(FilterSet):
    class Meta:
        model = FinanceInvoiceItem
        fields = [ 
            'id', 
            'finance_invoice', 
        ]
        
        order_by = OrderingFilter(
            fields=(
                ('line_number', 'line_number'),
            )
        )


class FinanceInvoiceItemNode(DjangoObjectType):
    class Meta:
        model = FinanceInvoiceItem
        filter_fields = [ 'id', 'finance_invoice' ]
        interfaces = (graphene.relay.Node, FinanceInvoiceItemInterface, )

    def resolve_price_display(self, info):
        return display_float_as_amount(self.subtotal)

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
        require_login_and_permission(user, 'costasiella.view_financeinvoiceitem')

        return self._meta.model.objects.get(id=id)


class FinanceInvoiceItemQuery(graphene.ObjectType):  
    finance_invoice_items = DjangoFilterConnectionField(
        FinanceInvoiceItemNode,
        filterset_class=FinanceInvoiceItemFilter
    )
    finance_invoice_item = graphene.relay.Node.Field(FinanceInvoiceItemNode)


    def resolve_finance_invoice_items(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeinvoiceitem')

        return FinanceInvoiceItemFilter(kwargs).qs.order_by('line_number')


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

    # Check finance tax rate
    if 'finance_tax_rate' in input:
        result['finance_tax_rate'] = None
        if input['finance_tax_rate']:
            rid = get_rid(input['finance_tax_rate'])
            finance_tax_rate = FinanceTaxRate.objects.filter(id=rid.id).first()
            result['finance_tax_rate'] = finance_tax_rate
            if not finance_tax_rate:
                raise Exception(_('Invalid Finance Tax Rate ID!'))

    # Check GLAccount
    if 'finance_glaccount' in input:
        result['finance_glaccount'] = None
        if input['finance_glaccount']: 
            rid = get_rid(input['finance_glaccount'])
            finance_glaccount= FinanceGLAccount.objects.filter(id=rid.id).first()
            result['finance_glaccount'] = finance_glaccount
            if not finance_glaccount:
                raise Exception(_('Invalid Finance GLAccount ID!'))

    # Check Costcenter
    if 'finance_costcenter' in input:
        result['finance_costcenter'] = None
        if input['finance_costcenter']:
            rid = get_rid(input['finance_costcenter'])
            finance_costcenter= FinanceCostCenter.objects.filter(id=rid.id).first()
            result['finance_costcenter'] = finance_costcenter
            if not finance_costcenter:
                raise Exception(_('Invalid Finance Costcenter ID!'))


    return result


class CreateFinanceInvoiceItem(graphene.relay.ClientIDMutation):
    class Input:
        finance_invoice = graphene.ID(required=True)
        product_name = graphene.String(required=False, default_value="")
        description = graphene.String(required=False, default_value="")
        quantity = graphene.Float(required=False, default_value=0)
        price = graphene.Float(required=False, default_value=0)
        finance_tax_rate = graphene.ID(required=False, default_value=None)
        finance_glaccount = graphene.ID(required=False)
        finance_costcenter = graphene.ID(required=False)
  
    finance_invoice_item = graphene.Field(FinanceInvoiceItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeinvoiceitem')

        validation_result = validate_create_update_input(input)

        finance_invoice_item = FinanceInvoiceItem(
            finance_invoice = validation_result['finance_invoice'],
        )

        if 'product_name' in input:
            finance_invoice_item.product_name = input['product_name']

        if 'description' in input:
            finance_invoice_item.description = input['description']

        if 'quantity' in input:
            finance_invoice_item.quantity = input['quantity']

        if 'price' in input:
            finance_invoice_item.price = input['price']

        if 'finance_tax_rate' in validation_result:
            finance_invoice_item.finance_tax_rate = validation_result['finance_tax_rate']

        if 'finance_glaccount' in validation_result:
            finance_invoice_item.finance_glaccount = validation_result['finance_glaccount']

        if 'finance_costcenter' in validation_result:
            finance_invoice_item.finance_costcenter = validation_result['finance_costcenter']

        # Save invoice_item
        finance_invoice_item.save()

        return CreateFinanceInvoiceItem(finance_invoice_item=finance_invoice_item)


class UpdateFinanceInvoiceItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        line_number = graphene.Int(required=False)
        product_name = graphene.String(required=False)
        description = graphene.String(required=False)
        quantity = graphene.Float(required=False)
        price = graphene.Float(required=False)
        finance_tax_rate = graphene.ID(required=False)
        finance_glaccount = graphene.ID(required=False)
        finance_costcenter = graphene.ID(required=False)
        
    finance_invoice_item = graphene.Field(FinanceInvoiceItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeinvoiceitem')

        print(input)

        rid = get_rid(input['id'])

        finance_invoice_item = FinanceInvoiceItem.objects.filter(id=rid.id).first()
        if not finance_invoice_item:
            raise Exception('Invalid Finance Invoice Item  ID!')

        validation_result = validate_create_update_input(input, update=True)
        
        if 'line_number' in input:
            # TODO: Add code to make sure line numbers remain sequential
            old_line_nr = int(finance_invoice_item.line_number)
            new_line_nr = int(input['line_number'])

            if old_line_nr > new_line_nr:
                items = FinanceInvoiceItem.objects.filter(
                    finance_invoice = finance_invoice_item.finance_invoice,
                    line_number__lt = old_line_nr,
                    line_number__gte = new_line_nr
                )
                for i in items:
                    i.line_number += 1
                    i.save()
            else:
                items = FinanceInvoiceItem.objects.filter(
                    finance_invoice = finance_invoice_item.finance_invoice,
                    line_number__gt = old_line_nr,
                    line_number__lte = new_line_nr
                )
                for i in items:
                    i.line_number -= 1
                    i.save()

            finance_invoice_item.line_number = new_line_nr
            # Always save after this operation
            finance_invoice_item.save()

            # def items_update_sorting():
            #     """
            #         Called as JSON, sets the sorting for invoice items in the db
            #     """
            #     # check if we're using json, if not, provide a fail message
            #     if not request.extension == 'json':
            #         return dict(status  = 'fail',
            #                     message = T("Please call this function as json"))

            #     status = 'OK'
            #     message = T('Changed sorting')

            #     iID       = request.vars['iID']
            #     old_index = int(request.vars['old_index'])
            #     new_index = int(request.vars['new_index'])

            #     query = (db.invoices_items.invoices_id == iID) & \
            #             (db.invoices_items.Sorting == old_index)
            #     changed_row = db(query).select(db.invoices_items.ALL).first()

            #     if old_index > new_index:
            #         query = (db.invoices_items.invoices_id == iID) & \
            #                 (db.invoices_items.Sorting < old_index) & \
            #                 (db.invoices_items.Sorting >= new_index)
            #         rows = db(query).select(db.invoices_items.ALL)
            #         for row in rows:
            #             row.Sorting = row.Sorting + 1
            #             row.update_record()
            #     else:
            #         query = (db.invoices_items.invoices_id == iID) & \
            #                 (db.invoices_items.Sorting > old_index) & \
            #                 (db.invoices_items.Sorting <= new_index)
            #         rows = db(query).select(db.invoices_items.ALL)
            #         for row in rows:
            #             row.Sorting = row.Sorting - 1
            #             row.update_record()


            #     changed_row.Sorting = new_index
            #     changed_row.update_record()

            #     invoice = Invoice(iID)
            #     invoice.on_update()


            #     return dict(status = status,
            #                 message = message)


        if 'product_name' in input:
            finance_invoice_item.product_name = input['product_name']

        if 'description' in input:
            finance_invoice_item.description = input['description']

        if 'quantity' in input:
            finance_invoice_item.quantity = input['quantity']

        if 'price' in input:
            finance_invoice_item.price = input['price']

        if 'finance_tax_rate' in validation_result:
            finance_invoice_item.finance_tax_rate = validation_result['finance_tax_rate']

        if 'finance_glaccount' in validation_result:
            finance_invoice_item.finance_glaccount = validation_result['finance_glaccount']

        if 'finance_costcenter' in validation_result:
            finance_invoice_item.finance_costcenter = validation_result['finance_costcenter']

        finance_invoice_item.save()

        # Update amounts 
        finance_invoice = finance_invoice_item.finance_invoice
        finance_invoice.update_amounts()

        return UpdateFinanceInvoiceItem(finance_invoice_item=finance_invoice_item)


class DeleteFinanceInvoiceItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    
    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financeinvoiceitem')

        rid = get_rid(input['id'])

        finance_invoice_item = FinanceInvoiceItem.objects.filter(id=rid.id).first()
        if not finance_invoice_item:
            raise Exception('Invalid Finance Invoice Item ID!')

        finance_invoice = finance_invoice_item.finance_invoice
        ok = finance_invoice_item.delete()

        # TODO: Add code to make sure line numbers remain sequential
        
        # Update amounts
        finance_invoice.update_amounts()

        return DeleteFinanceInvoiceItem(ok=ok)


class FinanceInvoiceItemMutation(graphene.ObjectType):
    delete_finance_invoice_item = DeleteFinanceInvoiceItem.Field()
    create_finance_invoice_item = CreateFinanceInvoiceItem.Field()
    update_finance_invoice_item = UpdateFinanceInvoiceItem.Field()