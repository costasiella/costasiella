from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationClasspass, OrganizationClasspassGroup, OrganizationClasspassGroupClasspass
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationClasspassGroupClasspassNode(DjangoObjectType):
    class Meta:
        model = OrganizationClasspassGroupClasspass
        fields = (
            'organization_classpass_group',
            'organization_classpass'
        )
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationclasspassgroupclasspass')

        return self._meta.model.objects.get(id=id)


class CreateOrganizationClasspassGroupClasspass(graphene.relay.ClientIDMutation):
    class Input:
        organization_classpass_group = graphene.ID(required=True)
        organization_classpass = graphene.ID(required=True)

    organization_classpass_group_classpass = graphene.Field(OrganizationClasspassGroupClasspassNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationclasspassgroupclasspass')

        rid_group = get_rid(input['organization_classpass_group'])
        rid_pass = get_rid(input['organization_classpass'])

        organization_classpass_group = OrganizationClasspassGroup.objects.get(pk=rid_group.id)
        organization_classpass = OrganizationClasspass.objects.get(pk=rid_pass.id)

        query_set = OrganizationClasspassGroupClasspass.objects.filter(
            organization_classpass_group = organization_classpass_group,
            organization_classpass = organization_classpass
        )

        # Don't insert duplicate records in the DB. If this records exist, fetch and return it
        if not query_set.exists():
            organization_classpass_group_classpass = OrganizationClasspassGroupClasspass(
                organization_classpass_group = organization_classpass_group,
                organization_classpass = organization_classpass
            )

            organization_classpass_group_classpass.save()
        else:
            organization_classpass_group_classpass = query_set.first()

        return CreateOrganizationClasspassGroupClasspass(organization_classpass_group_classpass=organization_classpass_group_classpass)


class DeleteOrganizationClasspassGroupClasspass(graphene.relay.ClientIDMutation):
    class Input:
        # id = graphene.ID(required=True)
        organization_classpass_group = graphene.ID(required=True)
        organization_classpass = graphene.ID(required=True)

    ok = graphene.Boolean()
    deleted_organization_classpass_group_classpass_id = graphene.ID()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationclasspassgroupclasspass')

        # rid = get_rid(input['id'])
        rid_group = get_rid(input['organization_classpass_group'])
        rid_pass = get_rid(input['organization_classpass'])

        organization_classpass_group = OrganizationClasspassGroup.objects.get(pk=rid_group.id)
        organization_classpass = OrganizationClasspass.objects.get(pk=rid_pass.id)

        organization_classpass_group_classpass = OrganizationClasspassGroupClasspass.objects.filter(
            organization_classpass_group = organization_classpass_group,
            organization_classpass = organization_classpass
        ).first()

        ok = bool(organization_classpass_group_classpass.delete())

        return DeleteOrganizationClasspassGroupClasspass(ok=ok)


class OrganizationClasspassGroupClasspassMutation(graphene.ObjectType):
    create_organization_classpass_group_classpass = CreateOrganizationClasspassGroupClasspass.Field()
    delete_organization_classpass_group_classpass = DeleteOrganizationClasspassGroupClasspass.Field()