from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationClasspassGroup
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..modules.model_helpers.organization_classpass_group_helper import OrganizationClasspassGroupHelper

m = Messages()


class OrganizationClasspassGroupNode(DjangoObjectType):
    class Meta:
        model = OrganizationClasspassGroup
        fields = (
            'name',
            'description',
            'organization_classpasses'
        )
        filter_fields = []
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id, **kwargs):
        user = info.context.user
        organization_classpass_group = self._meta.model.objects.get(id=id)

        # Allow returning data when coming from schedule_event_subscription_group_discount and subscription group
        if (info.path.typename == "OrganizationClasspassGroupClasspassNode"):
            return organization_classpass_group

        require_login_and_permission(user, 'costasiella.view_organizationclasspassgroup')

        return organization_classpass_group

class OrganizationClasspassGroupQuery(graphene.ObjectType):
    organization_classpass_groups = DjangoFilterConnectionField(OrganizationClasspassGroupNode)
    organization_classpass_group = graphene.relay.Node.Field(OrganizationClasspassGroupNode)

    def resolve_organization_classpass_groups(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationclasspassgroup')

        ## return everything:
        return OrganizationClasspassGroup.objects.all().order_by('name')


class CreateOrganizationClasspassGroup(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        description = graphene.String(default_value="")

    organization_classpass_group = graphene.Field(OrganizationClasspassGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationclasspassgroup')

        organization_classpass_group = OrganizationClasspassGroup(
            name=input['name'],
            description=input['description']
        )

        organization_classpass_group.save()
        helper = OrganizationClasspassGroupHelper()
        helper.add_to_all_classes(organization_classpass_group.id)

        return CreateOrganizationClasspassGroup(organization_classpass_group=organization_classpass_group)


class UpdateOrganizationClasspassGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=False)
        description = graphene.String(required=False)

    organization_classpass_group = graphene.Field(OrganizationClasspassGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationclasspassgroup')

        rid = get_rid(input['id'])

        organization_classpass_group = OrganizationClasspassGroup.objects.filter(id=rid.id).first()
        if not organization_classpass_group:
            raise Exception('Invalid Organization Classpass Group ID!')

        if 'name' in input:
            organization_classpass_group.name = input['name']

        if 'description' in input:
            organization_classpass_group.description = input['description']

        organization_classpass_group.save()

        return UpdateOrganizationClasspassGroup(organization_classpass_group=organization_classpass_group)


class DeleteOrganizationClasspassGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationclasspassgroup')

        rid = get_rid(input['id'])
        organization_classpass_group = OrganizationClasspassGroup.objects.filter(id=rid.id).first()
        if not organization_classpass_group:
            raise Exception('Invalid Organization Classpass Group ID!')

        ok = bool(organization_classpass_group.delete())

        return DeleteOrganizationClasspassGroup(ok=ok)


class OrganizationClasspassGroupMutation(graphene.ObjectType):
    delete_organization_classpass_group = DeleteOrganizationClasspassGroup.Field()
    create_organization_classpass_group = CreateOrganizationClasspassGroup.Field()
    update_organization_classpass_group = UpdateOrganizationClasspassGroup.Field()
