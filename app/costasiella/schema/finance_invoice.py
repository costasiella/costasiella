from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, FinanceInvoice, FinanceInvoiceGroup, FinancePaymentMethod
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..modules.finance_tools import display_float_as_amount

m = Messages()

class FinanceInvoiceInterface(graphene.Interface):
    id = graphene.GlobalID()
    subtotal_display = graphene.String()
    tax_display = graphene.String()
    total_display = graphene.String()
    paid_display = graphene.String()
    balance_display = graphene.String()


class FinanceInvoiceNode(DjangoObjectType):
    class Meta:
        model = FinanceInvoice
        filter_fields = {
            'account': ['exact'],
            'invoice_number': ['icontains', 'exact'],
            'status': ['exact'],
            'date_sent': ['lte', 'gte'],
            'date_due': ['lte', 'gte'],
        }
        interfaces = (graphene.relay.Node, FinanceInvoiceInterface, )

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
        require_login_and_permission(user, 'costasiella.view_financeinvoice')

        return self._meta.model.objects.get(id=id)


class FinanceInvoiceQuery(graphene.ObjectType):
    finance_invoices = DjangoFilterConnectionField(FinanceInvoiceNode)
    finance_invoice = graphene.relay.Node.Field(FinanceInvoiceNode)

    def resolve_finance_invoices(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeinvoice')

        return FinanceInvoice.objects.all().order_by('-pk')


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Fetch & check invoice group
    if not update:
        ## Create only
        # invoice group
        rid = get_rid(input['finance_invoice_group'])
        finance_invoice_group = FinanceInvoiceGroup.objects.filter(id=rid.id).first()
        result['finance_invoice_group'] = finance_invoice_group
        if not finance_invoice_group:
            raise Exception(_('Invalid Finance Invoice Group ID!'))

        # account
        rid = get_rid(input['account'])
        account = Account.objects.filter(id=rid.id).first()
        result['account'] = account
        if not account:
            raise Exception(_('Invalid Account ID!'))

    # Check finance payment method
    if 'finance_payment_method' in input:
        if input['finance_payment_method']:
            rid = get_rid(input['finance_payment_method'])
            finance_payment_method = FinancePaymentMethod.objects.filter(id=rid.id).first()
            result['finance_payment_method'] = finance_payment_method
            if not finance_payment_method:
                raise Exception(_('Invalid Finance Payment Method ID!'))


    return result


class CreateFinanceInvoice(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        finance_invoice_group = graphene.ID(required=True)
        summary = graphene.String(required=False, default_value="")
        
    finance_invoice = graphene.Field(FinanceInvoiceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeinvoice')

        validation_result = validate_create_update_input(input)
        finance_invoice_group = validation_result['finance_invoice_group']

        finance_invoice = FinanceInvoice(
            account = validation_result['account'],
            finance_invoice_group = finance_invoice_group,
            status = 'DRAFT',
            terms = finance_invoice_group.terms,
            footer = finance_invoice_group.footer
        )

        if 'summary' in input:
            finance_invoice.summary = input['summary']

        # Save invoice
        finance_invoice.save()

        return CreateFinanceInvoice(finance_invoice=finance_invoice)


class UpdateFinanceInvoice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        finance_payment_method = graphene.ID(required=False)
        summary = graphene.String(required=False)
        relation_company = graphene.String(required=False)
        relation_company_registration = graphene.String(required=False)
        relation_company_tax_registration = graphene.String(required=False)
        relation_contact_name = graphene.String(required=False)
        relation_address = graphene.String(required=False)
        relation_postcode = graphene.String(required=False)
        relation_city = graphene.String(required=False)
        relation_country = graphene.String(required=False)
        invoice_number = graphene.String(required=False)
        date_sent = graphene.types.datetime.Date(required=False)
        date_due = graphene.types.datetime.Date(required=False)
        status = graphene.String(required=False)
        terms = graphene.String(required=False)
        footer = graphene.String(required=False)
        note = graphene.String(required=False)

    finance_invoice = graphene.Field(FinanceInvoiceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeinvoice')

        print(input)

        rid = get_rid(input['id'])

        finance_invoice = FinanceInvoice.objects.filter(id=rid.id).first()
        if not finance_invoice:
            raise Exception('Invalid Finance Invoice  ID!')

        validation_result = validate_create_update_input(input, update=True)

        if 'summary' in input:
            finance_invoice.summary = input['summary']

        if 'relation_company' in input:
            finance_invoice.relation_company = input['relation_company']

        if 'relation_company_registration' in input:
            finance_invoice.relation_company_registration = input['relation_company_registration']

        if 'relation_company_tax_registration' in input:
            finance_invoice.relation_company_tax_registration = input['relation_company_tax_registration']

        if 'relation_contact_name' in input:
            finance_invoice.relation_contact_name = input['relation_contact_name']

        if 'relation_address' in input:
            finance_invoice.relation_address = input['relation_address']

        if 'relation_postcode' in input:
            finance_invoice.relation_postcode = input['relation_postcode']

        if 'relation_city' in input:
            finance_invoice.relation_city = input['relation_city']

        if 'relation_country' in input:
            finance_invoice.relation_country = input['relation_country']

        if 'invoice_number' in input:
            finance_invoice.invoice_number = input['invoice_number']

        if 'date_sent' in input:
            finance_invoice.date_sent = input['date_sent']

        if 'date_due' in input:
            finance_invoice.date_due = input['date_due']

        if 'status' in input:
            finance_invoice.status = input['status']

        if 'terms' in input:
            finance_invoice.terms = input['terms']

        if 'footer' in input:
            finance_invoice.footer = input['footer']

        if 'note' in input:
            finance_invoice.note = input['note']

        if 'finance_payment_method' in validation_result:
            finance_invoice.finance_payment_method = validation_result['finance_payment_method']


        finance_invoice.save()

        return UpdateFinanceInvoice(finance_invoice=finance_invoice)


class DeleteFinanceInvoice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    
    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financeinvoice')

        rid = get_rid(input['id'])

        finance_invoice = FinanceInvoice.objects.filter(id=rid.id).first()
        if not finance_invoice:
            raise Exception('Invalid Finance Invoice ID!')

        ok = finance_invoice.delete()

        return DeleteFinanceInvoice(ok=ok)


class FinanceInvoiceMutation(graphene.ObjectType):
    delete_finance_invoice = DeleteFinanceInvoice.Field()
    create_finance_invoice = CreateFinanceInvoice.Field()
    update_finance_invoice = UpdateFinanceInvoice.Field()