from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationLocation, OrganizationLocationRoom
from ..modules.gql_tools import require_login_and_permission, require_login_and_one_of_permissions, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationLocationRoomNode(DjangoObjectType):
    class Meta:
        model = OrganizationLocationRoom
        fields = (
            'organization_location',
            'archived',
            'display_public',
            'name'
        )
        filter_fields = ['archived', 'organization_location']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user

        room = self._meta.model.objects.get(id=id)

        if info.path.typename == "ScheduleItemNode":
            return room

        if room.archived or not room.display_public:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_organizationlocationroom',
                'costasiella.view_selfcheckin'
            ])

        # Return only public non-archived location rooms
        # if not accessing from another object
        return room


class OrganizationLocationRoomQuery(graphene.ObjectType):
    organization_location_rooms = DjangoFilterConnectionField(OrganizationLocationRoomNode)
    organization_location_room = graphene.relay.Node.Field(OrganizationLocationRoomNode)

    def resolve_organization_location_rooms(self, info, archived=False, **kwargs):
        user = info.context.user

        if user.is_anonymous:
            raise Exception(m.user_not_logged_in)

        ## return everything:
        if user.has_perm('costasiella.view_organizationlocationroom') or \
           user.has_perm('costasiella.view_selfcheckin'):
            return OrganizationLocationRoom.objects.filter(
                archived=archived
            ).order_by('organization_location__name', 'name')

        # Return only public non-archived rooms
        return OrganizationLocationRoom.objects.filter(
            display_public=True, archived=False
        ).order_by('organization_location__name', 'name')
            

class CreateOrganizationLocationRoom(graphene.relay.ClientIDMutation):
    class Input:
        organization_location = graphene.ID(required=True)
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)

    organization_location_room = graphene.Field(OrganizationLocationRoomNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationlocationroom')

        if not len(input['name']):
            raise GraphQLError(_('Name is required'))

        rid = get_rid(input['organization_location'])
        organization_location = OrganizationLocation.objects.filter(id=rid.id).first()
        if not organization_location:
            raise Exception('Invalid Organization Location ID!')

        organization_location_room = OrganizationLocationRoom(
            organization_location = organization_location,
            name=input['name'], 
            display_public=input['display_public']
        )
        organization_location_room.save()

        return CreateOrganizationLocationRoom(organization_location_room=organization_location_room)


class UpdateOrganizationLocationRoom(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)
        
    organization_location_room = graphene.Field(OrganizationLocationRoomNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationlocationroom')

        rid = get_rid(input['id'])

        organization_location_room = OrganizationLocationRoom.objects.filter(id=rid.id).first()
        if not organization_location_room:
            raise Exception('Invalid Organization Location Room ID!')

        organization_location_room.name = input['name']
        organization_location_room.display_public = input['display_public']
        organization_location_room.save(force_update=True)

        return UpdateOrganizationLocationRoom(organization_location_room=organization_location_room)


class ArchiveOrganizationLocationRoom(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_location_room = graphene.Field(OrganizationLocationRoomNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationlocationroom')

        rid = get_rid(input['id'])

        organization_location_room = OrganizationLocationRoom.objects.filter(id=rid.id).first()
        if not organization_location_room:
            raise Exception('Invalid Organization Location Room ID!')

        organization_location_room.archived = input['archived']
        organization_location_room.save()

        return ArchiveOrganizationLocationRoom(organization_location_room=organization_location_room)


class OrganizationLocationRoomMutation(graphene.ObjectType):
    archive_organization_location_room = ArchiveOrganizationLocationRoom.Field()
    create_organization_location_room = CreateOrganizationLocationRoom.Field()
    update_organization_location_room = UpdateOrganizationLocationRoom.Field()
    