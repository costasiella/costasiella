from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationDiscovery
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationDiscoveryNode(DjangoObjectType):
    class Meta:
        model = OrganizationDiscovery
        fields = (
            'archived',
            'name'
        )
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationdiscovery')

        return self._meta.model.objects.get(id=id)


class OrganizationDiscoveryQuery(graphene.ObjectType):
    organization_discoveries = DjangoFilterConnectionField(OrganizationDiscoveryNode)
    organization_discovery = graphene.relay.Node.Field(OrganizationDiscoveryNode)

    def resolve_organization_discoveries(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationdiscovery')

        ## return everything:
        # if user.has_perm('costasiella.view_organizationdiscovery'):
        return OrganizationDiscovery.objects.filter(archived = archived).order_by('name')

        # return None


class CreateOrganizationDiscovery(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    organization_discovery = graphene.Field(OrganizationDiscoveryNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationdiscovery')

        errors = []
        if not len(input['name']):
            raise GraphQLError(_('Name is required'))

        organization_discovery = OrganizationDiscovery(
            name=input['name'], 
        )

        organization_discovery.save()

        return CreateOrganizationDiscovery(organization_discovery=organization_discovery)


class UpdateOrganizationDiscovery(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        
    organization_discovery = graphene.Field(OrganizationDiscoveryNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationdiscovery')

        rid = get_rid(input['id'])

        organization_discovery = OrganizationDiscovery.objects.filter(id=rid.id).first()
        if not organization_discovery:
            raise Exception('Invalid Organization Discovery ID!')

        organization_discovery.name = input['name']
        organization_discovery.save(force_update=True)

        return UpdateOrganizationDiscovery(organization_discovery=organization_discovery)


class ArchiveOrganizationDiscovery(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_discovery = graphene.Field(OrganizationDiscoveryNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationdiscovery')

        rid = get_rid(input['id'])

        organization_discovery = OrganizationDiscovery.objects.filter(id=rid.id).first()
        if not organization_discovery:
            raise Exception('Invalid Organization Discovery ID!')

        organization_discovery.archived = input['archived']
        organization_discovery.save()

        return ArchiveOrganizationDiscovery(organization_discovery=organization_discovery)


class OrganizationDiscoveryMutation(graphene.ObjectType):
    archive_organization_discovery = ArchiveOrganizationDiscovery.Field()
    create_organization_discovery = CreateOrganizationDiscovery.Field()
    update_organization_discovery = UpdateOrganizationDiscovery.Field()