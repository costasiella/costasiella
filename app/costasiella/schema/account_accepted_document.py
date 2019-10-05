from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import Account, AccountClasspass, FinancePaymentMethod, OrganizationClasspass
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..dudes.sales_dude import SalesDude

from sorl.thumbnail import get_thumbnail

m = Messages()


class AccountAcceptedDocumentNode(DjangoObjectType):   
    class Meta:
        model = AccountClasspass
        filter_fields = ['account', 'date_start', 'date_end']
        interfaces = (graphene.relay.Node, )


    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountaccepteddocument')

        return self._meta.model.objects.get(id=id)


class AccountAcceptedDocumentQuery(graphene.ObjectType):
    account_accepted_documents = DjangoFilterConnectionField(AccountAcceptedDocumentNode)
    account_accepted_document = graphene.relay.Node.Field(AccountAcceptedDocumentNode)


    def resolve_account_accepted_documents(self, info, account, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountaccepteddocument')

        rid = get_rid(account)
        return AccountClasspass.objects.filter(account=rid.id).order_by('date_start')

