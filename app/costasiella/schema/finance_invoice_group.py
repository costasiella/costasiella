from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import FinanceInvoiceGroup
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class FinanceInvoiceGroupNode(DjangoObjectType):
    class Meta:
        model = FinanceInvoiceGroup
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeinvoicegroup')

        return self._meta.model.objects.get(id=id)


class FinanceInvoiceGroupQuery(graphene.ObjectType):
    finance_invoicegroups = DjangoFilterConnectionField(FinanceInvoiceGroupNode)
    finance_invoicegroup = graphene.relay.Node.Field(FinanceInvoiceGroupNode)

    def resolve_finance_invoicegroups(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeinvoicegroup')

        return FinanceInvoiceGroup.objects.filter(archived = archived).order_by('name')


class CreateFinanceInvoiceGroup(graphene.relay.ClientIDMutation):
    class Input:
        display_public = graphene.Boolean(required=False, default_value=True)
        name = graphene.String(required=True)
        due_after_days = graphene.Integer(required=False, default_value=30)
        prefix = graphene.String(required=False, default_value="")
        prefix_year = graphene.Boolean(required=False, default_value=True)
        auto_reset_prefix_year = graphene.Boolean(required=False, default_value=True)
        terms = graphene.String(required=False, default_value="")
        footer = graphene.String(required=False, default_value="")
        code = graphene.String(required=False, default_value="")

    finance_invoicegroup = graphene.Field(FinanceInvoiceGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeinvoicegroup')

        errors = []
        if not len(input['name']):
            print('validation error found')
            raise GraphQLError(_('Name is required'))

        finance_invoicegroup = FinanceInvoiceGroup(
            name=input['name'], 
        )

        if input['due_after_days']:
            finance_invoicegroup.due_after_days = input['due_after_days']

        if input['prefix']:
            finance_invoicegroup.prefix = input['prefix']

        if input['prefix_year']:
            finance_invoicegroup.prefix_year = input['prefix_year']

        if input['auto_reset_prefix_year']:
            finance_invoicegroup.auto_reset_prefix_year = input['auto_reset_prefix_year']

        if input['terms']:
            finance_invoicegroup.terms = input['terms']

        if input['footer']:
            finance_invoicegroup.footer = input['footer']

        if input['code']:
            finance_invoicegroup.code = input['code']

        finance_invoicegroup.save()

        return CreateFinanceInvoiceGroup(finance_invoicegroup=finance_invoicegroup)


class UpdateFinanceInvoiceGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        code = graphene.String(default_value="")
        
    finance_invoicegroup = graphene.Field(FinanceInvoiceGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeinvoicegroup')

        rid = get_rid(input['id'])

        finance_invoicegroup = FinanceInvoiceGroup.objects.filter(id=rid.id).first()
        if not finance_invoicegroup:
            raise Exception('Invalid Finance Costcenter ID!')

        finance_invoicegroup.name = input['name']
        if input['code']:
            finance_invoicegroup.code = input['code']
        finance_invoicegroup.save(force_update=True)

        return UpdateFinanceInvoiceGroup(finance_invoicegroup=finance_invoicegroup)


class ArchiveFinanceInvoiceGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    finance_invoicegroup = graphene.Field(FinanceInvoiceGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_financeinvoicegroup')

        rid = get_rid(input['id'])

        finance_invoicegroup = FinanceInvoiceGroup.objects.filter(id=rid.id).first()
        if not finance_invoicegroup:
            raise Exception('Invalid Finance Costcenter ID!')

        finance_invoicegroup.archived = input['archived']
        finance_invoicegroup.save(force_update=True)

        return ArchiveFinanceInvoiceGroup(finance_invoicegroup=finance_invoicegroup)


class FinanceInvoiceGroupMutation(graphene.ObjectType):
    archive_finance_invoicegroup = ArchiveFinanceInvoiceGroup.Field()
    create_finance_invoicegroup = CreateFinanceInvoiceGroup.Field()
    update_finance_invoicegroup = UpdateFinanceInvoiceGroup.Field()