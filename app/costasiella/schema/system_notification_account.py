from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, SystemNotification, SystemNotificationAccount
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class SystemNotificationAccountNode(DjangoObjectType):
    class Meta:
        model = SystemNotificationAccount
        fields = (
            'account',
            'system_notification',
        )
        filter_fields = {
            'id': ['exact'],
            'system_notification': ['exact'],
        }
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(cls, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_systemnotificationaccount')

        return cls._meta.model.objects.get(id=id)


class SystemNotificationAccountQuery(graphene.ObjectType):
    system_notification_accounts = DjangoFilterConnectionField(SystemNotificationAccountNode)
    system_notification_account = graphene.relay.Node.Field(SystemNotificationAccountNode)

    @staticmethod
    def resolve_system_notification_accounts(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_systemnotificationaccount')

        # rid = get_rid()
        # return everything:
        return SystemNotificationAccount.objects.all().order_by('system_notification')

def validate_create_delete_input(input):
    """
    Validate input
    """
    result = {}

    # Check account
    if 'account' in input:
        if input['account']:
            rid = get_rid(input['account'])
            account = Account.objects.filter(id=rid.id).first()
            result['account'] = account
            if not account:
                raise Exception(_('Invalid Account ID!'))

    # Check account
    if 'system_notification' in input:
        if input['system_notification']:
            rid = get_rid(input['system_notification'])
            system_notification = SystemNotification.objects.filter(id=rid.id).first()
            result['system_notification'] = system_notification
            if not system_notification:
                raise Exception(_('Invalid System Notification ID!'))

    return result


class CreateSystemNotificationAccount(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID()
        system_notification = graphene.ID()

    system_notification_account = graphene.Field(SystemNotificationAccountNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_systemnotificationaccount')

        result = validate_create_delete_input(input)
        system_notification_account = SystemNotificationAccount(
            account=result['account'],
            system_notification=result['system_notification']
        )
        system_notification_account.save()

        return CreateSystemNotificationAccount(system_notification_account=system_notification_account)


class DeleteSystemNotificationAccount(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=False)
        account = graphene.ID(required=False)
        system_notification = graphene.ID(required=False)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_systemnotificationaccount')

        result = validate_create_delete_input(input)

        if 'id' in input:
            rid = get_rid(input['id'])
            system_notification_account = SystemNotificationAccount.objects.filter(id=rid.id).first()
            if not system_notification_account:
                raise Exception('Invalid System Notification Account ID!')

            ok = bool(system_notification_account.delete())
        elif 'account' and 'system_notification' in result:
            qs = SystemNotificationAccount.objects.filter(
                account=result['account'],
                system_notification=result['system_notification']
            )

            ok = bool(qs.delete())
        else:
            raise Exception("Either id or account and systemNotification need to be specified")

        return DeleteSystemNotificationAccount(ok=ok)


class SystemNotificationAccountMutation(graphene.ObjectType):
    create_system_notification_account = CreateSystemNotificationAccount.Field()
    delete_system_notification_account = DeleteSystemNotificationAccount.Field()
