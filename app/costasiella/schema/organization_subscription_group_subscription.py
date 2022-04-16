from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationSubscription, OrganizationSubscriptionGroup, OrganizationSubscriptionGroupSubscription
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationSubscriptionGroupSubscriptionNode(DjangoObjectType):
    class Meta:
        model = OrganizationSubscriptionGroupSubscription
        fields = (
            'organization_subscription_group',
            'organization_subscription'
        )
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationsubscriptiongroupsubscription')

        return self._meta.model.objects.get(id=id)


class CreateOrganizationSubscriptionGroupSubscription(graphene.relay.ClientIDMutation):
    class Input:
        organization_subscription_group = graphene.ID(required=True)
        organization_subscription = graphene.ID(required=True)

    organization_subscription_group_subscription = graphene.Field(OrganizationSubscriptionGroupSubscriptionNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationsubscriptiongroupsubscription')

        rid_group = get_rid(input['organization_subscription_group'])
        rid_pass = get_rid(input['organization_subscription'])

        organization_subscription_group = OrganizationSubscriptionGroup.objects.get(pk=rid_group.id)
        organization_subscription = OrganizationSubscription.objects.get(pk=rid_pass.id)

        query_set = OrganizationSubscriptionGroupSubscription.objects.filter(
            organization_subscription_group = organization_subscription_group,
            organization_subscription = organization_subscription
        )

        # Don't insert duplicate records in the DB. If this records exist, fetch and return it
        if not query_set.exists():
            organization_subscription_group_subscription = OrganizationSubscriptionGroupSubscription(
                organization_subscription_group = organization_subscription_group,
                organization_subscription = organization_subscription
            )

            organization_subscription_group_subscription.save()
        else:
            organization_subscription_group_subscription = query_set.first()

        return CreateOrganizationSubscriptionGroupSubscription(organization_subscription_group_subscription=organization_subscription_group_subscription)


class DeleteOrganizationSubscriptionGroupSubscription(graphene.relay.ClientIDMutation):
    class Input:
        # id = graphene.ID(required=True)
        organization_subscription_group = graphene.ID(required=True)
        organization_subscription = graphene.ID(required=True)

    ok = graphene.Boolean()
    deleted_organization_subscription_group_subscription_id = graphene.ID()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationsubscriptiongroupsubscription')

        # rid = get_rid(input['id'])
        rid_group = get_rid(input['organization_subscription_group'])
        rid_pass = get_rid(input['organization_subscription'])

        organization_subscription_group = OrganizationSubscriptionGroup.objects.get(pk=rid_group.id)
        organization_subscription = OrganizationSubscription.objects.get(pk=rid_pass.id)

        organization_subscription_group_subscription = OrganizationSubscriptionGroupSubscription.objects.filter(
            organization_subscription_group = organization_subscription_group,
            organization_subscription = organization_subscription
        ).first()

        ok = bool(organization_subscription_group_subscription.delete())

        return DeleteOrganizationSubscriptionGroupSubscription(
            ok=ok
        )


class OrganizationSubscriptionGroupSubscriptionMutation(graphene.ObjectType):
    create_organization_subscription_group_subscription = CreateOrganizationSubscriptionGroupSubscription.Field()
    delete_organization_subscription_group_subscription = DeleteOrganizationSubscriptionGroupSubscription.Field()