from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_relay import to_global_id

from ..models import Account, AccountSubscription, Business, FinanceQuote, FinanceQuoteGroup
from ..modules.gql_tools import require_login, require_login_and_permission, require_permission, get_rid
from ..modules.messages import Messages
from ..modules.finance_tools import display_float_as_amount

from .custom_schema_validators import is_year, is_month

m = Messages()


class FinanceQuoteInterface(graphene.Interface):
    id = graphene.GlobalID()
    subtotal_display = graphene.String()
    tax_display = graphene.String()
    total_display = graphene.String()


class FinanceQuoteNode(DjangoObjectType):
    class Meta:
        model = FinanceQuote
        fields = (
            'account',
            'business',
            'finance_quote_group',
            'custom_to',
            'relation_company',
            'relation_company_registration',
            'relation_company_tax_registration',
            'relation_contact_name',
            'relation_address',
            'relation_postcode',
            'relation_city',
            'relation_country',
            'status',
            'summary',
            'quote_number',
            'date_sent',
            'date_expire',
            'terms',
            'footer',
            'note',
            'subtotal',
            'tax',
            'total',
            'created_at',
            'updated_at',
            # Reverse relations
            'items',
        )
        filter_fields = {
            'account': ['exact'],
            'business': ['exact'],
            'quote_number': ['icontains', 'exact'],
            'status': ['exact'],
            'date_sent': ['lte', 'gte'],
            'date_expire': ['lte', 'gte'],
        }
        interfaces = (graphene.relay.Node, FinanceQuoteInterface, )

    def resolve_subtotal_display(self, info):
        return display_float_as_amount(self.subtotal)

    def resolve_tax_display(self, info):
        return display_float_as_amount(self.tax)

    def resolve_total_display(self, info):
        return display_float_as_amount(self.total)

    @classmethod
    def get_node(cls, info, id):
        user = info.context.user
        require_login(user)

        # Own quote always ok
        finance_quote = cls._meta.model.objects.get(id=id)
        if finance_quote.account == user:
            return finance_quote

        # Permission required to quotes belonging to other accounts
        require_permission(user, 'costasiella.view_financequote')

        return finance_quote


class FinanceQuoteQuery(graphene.ObjectType):
    finance_quotes = DjangoFilterConnectionField(FinanceQuoteNode)
    finance_quote = graphene.relay.Node.Field(FinanceQuoteNode)

    def resolve_finance_quotes(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login(user)
        view_permission = user.has_perm('costasiella.view_financequote')

        if view_permission and 'account' in kwargs and kwargs['account']:
            # Allow user to filter by any account
            rid = get_rid(kwargs.get('account', user.id))
            account_id = rid.id
        elif view_permission:
            # return all
            account_id = None
        else:
            # A user can only query their own quotes
            account_id = user.id

        order_by = '-pk'
        if account_id:
            return FinanceQuote.objects.filter(account=account_id).order_by(order_by)
        else:
            return FinanceQuote.objects.all().order_by(order_by)


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Fetch & check quote group
    if not update:
        ## Create only
        # quote group
        rid = get_rid(input['finance_quote_group'])
        finance_quote_group = FinanceQuoteGroup.objects.filter(id=rid.id).first()
        result['finance_quote_group'] = finance_quote_group
        if not finance_quote_group:
            raise Exception(_('Invalid Finance Invoice Group ID!'))

        # account
        rid = get_rid(input['account'])
        account = Account.objects.filter(id=rid.id).first()
        result['account'] = account
        if not account:
            raise Exception(_('Invalid Account ID!'))

    # Check business
    if 'business' in input:
        if input['business']:
            rid = get_rid(input['business'])
            business = Business.objects.get(id=rid.id)
            result['business'] = business
            if not business:
                raise Exception(_('Invalid Business ID!'))
        else:
            result['business'] = None

    return result


class CreateFinanceQuote(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        finance_quote_group = graphene.ID(required=True)
        business = graphene.ID(required=False)
        summary = graphene.String(required=False, default_value="")
        
    finance_quote = graphene.Field(FinanceQuoteNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financequote')

        validation_result = validate_create_update_input(input)
        finance_quote_group = validation_result['finance_quote_group']

        finance_quote = FinanceQuote(
            account=validation_result['account'],
            finance_quote_group=finance_quote_group,
            status='DRAFT',
            terms=finance_quote_group.terms,
            footer=finance_quote_group.footer
        )

        if 'summary' in input:
            finance_quote.summary = input['summary']

        # Save quote
        finance_quote.save()

        # Do this after an initial save to override the "invoice_to_business" field on an account, if set.
        if 'business' in validation_result:
            finance_quote.business = validation_result['business']
            finance_quote.set_relation_info()
            finance_quote.save()

        return CreateFinanceQuote(finance_quote=finance_quote)


class UpdateFinanceQuote(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        business = graphene.ID(required=False)
        summary = graphene.String(required=False)
        custom_to = graphene.Boolean(required=False)
        relation_company = graphene.String(required=False)
        relation_company_registration = graphene.String(required=False)
        relation_company_tax_registration = graphene.String(required=False)
        relation_contact_name = graphene.String(required=False)
        relation_address = graphene.String(required=False)
        relation_postcode = graphene.String(required=False)
        relation_city = graphene.String(required=False)
        relation_country = graphene.String(required=False)
        quote_number = graphene.String(required=False)
        date_sent = graphene.types.datetime.Date(required=False)
        date_expire = graphene.types.datetime.Date(required=False)
        status = graphene.String(required=False)
        terms = graphene.String(required=False)
        footer = graphene.String(required=False)
        note = graphene.String(required=False)

    finance_quote = graphene.Field(FinanceQuoteNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financequote')

        rid = get_rid(input['id'])
        finance_quote = FinanceQuote.objects.filter(id=rid.id).first()
        if not finance_quote:
            raise Exception('Invalid Finance Invoice  ID!')

        validation_result = validate_create_update_input(input, update=True)

        if 'business' in validation_result:
            finance_quote.business = validation_result['business']

        if 'summary' in input:
            finance_quote.summary = input['summary']

        if 'custom_to' in input:
            finance_quote.custom_to = input['custom_to']

        if 'relation_company' in input:
            finance_quote.relation_company = input['relation_company']

        if 'relation_company_registration' in input:
            finance_quote.relation_company_registration = input['relation_company_registration']

        if 'relation_company_tax_registration' in input:
            finance_quote.relation_company_tax_registration = input['relation_company_tax_registration']

        if 'relation_contact_name' in input:
            finance_quote.relation_contact_name = input['relation_contact_name']

        if 'relation_address' in input:
            finance_quote.relation_address = input['relation_address']

        if 'relation_postcode' in input:
            finance_quote.relation_postcode = input['relation_postcode']

        if 'relation_city' in input:
            finance_quote.relation_city = input['relation_city']

        if 'relation_country' in input:
            finance_quote.relation_country = input['relation_country']

        if 'quote_number' in input:
            finance_quote.quote_number = input['quote_number']

        if 'date_sent' in input:
            finance_quote.date_sent = input['date_sent']

        if 'date_expire' in input:
            finance_quote.date_expire = input['date_expire']

        if 'status' in input:
            finance_quote.status = input['status']

        if 'terms' in input:
            finance_quote.terms = input['terms']

        if 'footer' in input:
            finance_quote.footer = input['footer']

        if 'note' in input:
            finance_quote.note = input['note']

        # Applies custom relation address info only when customTo is set
        finance_quote.set_relation_info()
        finance_quote.save()

        return UpdateFinanceQuote(finance_quote=finance_quote)


class DeleteFinanceQuote(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    
    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financequote')

        rid = get_rid(input['id'])

        finance_quote = FinanceQuote.objects.filter(id=rid.id).first()
        if not finance_quote:
            raise Exception('Invalid Finance Invoice ID!')

        ok = bool(finance_quote.delete())

        return DeleteFinanceQuote(ok=ok)


class FinanceQuoteMutation(graphene.ObjectType):
    delete_finance_quote = DeleteFinanceQuote.Field()
    create_finance_quote = CreateFinanceQuote.Field()
    update_finance_quote = UpdateFinanceQuote.Field()
