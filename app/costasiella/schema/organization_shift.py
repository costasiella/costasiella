from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationShift
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationShiftNode(DjangoObjectType):
    class Meta:
        model = OrganizationShift
        fields = (
            'archived',
            'name'
        )
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationshift')
        
        return self._meta.model.objects.get(id=id)


class OrganizationShiftQuery(graphene.ObjectType):
    organization_shifts = DjangoFilterConnectionField(OrganizationShiftNode)
    organization_shift = graphene.relay.Node.Field(OrganizationShiftNode)

    def resolve_organization_shifts(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationshift')

        return OrganizationShift.objects.filter(archived=archived).order_by('name')


class CreateOrganizationShift(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)

    organization_shift = graphene.Field(OrganizationShiftNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationshift')

        organization_shift = OrganizationShift(
            name=input['name'], 
        )

        organization_shift.save()

        return CreateOrganizationShift(organization_shift=organization_shift)


class UpdateOrganizationShift(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        
    organization_shift = graphene.Field(OrganizationShiftNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationshift')

        rid = get_rid(input['id'])

        organization_shift = OrganizationShift.objects.filter(id=rid.id).first()
        if not organization_shift:
            raise Exception('Invalid Organization Shift ID!')

        organization_shift.name = input['name']
        organization_shift.save(force_update=True)

        return UpdateOrganizationShift(organization_shift=organization_shift)


class ArchiveOrganizationShift(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_shift = graphene.Field(OrganizationShiftNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationshift')

        rid = get_rid(input['id'])

        organization_shift = OrganizationShift.objects.filter(id=rid.id).first()
        if not organization_shift:
            raise Exception('Invalid Organization Shift ID!')

        organization_shift.archived = input['archived']
        organization_shift.save()

        return ArchiveOrganizationShift(organization_shift=organization_shift)


class OrganizationShiftMutation(graphene.ObjectType):
    archive_organization_shift = ArchiveOrganizationShift.Field()
    create_organization_shift = CreateOrganizationShift.Field()
    update_organization_shift = UpdateOrganizationShift.Field()