from decimal import Decimal

from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django_filters import FilterSet, OrderingFilter
from graphql import GraphQLError

from ..models import Account, FinanceQuote, FinanceQuoteItem, FinanceTaxRate, FinanceGLAccount, FinanceCostCenter
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..modules.finance_tools import display_float_as_amount

m = Messages()


class FinanceQuoteItemInterface(graphene.Interface):
    id = graphene.GlobalID()
    price_display = graphene.String()
    subtotal_display = graphene.String()
    tax_display = graphene.String()
    total_display = graphene.String()


class FinanceQuoteItemFilter(FilterSet):
    class Meta:
        model = FinanceQuoteItem
        fields = [
            'id',
            'finance_quote',
        ]
        
        order_by = OrderingFilter(
            fields=(
                ('line_number', 'line_number'),
            )
        )


class FinanceQuoteItemNode(DjangoObjectType):
    class Meta:
        model = FinanceQuoteItem
        fields = (
            'finance_quote',
            'line_number',
            'product_name',
            'description',
            'quantity',
            'price',
            'finance_tax_rate',
            'subtotal',
            'tax',
            'total',
            'finance_glaccount',
            'finance_costcenter'
        )
        filter_fields = ['id', 'finance_quote']
        interfaces = (graphene.relay.Node, FinanceQuoteItemInterface, )

    def resolve_price_display(self, info):
        return display_float_as_amount(self.price)

    def resolve_subtotal_display(self, info):
        return display_float_as_amount(self.subtotal)

    def resolve_tax_display(self, info):
        return display_float_as_amount(self.tax)

    def resolve_total_display(self, info):
        return display_float_as_amount(self.total)  


    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financequoteitem')

        return self._meta.model.objects.get(id=id)


class FinanceQuoteItemQuery(graphene.ObjectType):  
    finance_quote_items = DjangoFilterConnectionField(
        FinanceQuoteItemNode,
        filterset_class=FinanceQuoteItemFilter,
        orderBy=graphene.List(of_type=graphene.String)
    )
    finance_quote_item = graphene.relay.Node.Field(FinanceQuoteItemNode)

    def resolve_finance_quote_items(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financequoteitem')

        order_by = kwargs.get('orderBy')
        if not order_by:
            order_by = ['line_number']

        # example gql
        # financeInvoiceItems(..., orderBy: ["-finance_quote__date_sent"]) {
        # return FinanceQuoteItemFilter(kwargs).qs.order_by('line_number')
        return FinanceQuoteItemFilter(kwargs).qs.order_by(*order_by)


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    ## Create only
    if not update:
        # quote
        rid = get_rid(input['finance_quote'])
        finance_quote = FinanceQuote.objects.filter(id=rid.id).first()
        result['finance_quote'] = finance_quote
        if not finance_quote:
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


class CreateFinanceQuoteItem(graphene.relay.ClientIDMutation):
    class Input:
        finance_quote = graphene.ID(required=True)
        product_name = graphene.String(required=False, default_value="")
        description = graphene.String(required=False, default_value="")
        quantity = graphene.Decimal(required=False, default_value=Decimal(0))
        price = graphene.Decimal(required=False, default_value=Decimal(0))
        finance_tax_rate = graphene.ID(required=False, default_value=None)
        finance_glaccount = graphene.ID(required=False)
        finance_costcenter = graphene.ID(required=False)
  
    finance_quote_item = graphene.Field(FinanceQuoteItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financequoteitem')

        validation_result = validate_create_update_input(input)
        finance_quote = validation_result['finance_quote']

        finance_quote_item = FinanceQuoteItem(
            finance_quote=finance_quote,
            line_number=finance_quote._get_item_next_line_nr()
        )

        if 'product_name' in input:
            finance_quote_item.product_name = input['product_name']

        if 'description' in input:
            finance_quote_item.description = input['description']

        if 'quantity' in input:
            finance_quote_item.quantity = input['quantity']

        if 'price' in input:
            finance_quote_item.price = input['price']

        if 'finance_tax_rate' in validation_result:
            finance_quote_item.finance_tax_rate = validation_result['finance_tax_rate']

        if 'finance_glaccount' in validation_result:
            finance_quote_item.finance_glaccount = validation_result['finance_glaccount']

        if 'finance_costcenter' in validation_result:
            finance_quote_item.finance_costcenter = validation_result['finance_costcenter']

        # Save quote_item
        finance_quote_item.save()

        return CreateFinanceQuoteItem(finance_quote_item=finance_quote_item)


class UpdateFinanceQuoteItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        line_number = graphene.Int(required=False)
        product_name = graphene.String(required=False)
        description = graphene.String(required=False)
        quantity = graphene.Decimal(required=False)
        price = graphene.Decimal(required=False)
        finance_tax_rate = graphene.ID(required=False)
        finance_glaccount = graphene.ID(required=False)
        finance_costcenter = graphene.ID(required=False)
        
    finance_quote_item = graphene.Field(FinanceQuoteItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financequoteitem')

        rid = get_rid(input['id'])
        finance_quote_item = FinanceQuoteItem.objects.filter(id=rid.id).first()
        if not finance_quote_item:
            raise Exception('Invalid Finance Invoice Item  ID!')

        validation_result = validate_create_update_input(input, update=True)
        
        if 'line_number' in input:
            old_line_nr = int(finance_quote_item.line_number)
            new_line_nr = int(input['line_number'])

            if old_line_nr > new_line_nr:
                items = FinanceQuoteItem.objects.filter(
                    finance_quote=finance_quote_item.finance_quote,
                    line_number__lt=old_line_nr,
                    line_number__gte=new_line_nr
                )
                for i in items:
                    i.line_number += 1
                    i.save()
            else:
                items = FinanceQuoteItem.objects.filter(
                    finance_quote=finance_quote_item.finance_quote,
                    line_number__gt=old_line_nr,
                    line_number__lte=new_line_nr
                )
                for i in items:
                    i.line_number -= 1
                    i.save()

            finance_quote_item.line_number = new_line_nr
            # Always save after this operation
            finance_quote_item.save()

        if 'product_name' in input:
            finance_quote_item.product_name = input['product_name']

        if 'description' in input:
            finance_quote_item.description = input['description']

        if 'quantity' in input:
            finance_quote_item.quantity = input['quantity']

        if 'price' in input:
            finance_quote_item.price = input['price']

        if 'finance_tax_rate' in validation_result:
            finance_quote_item.finance_tax_rate = validation_result['finance_tax_rate']

        if 'finance_glaccount' in validation_result:
            finance_quote_item.finance_glaccount = validation_result['finance_glaccount']

        if 'finance_costcenter' in validation_result:
            finance_quote_item.finance_costcenter = validation_result['finance_costcenter']

        finance_quote_item.save()

        # Update amounts 
        finance_quote = finance_quote_item.finance_quote
        finance_quote.update_amounts()

        return UpdateFinanceQuoteItem(finance_quote_item=finance_quote_item)


class DeleteFinanceQuoteItem(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    
    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financequoteitem')

        rid = get_rid(input['id'])

        finance_quote_item = FinanceQuoteItem.objects.filter(id=rid.id).first()
        if not finance_quote_item:
            raise Exception('Invalid Finance Invoice Item ID!')

        finance_quote = finance_quote_item.finance_quote

        # Update line numbers of following items to keep them sequential
        items = FinanceQuoteItem.objects.filter(
            finance_quote=finance_quote_item.finance_quote,
            line_number__gt=finance_quote_item.line_number
        )
        for i in items:
            i.line_number -= 1
            i.save()

        # Actually delete item
        ok = bool(finance_quote_item.delete())
        
        # Update amounts
        finance_quote.update_amounts()

        return DeleteFinanceQuoteItem(ok=ok)


class FinanceQuoteItemMutation(graphene.ObjectType):
    delete_finance_quote_item = DeleteFinanceQuoteItem.Field()
    create_finance_quote_item = CreateFinanceQuoteItem.Field()
    update_finance_quote_item = UpdateFinanceQuoteItem.Field()
