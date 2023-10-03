from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationLocation, OrganizationLocationRoom
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationLocationNode(DjangoObjectType):
    class Meta:
        model = OrganizationLocation
        fields = (
            'archived',
            'display_public',
            'name',
            # Reverse relations
            'rooms'
        )
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        # require_login_and_permission(user, 'costasiella.view_organizationlocation')

        organization_location = self._meta.model.objects.get(id=id)

        if info.path.typename == 'ScheduleEventNode' or info.path.typename == "OrganizationLocationRoomNode":
            return organization_location

        if user.has_perm('costasiella.view_organizationlocation') or \
           (organization_location.display_public is True and organization_location.archived is False):
            return organization_location


class OrganizationLocationQuery(graphene.ObjectType):
    organization_locations = DjangoFilterConnectionField(OrganizationLocationNode)
    organization_location = graphene.relay.Node.Field(OrganizationLocationNode)

    def resolve_organization_locations(self, info, archived=False, **kwargs):
        user = info.context.user
        if archived is None:
            archived = False

        ## return everything:
        if user.has_perm('costasiella.view_organizationlocation') or \
           user.has_perm('costasiella.view_selfcheckin'):
            # return OrganizationLocation.objects.filter(archived=archived).order_by('name')
            return OrganizationLocation.objects.filter(archived=archived).order_by('name')

        # Return only public non-archived locations
        return OrganizationLocation.objects.filter(display_public=True, archived=False).order_by('name')


    # def resolve_organization_location(self, info, id):
    #     user = info.context.user
    #     print('user authenticated:')
    #     print(user.is_authenticated)
    #     print(user)
    #     print(user.is_anonymous)
    #     require_login_and_permission(user, 'costasiella.view_organizationlocation')

    #     # Return only public non-archived locations
    #     return OrganizationLocation.objects.get(id=id)


# # class CreateOrganizationLocationSuccess(graphene.ObjectType):
# # 	organization_location = graphene.Field(OrganizationLocationType, required=True)


# # class CreateOrganizationLocationPayload(graphene.Union):
# #     class Meta:
# #         types = (ValidationErrors, CreateOrganizationLocationSuccess)


class CreateOrganizationLocation(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)

    organization_location = graphene.Field(OrganizationLocationNode)

    # Output = CreateOrganizationLocationPayload

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationlocation')

        errors = []
        if not len(input['name']):
            raise GraphQLError(_('Name is required'))
            # errors.append(
            #     ValidationErrorMessage(
            #         field="name",
            #         message=_("Name is required")
            #     )
            # )

            # return ValidationErrors(
            #     validation_errors = errors
            # )

        organization_location = OrganizationLocation(
            name=input['name'], 
            display_public=input['display_public']
        )
        organization_location.save()

        # Insert default room when creating a location
        default_room = OrganizationLocationRoom(
            organization_location = organization_location,
            display_public = organization_location.display_public, # mimic parent object
            name = _("Room 1")
        )
        default_room.save()

        # return CreateOrganizationLocationSuccess(organization_location=organization_location)
        return CreateOrganizationLocation(organization_location=organization_location)


# ''' Query like this when enabling error output using union:
# mutation {
#   createOrganizationLocation(name:"", displayPublic:true) {
#     __typename
#     ... on CreateOrganizationLocationSuccess {
#       organizationLocation {
#         id
#         name
#       }
#     }
#     ... on ValidationErrors {
#       validationErrors {
#         field
#         message
#       }
#     }
#   }
# }

# '''

class UpdateOrganizationLocation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)
        
    organization_location = graphene.Field(OrganizationLocationNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationlocation')

        rid = get_rid(input['id'])

        organization_location = OrganizationLocation.objects.filter(id=rid.id).first()
        if not organization_location:
            raise Exception('Invalid Organization Location ID!')

        organization_location.name = input['name']
        organization_location.display_public = input['display_public']
        organization_location.save(force_update=True)

        return UpdateOrganizationLocation(organization_location=organization_location)


class ArchiveOrganizationLocation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_location = graphene.Field(OrganizationLocationNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationlocation')

        rid = get_rid(input['id'])

        organization_location = OrganizationLocation.objects.filter(id=rid.id).first()
        if not organization_location:
            raise Exception('Invalid Organization Location ID!')

        organization_location.archived = input['archived']
        organization_location.save()

        return ArchiveOrganizationLocation(organization_location=organization_location)


class OrganizationLocationMutation(graphene.ObjectType):
    archive_organization_location = ArchiveOrganizationLocation.Field()
    create_organization_location = CreateOrganizationLocation.Field()
    update_organization_location = UpdateOrganizationLocation.Field()