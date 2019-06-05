from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import ScheduleItem
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class ScheduleItemNode(DjangoObjectType):
    class Meta:
        model = ScheduleItem
        filter_fields = ['schedule_type']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitem')

        return self._meta.model.objects.get(id=id)


class ScheduleItemQuery(graphene.ObjectType):
    schedule_items = DjangoFilterConnectionField(ScheduleItemNode)
    schedule_item = graphene.relay.Node.Field(ScheduleItemNode)

    def resolve_organization_levels(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleitem')

        ## return everything:
        # if user.has_perm('costasiella.view_organizationlevel'):
        return OrganizationLevel.objects.filter(archived = archived).order_by('name')

        # return None


class CreateScheduleItem(graphene.relay.ClientIDMutation):
    class Input:
        schedule_item_type = graphene.String(required=True)
        frequency_type = graphene.String(required=True)
        frequency_interval = graphene.Int(required=True)
        organization_location_room = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        time_start = graphene.types.datetime.Time(required=True)
        time_end = graphene.types.datetime.Time(required=True)

    schedule_item = graphene.Field(ScheduleItemNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleitem')

        
        # if not len(input['name']):
        #     print('validation error found')
        #     raise GraphQLError(_('Name is required'))

        schedule_item = ScheduleItem(
            schedule_item_type=input['schedule_item_type'], 
            frequency_type=input['frequency_type'], 
            frequency_interval=input['frequency_interval'], 
        )

        schedule_item.save()

        return CreateScheduleItem(schedule_item=schedule_item)


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
        organization_level.save(force_update=True)

        return ArchiveOrganizationLevel(organization_level=organization_level)


class OrganizationLevelMutation(graphene.ObjectType):
    archive_organization_level = ArchiveOrganizationLevel.Field()
    create_organization_level = CreateOrganizationLevel.Field()
    update_organization_level = UpdateOrganizationLevel.Field()