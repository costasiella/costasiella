from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationSubscriptionGroup
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..modules.model_helpers.organization_subscription_group_helper import OrganizationSubscriptionGroupHelper

m = Messages()


class OrganizationSubscriptionGroupNode(DjangoObjectType):
    class Meta:
        model = OrganizationSubscriptionGroup
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationsubscriptiongroup')

        return self._meta.model.objects.get(id=id)


class OrganizationSubscriptionGroupQuery(graphene.ObjectType):
    organization_subscription_groups = DjangoFilterConnectionField(OrganizationSubscriptionGroupNode)
    organization_subscription_group = graphene.relay.Node.Field(OrganizationSubscriptionGroupNode)

    def resolve_organization_subscription_groups(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationsubscriptiongroup')

        ## return everything:
        return OrganizationSubscriptionGroup.objects.filter(archived = archived).order_by('name')


class CreateOrganizationSubscriptionGroup(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    organization_subscription_group = graphene.Field(OrganizationSubscriptionGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationsubscriptiongroup')

        errors = []
        if not len(input['name']):
            print('validation error found')
            raise GraphQLError(_('Name is required'))

        organization_subscription_group = OrganizationSubscriptionGroup(
            name=input['name'], 
        )

        organization_subscription_group.save()
        helper = OrganizationSubscriptionGroupHelper()
        helper.add_to_all_classes(organization_subscription_group.id)

        return CreateOrganizationSubscriptionGroup(organization_subscription_group=organization_subscription_group)


class UpdateOrganizationSubscriptionGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        
    organization_subscription_group = graphene.Field(OrganizationSubscriptionGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationsubscriptiongroup')

        rid = get_rid(input['id'])

        organization_subscription_group = OrganizationSubscriptionGroup.objects.filter(id=rid.id).first()
        if not organization_subscription_group:
            raise Exception('Invalid Organization Subscription Group ID!')

        organization_subscription_group.name = input['name']
        organization_subscription_group.save(force_update=True)

        return UpdateOrganizationSubscriptionGroup(organization_subscription_group=organization_subscription_group)


class ArchiveOrganizationSubscriptionGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_subscription_group = graphene.Field(OrganizationSubscriptionGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationsubscriptiongroup')

        rid = get_rid(input['id'])

        organization_subscription_group = OrganizationSubscriptionGroup.objects.filter(id=rid.id).first()
        if not organization_subscription_group:
            raise Exception('Invalid Organization Subscription Group ID!')

        organization_subscription_group.archived = input['archived']
        organization_subscription_group.save(force_update=True)

        return ArchiveOrganizationSubscriptionGroup(organization_subscription_group=organization_subscription_group)


class OrganizationSubscriptionGroupMutation(graphene.ObjectType):
    archive_organization_subscription_group = ArchiveOrganizationSubscriptionGroup.Field()
    create_organization_subscription_group = CreateOrganizationSubscriptionGroup.Field()
    update_organization_subscription_group = UpdateOrganizationSubscriptionGroup.Field()