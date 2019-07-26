from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import FinanceInvoice, FinanceInvoiceGroup, FinancePaymentMethod
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class FinanceInvoiceNode(DjangoObjectType):
    class Meta:
        model = FinanceInvoice
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeinvoice')

        return self._meta.model.objects.get(id=id)


class FinanceInvoiceQuery(graphene.ObjectType):
    finance_invoices = DjangoFilterConnectionField(FinanceInvoiceNode)
    finance_invoice_ = graphene.relay.Node.Field(FinanceInvoiceNode)

    def resolve_finance_invoices(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeinvoice')

        return FinanceInvoice.objects.all().order_by('invoice_number')


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
        
    finance_invoice_ = graphene.Field(FinanceInvoiceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeinvoice')

        validation_result = validate_create_update_input(input)

        finance_invoice_group = validation_result['finance_invoice_group']

        finance_invoice_ = FinanceInvoice(
            finance_invoice_group = finance_invoice_group,
            status = 'DRAFT',
            terms = finance_invoice_group.terms,
            footer = finance_invoice_group.footer
        )

        if 'summary' in input:
            finance_invoice.summary = input['summary']

        


        #TODO: Link to account or business relation

        #TODO: Based on link, set relation fields

        finance_invoice.save()

        return CreateFinanceInvoice(finance_invoice_=finance_invoice_)


class UpdateFinanceInvoice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        display_public = graphene.Boolean(required=False)
        name = graphene.String(required=True)
        next_id = graphene.Int(required=False)
        due_after_days = graphene.Int(required=False)
        prefix = graphene.String(required=False)
        prefix_year = graphene.Boolean(required=False)
        auto_reset_prefix_year = graphene.Boolean(required=False)
        terms = graphene.String(required=False)
        footer = graphene.String(required=False)
        code = graphene.String(required=False, default_value="")
        
    finance_invoice_ = graphene.Field(FinanceInvoiceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeinvoice')

        rid = get_rid(input['id'])

        finance_invoice_ = FinanceInvoice.objects.filter(id=rid.id).first()
        if not finance_invoice_:
            raise Exception('Invalid Finance Invoice  ID!')

        finance_invoice_.name = input['name']

        if 'next_id' in input:
            finance_invoice_.due_after_days = input['next_id']

        if 'due_after_days' in input:
            finance_invoice_.due_after_days = input['due_after_days']

        if 'prefix' in input:
            finance_invoice_.prefix = input['prefix']

        if 'prefix_year' in input:
            finance_invoice_.prefix_year = input['prefix_year']

        if 'auto_reset_prefix_year' in input:
            finance_invoice_.auto_reset_prefix_year = input['auto_reset_prefix_year']

        if 'terms' in input:
            finance_invoice_.terms = input['terms']

        if 'footer' in input:
            finance_invoice_.footer = input['footer']

        if 'code' in input:
            finance_invoice_.code = input['code']

        finance_invoice_.save()

        return UpdateFinanceInvoice(finance_invoice_=finance_invoice_)


class ArchiveFinanceInvoice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    finance_invoice_ = graphene.Field(FinanceInvoiceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financeinvoice')

        rid = get_rid(input['id'])

        finance_invoice_ = FinanceInvoice.objects.filter(id=rid.id).first()
        if not finance_invoice_:
            raise Exception('Invalid Finance Invoice  ID!')

        finance_invoice_.archived = input['archived']
        finance_invoice_.save()

        return ArchiveFinanceInvoice(finance_invoice_=finance_invoice_)


class FinanceInvoiceMutation(graphene.ObjectType):
    archive_finance_invoice_ = ArchiveFinanceInvoice.Field()
    create_finance_invoice_ = CreateFinanceInvoice.Field()
    update_finance_invoice_ = UpdateFinanceInvoice.Field()