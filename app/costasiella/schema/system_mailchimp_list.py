from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..dudes import IntegrationMailChimpDude
from ..models import SystemMailChimpList
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class SystemMailChimpListNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    subscribed = graphene.Boolean()


class SystemMailChimpListNode(DjangoObjectType):
    class Meta:
        model = SystemMailChimpList
        fields = (
            'name',
            'description',
            'frequency',
            'mailchimp_list_id'
        )
        filter_fields = ['id']
        interfaces = (graphene.relay.Node, SystemMailChimpListNodeInterface,)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login(user)
        # require_login_and_permission(user, 'costasiella.view_systemmailchimplist')

        return self._meta.model.objects.get(id=id)

    def resolve_subscribed(self, info):
        user = info.context.user
        require_login(user)

        mailchimp_dude = IntegrationMailChimpDude()
        result = mailchimp_dude.get_account_subscribed_to_list(
            self.mailchimp_list_id,
            user
        )

        subscribed = False
        if not result['error']:
            if result['subscription_status'] == 'subscribed':
                subscribed = True

        return subscribed


class SystemMailChimpListQuery(graphene.ObjectType):
    system_mailchimp_lists = DjangoFilterConnectionField(SystemMailChimpListNode)
    system_mailchimp_list = graphene.relay.Node.Field(SystemMailChimpListNode)

    def resolve_system_mailchimp_lists(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login(user)
        # require_login_and_permission(user, 'costasiella.view_systemmailchimplist')

        return SystemMailChimpList.objects.order_by('name')


class CreateSystemMailChimpList(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        description = graphene.String(required=True)
        frequency = graphene.String(required=True)
        mailchimp_list_id = graphene.String(required=True)

    system_mailchimp_list = graphene.Field(SystemMailChimpListNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_systemmailchimplist')

        system_mailchimp_list = SystemMailChimpList(
            name=input['name'], 
            description=input['description'],
            frequency=input['frequency'],
            mailchimp_list_id=input['mailchimp_list_id']
        )

        system_mailchimp_list.save()

        return CreateSystemMailChimpList(system_mailchimp_list=system_mailchimp_list)


class UpdateSystemMailChimpList(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)
        frequency = graphene.String(required=False)
        mailchimp_list_id = graphene.String(required=False)
        
    system_mailchimp_list = graphene.Field(SystemMailChimpListNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_systemmailchimplist')

        rid = get_rid(input['id'])

        system_mailchimp_list = SystemMailChimpList.objects.filter(id=rid.id).first()
        if not system_mailchimp_list:
            raise Exception('Invalid System MailChimp List ID!')

        if 'name' in input:
            system_mailchimp_list.name = input['name']

        if 'description' in input:
            system_mailchimp_list.description = input['description']

        if 'frequency' in input:
            system_mailchimp_list.frequency = input['frequency']

        if 'mailchimp_list_id' in input:
            system_mailchimp_list.mailchimp_list_id = input['mailchimp_list_id']

        system_mailchimp_list.save()

        return UpdateSystemMailChimpList(system_mailchimp_list=system_mailchimp_list)


class UpdateSystemMailChimpListSubscriptionStatus(graphene.relay.ClientIDMutation):
    class Input:
        mailchimp_list_id = graphene.String(required=True)

    subscription_status = graphene.String()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login(user)

        from ..dudes import IntegrationMailChimpDude

        mailchimp_dude = IntegrationMailChimpDude()
        mailchimp_list_id = input['mailchimp_list_id']

        result = mailchimp_dude.get_account_subscribed_to_list(
            mailchimp_list_id,
            user
        )

        subscription_status = result['subscription_status']
        if subscription_status == 'subscribed':
            result = mailchimp_dude.list_member_unsubscribe(mailchimp_list_id, user)
        else:
            result = mailchimp_dude.list_member_subscribe(mailchimp_list_id, user)

        # Refresh status before returning it
        result = mailchimp_dude.get_account_subscribed_to_list(
            mailchimp_list_id,
            user
        )

        subscription_status = result['subscription_status']

        return UpdateSystemMailChimpListSubscriptionStatus(subscription_status=subscription_status)


class DeleteSystemMailChimpList(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_systemmailchimplist')

        rid = get_rid(input['id'])
        system_mailchimp_list = SystemMailChimpList.objects.filter(id=rid.id).first()
        if not system_mailchimp_list:
            raise Exception('Invalid Organization Discovery ID!')

        ok = bool(system_mailchimp_list.delete())

        return DeleteSystemMailChimpList(ok=ok)


class SystemMailChimpListMutation(graphene.ObjectType):
    delete_system_mailchimp_list = DeleteSystemMailChimpList.Field()
    create_system_mailchimp_list = CreateSystemMailChimpList.Field()
    update_system_mailchimp_list = UpdateSystemMailChimpList.Field()
    update_system_mailchimp_list_subscription_status = UpdateSystemMailChimpListSubscriptionStatus.Field()
