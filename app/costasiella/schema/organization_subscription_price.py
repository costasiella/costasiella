from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationSubscription, OrganizationSubscriptionPrice
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()

class OrganizationSubscriptionPriceNode(DjangoObjectType):
    class Meta:
        model = OrganizationSubscriptionPrice
        filter_fields = ['archived', 'organization_subscription']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationsubscriptionprice')

        return self._meta.model.objects.get(id=id)


class OrganizationSubscriptionPriceQuery(graphene.ObjectType):
    organization_subscription_rooms = DjangoFilterConnectionField(OrganizationSubscriptionPriceNode)
    organization_subscription_room = graphene.relay.Node.Field(OrganizationSubscriptionPriceNode)

    def resolve_organization_subscription_rooms(self, info, organization_subscription, archived=False, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception(m.user_not_logged_in)

        rid = get_rid(organization_subscription)

        ## return everything:
        if user.has_perm('costasiella.view_organizationsubscriptionprice'):
            return OrganizationSubscriptionPrice.objects.filter(organization_subscription = rid.id, archived = archived).order_by('name')

        # Return only public non-archived prices
        return OrganizationSubscriptionPrice.objects.filter(organization_subscription = rid.id, display_public = True, archived = False).order_by('name')


class CreateOrganizationSubscriptionPrice(graphene.relay.ClientIDMutation):
    class Input:
        organization_subscription = graphene.ID(required=True)
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)

    organization_subscription_room = graphene.Field(OrganizationSubscriptionPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationsubscriptionprice')

        if not len(input['name']):
            raise GraphQLError(_('Name is required'))

        rid = get_rid(input['organization_subscription'])
        organization_subscription = OrganizationSubscription.objects.filter(id=rid.id).first()
        if not organization_subscription:
            raise Exception('Invalid Organization Subscription ID!')

        organization_subscription_room = OrganizationSubscriptionPrice(
            organization_subscription = organization_subscription,
            name=input['name'], 
            display_public=input['display_public']
        )
        organization_subscription_room.save()

        return CreateOrganizationSubscriptionPrice(organization_subscription_room=organization_subscription_room)


class UpdateOrganizationSubscriptionPrice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)
        
    organization_subscription_room = graphene.Field(OrganizationSubscriptionPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationsubscriptionprice')

        rid = get_rid(input['id'])

        organization_subscription_room = OrganizationSubscriptionPrice.objects.filter(id=rid.id).first()
        if not organization_subscription_room:
            raise Exception('Invalid Organization Subscription Room ID!')

        organization_subscription_room.name = input['name']
        organization_subscription_room.display_public = input['display_public']
        organization_subscription_room.save(force_update=True)

        return UpdateOrganizationSubscriptionPrice(organization_subscription_room=organization_subscription_room)


class ArchiveOrganizationSubscriptionPrice(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_subscription_room = graphene.Field(OrganizationSubscriptionPriceNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationsubscriptionprice')

        rid = get_rid(input['id'])

        organization_subscription_room = OrganizationSubscriptionPrice.objects.filter(id=rid.id).first()
        if not organization_subscription_room:
            raise Exception('Invalid Organization Subscription Room ID!')

        organization_subscription_room.archived = input['archived']
        organization_subscription_room.save(force_update=True)

        return ArchiveOrganizationSubscriptionPrice(organization_subscription_room=organization_subscription_room)


class OrganizationSubscriptionPriceMutation(graphene.ObjectType):
    archive_organization_subscription_room = ArchiveOrganizationSubscriptionPrice.Field()
    create_organization_subscription_room = CreateOrganizationSubscriptionPrice.Field()
    update_organization_subscription_room = UpdateOrganizationSubscriptionPrice.Field()
    