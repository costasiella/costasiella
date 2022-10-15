from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import ScheduleItem, OrganizationClasspassGroup, ScheduleItemOrganizationClasspassGroup
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class ScheduleItemOrganizationClasspassGroupNode(DjangoObjectType):
    class Meta:
        model = ScheduleItemOrganizationClasspassGroup
        fields = (
            'schedule_item',
            'organization_classpass_group',
            'shop_book',
            'attend'
        )
        filter_fields = ['schedule_item', 'organization_classpass_group']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitemorganizationclasspassgroup')

        return self._meta.model.objects.get(id=id)


class ScheduleItemOrganizationClasspassGroupQuery(graphene.ObjectType):
    schedule_item_organization_classpass_groups = DjangoFilterConnectionField(ScheduleItemOrganizationClasspassGroupNode)
    schedule_item_organization_classpass_group = graphene.relay.Node.Field(ScheduleItemOrganizationClasspassGroupNode)


    def resolve_schedule_item_organization_classpass_groups(self, info, **kwargs):
        user = info.context.user
        require_login(user)
        # Has permission: return everything
        if user.has_perm('costasiella.view_scheduleitemorganizationclasspassgroup'):
            return ScheduleItemOrganizationClasspassGroup.objects.filter().order_by('organization_classpass_group__name')


class CreateScheduleItemOrganizationClasspassGroup(graphene.relay.ClientIDMutation):
    class Input:
        schedule_item = graphene.ID(required=True)
        organization_classpass_group = graphene.ID(required=True)
        shop_book = graphene.Boolean(required=False, default_value=False)
        attend = graphene.Boolean(required=False, default_value=False)

    schedule_item_organization_classpass_group = graphene.Field(ScheduleItemOrganizationClasspassGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleitemorganizationclasspassgroup')

        rid_schedule_item = get_rid(input['schedule_item'])
        rid_group = get_rid(input['organization_classpass_group'])

        schedule_item = ScheduleItem.objects.get(pk=rid_schedule_item.id)
        organization_classpass_group = OrganizationClasspassGroup.objects.get(pk=rid_group.id)

        schedule_item_organization_classpass_group = ScheduleItemOrganizationClasspassGroup(
            schedule_item = schedule_item,
            organization_classpass_group = organization_classpass_group,
        )

        schedule_item_organization_classpass_group.save()

        return CreateScheduleItemOrganizationClasspassGroup(schedule_item_organization_classpass_group=schedule_item_organization_classpass_group)


class UpdateScheduleItemOrganizationClasspassGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        shop_book = graphene.Boolean(required=False, default_value=False)
        attend = graphene.Boolean(required=False, default_value=False)

    schedule_item_organization_classpass_group = graphene.Field(ScheduleItemOrganizationClasspassGroupNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleitemorganizationclasspassgroup')

        rid = get_rid(input['id'])
        schedule_item_organization_classpass_group = ScheduleItemOrganizationClasspassGroup.objects.filter(id=rid.id).first()
        if not schedule_item_organization_classpass_group:
            raise Exception('Invalid Schedule Item Organization Classpass Group ID!')

        if 'shop_book' in input:
            schedule_item_organization_classpass_group.shop_book = input['shop_book']

        if 'attend' in input:
            schedule_item_organization_classpass_group.attend = input['attend']

        schedule_item_organization_classpass_group.save()

        return UpdateScheduleItemOrganizationClasspassGroup(schedule_item_organization_classpass_group=schedule_item_organization_classpass_group)


class DeleteScheduleItemOrganizationClasspassGroup(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    deleted_schedule_item_organization_subscription_group_id = graphene.ID()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleitemorganizationclasspassgroup')

        rid = get_rid(input['id'])
        schedule_item_organization_classpass_group = ScheduleItemOrganizationClasspassGroup.objects.filter(id=rid.id).first()
        if not schedule_item_organization_classpass_group:
            raise Exception('Invalid Schedule Item Organization Classpass Group ID!')

        ok = bool(schedule_item_organization_classpass_group.delete())

        return DeleteScheduleItemOrganizationClasspassGroup(
            ok=ok
        )


class ScheduleItemOrganizationClasspassGroupMutation(graphene.ObjectType):
    # create_schedule_item_organization_classpass_group = CreateScheduleItemOrganizationClasspassGroup.Field()
    update_schedule_item_organization_classpass_group = UpdateScheduleItemOrganizationClasspassGroup.Field()
    # delete_schedule_item_organization_classpass_group = DeleteScheduleItemOrganizationClasspassGroup.Field()