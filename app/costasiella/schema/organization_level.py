from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationLevel
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationLevelNode(DjangoObjectType):
    class Meta:
        model = OrganizationLevel
        fields = (
            'archived',
            'name'
        )
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        # require_login_and_permission(user, 'costasiella.view_organizationlevel')
        organization_level = self._meta.model.objects.get(id=id)
        if user.has_perm('costasiella.view_organizationlevel'):
            return organization_level
        else:
            if organization_level.archived is False:
                return organization_level


class OrganizationLevelQuery(graphene.ObjectType):
    organization_levels = DjangoFilterConnectionField(OrganizationLevelNode)
    organization_level = graphene.relay.Node.Field(OrganizationLevelNode)

    def resolve_organization_levels(self, info, archived=False, **kwargs):
        user = info.context.user
        # require_login_and_permission(user, 'costasiella.view_organizationlevel')

        ## return everything:
        if user.has_perm('costasiella.view_organizationlevel'):
            return OrganizationLevel.objects.filter(archived=archived).order_by('name')
        else:
            return OrganizationLevel.objects.filter(archived=False).order_by('name')


class CreateOrganizationLevel(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    organization_level = graphene.Field(OrganizationLevelNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationlevel')

        errors = []
        if not len(input['name']):
            raise GraphQLError(_('Name is required'))

        organization_level = OrganizationLevel(
            name=input['name'], 
        )

        organization_level.save()

        return CreateOrganizationLevel(organization_level=organization_level)


class UpdateOrganizationLevel(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        
    organization_level = graphene.Field(OrganizationLevelNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationlevel')

        rid = get_rid(input['id'])

        organization_level = OrganizationLevel.objects.filter(id=rid.id).first()
        if not organization_level:
            raise Exception('Invalid Organization Level ID!')

        organization_level.name = input['name']
        organization_level.save(force_update=True)

        return UpdateOrganizationLevel(organization_level=organization_level)


class ArchiveOrganizationLevel(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_level = graphene.Field(OrganizationLevelNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationlevel')

        rid = get_rid(input['id'])

        organization_level = OrganizationLevel.objects.filter(id=rid.id).first()
        if not organization_level:
            raise Exception('Invalid Organization Level ID!')

        organization_level.archived = input['archived']
        organization_level.save()

        return ArchiveOrganizationLevel(organization_level=organization_level)


class OrganizationLevelMutation(graphene.ObjectType):
    archive_organization_level = ArchiveOrganizationLevel.Field()
    create_organization_level = CreateOrganizationLevel.Field()
    update_organization_level = UpdateOrganizationLevel.Field()