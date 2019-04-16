from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationClasspassGroup
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationClasspassGroupNode(DjangoObjectType):
    class Meta:
        model = OrganizationClasspassGroup
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationclasspassgroup')

        return self._meta.model.objects.get(id=id)


class OrganizationClasspassGroupQuery(graphene.ObjectType):
    organization_classpass_groups = DjangoFilterConnectionField(OrganizationClasspassGroupNode)
    organization_classpass_group = graphene.relay.Node.Field(OrganizationClasspassGroupNode)

    def resolve_organization_classpass_groups(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationclasspassgroup')

        ## return everything:
        return OrganizationClasspassGroup.objects.filter(archived = archived).order_by('name')


class CreateOrganizationClasspassGroup(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    organization_classpass_group = graphene.Field(OrganizationClasspassGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationclasspassgroup')

        errors = []
        if not len(input['name']):
            print('validation error found')
            raise GraphQLError(_('Name is required'))

        organization_classpass_group = OrganizationClasspassGroup(
            name=input['name'], 
        )

        organization_classpass_group.save()

        return CreateOrganizationClasspassGroup(organization_classpass_group=organization_classpass_group)


class UpdateOrganizationClasspassGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        
    organization_classpass_group = graphene.Field(OrganizationClasspassGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationclasspassgroup')

        rid = get_rid(input['id'])

        organization_classpass_group = OrganizationClasspassGroup.objects.filter(id=rid.id).first()
        if not organization_classpass_group:
            raise Exception('Invalid Organization Classpass Group ID!')

        organization_classpass_group.name = input['name']
        organization_classpass_group.save(force_update=True)

        return UpdateOrganizationClasspassGroup(organization_classpass_group=organization_classpass_group)


class ArchiveOrganizationClasspassGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_classpass_group = graphene.Field(OrganizationClasspassGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationclasspassgroup')

        rid = get_rid(input['id'])

        organization_classpass_group = OrganizationClasspassGroup.objects.filter(id=rid.id).first()
        if not organization_classpass_group:
            raise Exception('Invalid Organization Classpass Group ID!')

        organization_classpass_group.archived = input['archived']
        organization_classpass_group.save(force_update=True)

        return ArchiveOrganizationClasspassGroup(organization_classpass_group=organization_classpass_group)


class OrganizationClasspassGroupMutation(graphene.ObjectType):
    archive_organization_classpass_group = ArchiveOrganizationClasspassGroup.Field()
    create_organization_classpass_group = CreateOrganizationClasspassGroup.Field()
    update_organization_classpass_group = UpdateOrganizationClasspassGroup.Field()