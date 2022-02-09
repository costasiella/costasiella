from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import FinanceInvoiceGroup, FinanceInvoiceGroupDefault
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class FinanceInvoiceGroupDefaultNode(DjangoObjectType):
    class Meta:
        model = FinanceInvoiceGroupDefault
        fields = (
            'item_type',
            'finance_invoice_group'
        )
        filter_fields = []
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeinvoicegroupdefault')

        return self._meta.model.objects.get(id=id)


class FinanceInvoiceGroupDefaultQuery(graphene.ObjectType):
    finance_invoice_group_defaults = DjangoFilterConnectionField(FinanceInvoiceGroupDefaultNode)
    finance_invoice_group_default = graphene.relay.Node.Field(FinanceInvoiceGroupDefaultNode)

    def resolve_finance_invoice_group_defaults(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_financeinvoicegroupdefault')

        return FinanceInvoiceGroupDefault.objects.all().order_by('pk')


class UpdateFinanceInvoiceGroupDefault(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        finance_invoice_group = graphene.ID(required=True)
        
    finance_invoice_group_default = graphene.Field(FinanceInvoiceGroupDefaultNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_financeinvoicegroupdefault')

        rid = get_rid(input['id'])
        finance_invoice_group_default = FinanceInvoiceGroupDefault.objects.filter(id=rid.id).first()
        if not finance_invoice_group_default:
            raise Exception('Invalid Finance Invoice Group Default ID!')

        rid = get_rid(input['finance_invoice_group'])
        finance_invoice_group = FinanceInvoiceGroup.objects.filter(id=rid.id).first()
        if not finance_invoice_group:
            raise Exception('Invalid Finance Invoice Group ID!')

        finance_invoice_group_default.finance_invoice_group = finance_invoice_group
        finance_invoice_group_default.save()

        return UpdateFinanceInvoiceGroupDefault(finance_invoice_group_default=finance_invoice_group_default)


class FinanceInvoiceGroupDefaultMutation(graphene.ObjectType):
    update_finance_invoice_group_default = UpdateFinanceInvoiceGroupDefault.Field()