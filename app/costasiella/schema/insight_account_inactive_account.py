import graphene

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from ..models import InsightAccountInactiveAccount
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class InsightAccountInactiveAccountNode(DjangoObjectType):
    class Meta:
        model = InsightAccountInactiveAccount
        # Fields to include
        fields = (
            'account',
            'insight_account_inactive',
            'created_at'
        )
        filter_fields = ['id']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightaccountinactive')

        return self._meta.model.objects.get(id=id)


class InsightAccountInactiveAccountQuery(graphene.ObjectType):
    insight_account_inactive_accounts = DjangoFilterConnectionField(InsightAccountInactiveAccountNode)
    insight_account_inactive_account = graphene.relay.Node.Field(InsightAccountInactiveAccountNode)

    def resolve_insight_account_inactive_accounts(self, info, **kwargs):
        """
        Resolve accounts for insight account inactive
        """
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightaccountinactive')

        # Allow user to specify account
        return InsightAccountInactiveAccount.objects.all().order_by("created_at")
