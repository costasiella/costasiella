from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import AccountSubscription, AccountSubscriptionBlock
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail

m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    if input['date_start'] > input['date_end']:
        raise Exception(_("End date should be bigger than start date"))

    # Fetch & check account subscription
    if not update:
        rid = get_rid(input['account_subscription'])
        account_subscription = AccountSubscription.objects.get(pk=rid.id)
        result['account_subscription'] = account_subscription
        if not account_subscription:
            raise Exception(_('Invalid Account Subscription ID!'))

    return result


class AccountSubscriptionBlockNode(DjangoObjectType):
    class Meta:
        model = AccountSubscriptionBlock
        # Fields to include
        fields = (
            'account_subscription',
            'date_start',
            'date_end',
            'description',
            'created_at',
            'updated_at'
        )
        filter_fields = {
            'account_subscription': ['exact'],
        }
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountsubscriptionblock')

        return self._meta.model.objects.get(id=id)


class AccountSubscriptionBlockQuery(graphene.ObjectType):
    account_subscription_blocks = DjangoFilterConnectionField(AccountSubscriptionBlockNode)
    account_subscription_block = graphene.relay.Node.Field(AccountSubscriptionBlockNode)

    def resolve_account_subscription_blocks(self, info, account_subscription, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountsubscriptionblock')
        rid = get_rid(account_subscription)

        # return everything:
        return AccountSubscriptionBlock.objects.filter(account_subscription__id=rid.id).order_by('-date_start')


class CreateAccountSubscriptionBlock(graphene.relay.ClientIDMutation):
    class Input:
        account_subscription = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=True)
        description = graphene.String(required=False, default_value="")

    account_subscription_block = graphene.Field(AccountSubscriptionBlockNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountsubscriptionblock')

        # Validate input
        result = validate_create_update_input(input, update=False)

        account_subscription_block = AccountSubscriptionBlock(
            account_subscription=result['account_subscription'],
            date_start=input['date_start'],
            date_end=input['date_end'],
            description=input['description']
        )

        account_subscription_block.save()

        return CreateAccountSubscriptionBlock(account_subscription_block=account_subscription_block)


class UpdateAccountSubscriptionBlock(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=True)
        description = graphene.String(required=False, default_value="")
        
    account_subscription_block = graphene.Field(AccountSubscriptionBlockNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountsubscriptionblock')

        rid = get_rid(input['id'])
        account_subscription_block = AccountSubscriptionBlock.objects.filter(id=rid.id).first()
        if not account_subscription_block:
            raise Exception('Invalid Account Subscription Block ID!')

        result = validate_create_update_input(input, update=True)

        account_subscription_block.date_start = input['date_start']
        account_subscription_block.date_end = input['date_end']
        account_subscription_block.description = input['description']

        account_subscription_block.save()

        return UpdateAccountSubscriptionBlock(account_subscription_block=account_subscription_block)


class DeleteAccountSubscriptionBlock(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountsubscriptionblock')

        rid = get_rid(input['id'])
        account_subscription_block = AccountSubscriptionBlock.objects.filter(id=rid.id).first()
        if not account_subscription_block:
            raise Exception('Invalid Account Subscription Block ID!')

        ok = bool(account_subscription_block.delete())

        return DeleteAccountSubscriptionBlock(ok=ok)


class AccountSubscriptionBlockMutation(graphene.ObjectType):
    create_account_subscription_block = CreateAccountSubscriptionBlock.Field()
    delete_account_subscription_block = DeleteAccountSubscriptionBlock.Field()
    update_account_subscription_block = UpdateAccountSubscriptionBlock.Field()
