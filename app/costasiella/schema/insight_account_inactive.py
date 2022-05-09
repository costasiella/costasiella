import graphene
import validators

from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, InsightAccountInactive
from ..modules.gql_tools import require_login, require_login_and_permission, require_permission, get_rid
from ..modules.messages import Messages
from ..dudes.system_setting_dude import SystemSettingDude

m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Fetch & check account
    if not update:
        # Create only
        rid = get_rid(input['account'])
        account = Account.objects.filter(id=rid.id).first()
        result['account'] = account
        if not account:
            raise Exception(_('Invalid Account ID!'))

    if 'number' in input:
        system_setting_dude = SystemSettingDude()
        finance_bank_accounts_iban = system_setting_dude.get('finance_bank_accounts_iban')

        if finance_bank_accounts_iban == 'true':
            number = input['number'].strip()
            if not validators.iban(number):
                raise Exception(_('Number is not a valid IBAN!'))

    return result


class InsightAccountInactiveNode(DjangoObjectType):
    class Meta:
        model = InsightAccountInactive
        # Fields to include
        fields = (
            'date_no_activity_after'
            'created_at',
        )
        # filter_fields = ['account']
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
        return InsightAccountInactive.objects.all(order_by="created_at")


class CreateInsightAccountInactive(graphene.relay.ClientIDMutation):
    class Input:
        no_activity_after_date = graphene.graphene.types.datetime.Date(required=True)

    insight_account_inactive = graphene.Field(InsightAccountInactiveNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_insightaccountinactive')

        insight_account_inactive = InsightAccountInactive(
            no_activity_after_date=input['no_activity_after_date']
        )
        insight_account_inactive.save()

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
        insight_account_inactive = InsightAccountInactive.objects.filter(id=rid.id).first()
        if not insight_account_inactive:
            raise Exception('Invalid Insight Account Inactive ID!')

        ok = bool(insight_account_inactive.delete())

        return DeleteInsightAccountInactive(ok=ok)


class InsightAccountInactiveMutation(graphene.ObjectType):
    create_insight_account_inactive = CreateInsightAccountInactive.Field()
    delete_insight_account_inactive = DeleteInsightAccountInactive.Field()
