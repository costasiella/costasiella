import os
import graphene
import validators

from django.utils.translation import gettext as _
from django.conf import settings
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, InsightAccountInactive
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..dudes.system_setting_dude import SystemSettingDude
from ..tasks import insight_account_inactive_delete_accounts, \
    insight_account_inactive_populate_accounts

m = Messages()


class InsightAccountInactiveNode(DjangoObjectType):
    class Meta:
        model = InsightAccountInactive
        # Fields to include
        fields = (
            'no_activity_after_date',
            'count_inactive_accounts',
            'count_deleted_inactive_accounts',
            'created_at',
            # Reverse relations
            'accounts'
        )
        filter_fields = ['id']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightaccountinactive')

        return self._meta.model.objects.get(id=id)


class InsightAccountInactiveQuery(graphene.ObjectType):
    insight_account_inactives = DjangoFilterConnectionField(InsightAccountInactiveNode)
    insight_account_inactive = graphene.relay.Node.Field(InsightAccountInactiveNode)

    def resolve_insight_account_inactives(self, info, **kwargs):
        """
        Return bank accounts for an account
        - Require login
        - Always return users' own info when no view_accountbank_account permission
        - Allow user to specify the account
        :param info:
        :param account:
        :param kwargs:
        :return:
        """
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_insightaccountinactive')

        # Allow user to specify account
        return InsightAccountInactive.objects.all().order_by("-created_at")


class CreateInsightAccountInactive(graphene.relay.ClientIDMutation):
    class Input:
        no_activity_after_date = graphene.types.datetime.Date(required=True)

    insight_account_inactive = graphene.Field(InsightAccountInactiveNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_insightaccountinactive')

        insight_account_inactive = InsightAccountInactive(
            no_activity_after_date=input['no_activity_after_date']
        )
        insight_account_inactive.save()

        # Call background task to add accounts to inactive on date list when we're not in CI test mode
        if 'GITHUB_WORKFLOW' not in os.environ and not getattr(settings, 'TESTING', False):
            task = insight_account_inactive_populate_accounts.delay(insight_account_inactive.id)

        return CreateInsightAccountInactive(insight_account_inactive=insight_account_inactive)


class DeleteInsightAccountInactive(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_insightaccountinactive')

        rid = get_rid(input['id'])
        insight_account_inactive = InsightAccountInactive.objects.get(id=rid.id)
        if not insight_account_inactive:
            raise Exception('Invalid Insight Account Inactive ID!')

        ok = bool(insight_account_inactive.delete())

        return DeleteInsightAccountInactive(ok=ok)


class DeleteInsightAccountInactiveAccounts(graphene.relay.ClientIDMutation):
    class Input:
        # InsightAccountInactive.id
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_insightaccountinactiveaccount')

        rid = get_rid(input['id'])
        insight_account_inactive = InsightAccountInactive.objects.get(id=rid.id)
        if not insight_account_inactive:
            raise Exception('Invalid Insight Account Inactive ID!')

        # Call background task to add accounts to inactive on date list when we're not in CI test mode
        if 'GITHUB_WORKFLOW' not in os.environ and not getattr(settings, 'TESTING', False):
            task = insight_account_inactive_delete_accounts.delay(insight_account_inactive.id)

        # Always return ok as the actual removal of inactive accounts is handled by a bg task
        return DeleteInsightAccountInactiveAccounts(ok=True)


class InsightAccountInactiveMutation(graphene.ObjectType):
    create_insight_account_inactive = CreateInsightAccountInactive.Field()
    delete_insight_account_inactive = DeleteInsightAccountInactive.Field()
    delete_insight_account_inactive_accounts = DeleteInsightAccountInactiveAccounts.Field()
