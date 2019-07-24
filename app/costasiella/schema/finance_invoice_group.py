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
    finance_invoice_groups = DjangoFilterConnectionField(FinanceInvoiceGroupNode)
    finance_invoice_group = graphene.relay.Node.Field(FinanceInvoiceGroupNode)

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

    finance_invoice_group = graphene.Field(FinanceInvoiceGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_financeinvoicegroup')

        errors = []
        if not len(input['name']):
            print('validation error found')
            raise GraphQLError(_('Name is required'))

        finance_invoice_group = FinanceInvoiceGroup(
            name=input['name'], 
        )

        if input['due_after_days']:
            finance_invoice_group.due_after_days = input['due_after_days']

        if input['prefix']:
            finance_invoice_group.prefix = input['prefix']

        if input['prefix_year']:
            finance_invoice_group.prefix_year = input['prefix_year']

        if input['auto_reset_prefix_year']:
            finance_invoice_group.auto_reset_prefix_year = input['auto_reset_prefix_year']

        if input['terms']:
            finance_invoice_group.terms = input['terms']

        if input['footer']:
            finance_invoice_group.footer = input['footer']

        if input['code']:
            finance_invoice_group.code = input['code']

        finance_invoice_group.save()

        return CreateFinanceInvoiceGroup(finance_invoice_group=finance_invoice_group)


class UpdateFinanceInvoiceGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        display_public = graphene.Boolean(required=False, default_value=True)
        name = graphene.String(required=True)
        next_id = graphene.Integer(required=False)
        due_after_days = graphene.Integer(required=False, default_value=30)
        prefix = graphene.String(required=False, default_value="")
        prefix_year = graphene.Boolean(required=False, default_value=True)
        auto_reset_prefix_year = graphene.Boolean(required=False, default_value=True)
        terms = graphene.String(required=False, default_value="")
        footer = graphene.String(required=False, default_value="")
        code = graphene.String(required=False, default_value="")
        
    finance_invoice_group = graphene.Field(FinanceInvoiceGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeinvoicegroup')

        rid = get_rid(input['id'])

        finance_invoice_group = FinanceInvoiceGroup.objects.filter(id=rid.id).first()
        if not finance_invoice_group:
            raise Exception('Invalid Finance Invoice Group ID!')

        finance_invoice_group.name = input['name']

        if input['next_id']:
            finance_invoice_group.due_after_days = input['next_id']

        if input['due_after_days']:
            finance_invoice_group.due_after_days = input['due_after_days']

        if input['prefix']:
            finance_invoice_group.prefix = input['prefix']

        if input['prefix_year']:
            finance_invoice_group.prefix_year = input['prefix_year']

        if input['auto_reset_prefix_year']:
            finance_invoice_group.auto_reset_prefix_year = input['auto_reset_prefix_year']

        if input['terms']:
            finance_invoice_group.terms = input['terms']

        if input['footer']:
            finance_invoice_group.footer = input['footer']

        if input['code']:
            finance_invoice_group.code = input['code']

        finance_invoice_group.save()

        return UpdateFinanceInvoiceGroup(finance_invoice_group=finance_invoice_group)


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
            raise Exception('Invalid Finance Invoice Group ID!')

        finance_invoicegroup.archived = input['archived']
        finance_invoicegroup.save(force_update=True)

        return ArchiveFinanceInvoiceGroup(finance_invoicegroup=finance_invoicegroup)


class FinanceInvoiceGroupMutation(graphene.ObjectType):
    archive_finance_invoicegroup = ArchiveFinanceInvoiceGroup.Field()
    create_finance_invoicegroup = CreateFinanceInvoiceGroup.Field()
    update_finance_invoicegroup = UpdateFinanceInvoiceGroup.Field()