from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import FinanceQuoteGroup
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class FinanceQuoteGroupNode(DjangoObjectType):
    class Meta:
        model = FinanceQuoteGroup
        fields = (
            'archived',
            'display_public',
            'name',
            'next_id',
            'expires_after_days',
            'prefix',
            'prefix_year',
            'auto_reset_prefix_year',
            'terms',
            'footer',
            'code'
        )
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login(user)

        finance_quote_group = self._meta.model.objects.get(id=id)
        # When user has a quote that have the quote group return it, otherwise require permission
        if user.quotes.filter(finance_quote_group=finance_quote_group).exists():
            return finance_quote_group
        else:
            require_login_and_permission(user, 'costasiella.view_financequotegroup')

        return finance_quote_group

class FinanceQuoteGroupQuery(graphene.ObjectType):
    finance_quote_groups = DjangoFilterConnectionField(FinanceQuoteGroupNode)
    finance_quote_group = graphene.relay.Node.Field(FinanceQuoteGroupNode)

    def resolve_finance_quote_groups(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financequotegroup')

        return FinanceQuoteGroup.objects.filter(archived=archived).order_by('name')


class CreateFinanceQuoteGroup(graphene.relay.ClientIDMutation):
    class Input:
        display_public = graphene.Boolean(required=False, default_value=True)
        name = graphene.String(required=True)
        expires_after_days = graphene.Int(required=False, default_value=30)
        prefix = graphene.String(required=False, default_value="QUO")
        prefix_year = graphene.Boolean(required=False, default_value=True)
        auto_reset_prefix_year = graphene.Boolean(required=False, default_value=True)
        terms = graphene.String(required=False, default_value="")
        footer = graphene.String(required=False, default_value="")
        code = graphene.String(required=False, default_value="")

    finance_quote_group = graphene.Field(FinanceQuoteGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financequotegroup')

        errors = []
        if not len(input['name']):
            raise GraphQLError(_('Name is required'))

        finance_quote_group = FinanceQuoteGroup(
            name=input['name'], 
            next_id=1,
        )

        if 'expires_after_days' in input:
            finance_quote_group.expires_after_days = input['expires_after_days']

        if 'prefix' in input:
            finance_quote_group.prefix = input['prefix']

        if 'prefix_year' in input:
            finance_quote_group.prefix_year = input['prefix_year']

        if 'auto_reset_prefix_year' in input:
            finance_quote_group.auto_reset_prefix_year = input['auto_reset_prefix_year']

        if 'terms' in input:
            finance_quote_group.terms = input['terms']

        if 'footer' in input:
            finance_quote_group.footer = input['footer']

        if 'code' in input:
            finance_quote_group.code = input['code']

        finance_quote_group.save()

        return CreateFinanceQuoteGroup(finance_quote_group=finance_quote_group)


class UpdateFinanceQuoteGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        display_public = graphene.Boolean(required=False)
        name = graphene.String(required=True)
        next_id = graphene.Int(required=False)
        expires_after_days = graphene.Int(required=False)
        prefix = graphene.String(required=False)
        prefix_year = graphene.Boolean(required=False)
        auto_reset_prefix_year = graphene.Boolean(required=False)
        terms = graphene.String(required=False)
        footer = graphene.String(required=False)
        code = graphene.String(required=False, default_value="")
        
    finance_quote_group = graphene.Field(FinanceQuoteGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financequotegroup')

        rid = get_rid(input['id'])

        finance_quote_group = FinanceQuoteGroup.objects.filter(id=rid.id).first()
        if not finance_quote_group:
            raise Exception('Invalid Finance Quote Group ID!')

        finance_quote_group.name = input['name']

        if 'next_id' in input:
            finance_quote_group.next_id = input['next_id']

        if 'expires_after_days' in input:
            finance_quote_group.expires_after_days = input['expires_after_days']

        if 'prefix' in input:
            finance_quote_group.prefix = input['prefix']

        if 'prefix_year' in input:
            finance_quote_group.prefix_year = input['prefix_year']

        if 'auto_reset_prefix_year' in input:
            finance_quote_group.auto_reset_prefix_year = input['auto_reset_prefix_year']

        if 'terms' in input:
            finance_quote_group.terms = input['terms']

        if 'footer' in input:
            finance_quote_group.footer = input['footer']

        if 'code' in input:
            finance_quote_group.code = input['code']

        finance_quote_group.save()

        return UpdateFinanceQuoteGroup(finance_quote_group=finance_quote_group)


class ArchiveFinanceQuoteGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    finance_quote_group = graphene.Field(FinanceQuoteGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financequotegroup')

        rid = get_rid(input['id'])

        finance_quote_group = FinanceQuoteGroup.objects.filter(id=rid.id).first()
        if not finance_quote_group:
            raise Exception('Invalid Finance Quote Group ID!')

        finance_quote_group.archived = input['archived']
        finance_quote_group.save()

        return ArchiveFinanceQuoteGroup(finance_quote_group=finance_quote_group)


class FinanceQuoteGroupMutation(graphene.ObjectType):
    archive_finance_quote_group = ArchiveFinanceQuoteGroup.Field()
    create_finance_quote_group = CreateFinanceQuoteGroup.Field()
    update_finance_quote_group = UpdateFinanceQuoteGroup.Field()
