from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationLevel, OrganizationLocation, ScheduleEvent
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class ScheduleEventNode(DjangoObjectType):
    class Meta:
        model = ScheduleEvent
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_scheduleevent')

        return self._meta.model.objects.get(id=id)


class ScheduleEventQuery(graphene.ObjectType):
    schedule_events = DjangoFilterConnectionField(ScheduleEventNode)
    schedule_event = graphene.relay.Node.Field(ScheduleEventNode)

    def resolve_schedule_events(self, info, archived=False, **kwargs):
        user = info.context.user
        require_login(user)
        # Has permission: return everything requested
        if user.has_perm('costasiella.view_organizationsubscription'):
            return ScheduleEvent.objects.filter(archived=archived).order_by('-date_start')

        # Return only public non-archived locations
        return ScheduleEvent.objects.filter(display_public=True, archived=False).order_by('name')


def validate_create_update_input(input, update=False):
    """
    Validate input
    """
    result = {}

    # Fetch & check account
    # if not update:
    #     # Create only
    #     rid = get_rid(input['organization_location'])
    #     organization_location = OrganizationLocation.objects.filter(id=rid.id).first()
    #     result['organization_location'] = organization_location
    #     if not organization_location:
    #         raise Exception(_('Invalid Organization Location ID!'))

    # Fetch & check organization classpass
    # rid = get_rid(input['organization_classpass'])
    # organization_classpass = OrganizationClasspass.objects.get(pk=rid.id)
    # result['organization_classpass'] = organization_classpass
    # if not organization_classpass:
    #     raise Exception(_('Invalid Organization Classpass ID!'))

    # Fetch & check organization location
    rid = get_rid(input['organization_location'])
    organization_location = OrganizationLocation.objects.filter(id=rid.id).first()
    result['organization_location'] = organization_location
    if not organization_location:
        raise Exception(_('Invalid Organization Location ID!'))

    # Fetch & check organization level
    rid = get_rid(input['organization_level'])
    organization_level = OrganizationLevel.objects.filter(id=rid.id).first()
    result['organization_level'] = organization_level
    if not organization_level:
        raise Exception(_('Invalid Organization Level ID!'))

    return result


class CreateScheduleEvent(graphene.relay.ClientIDMutation):
    class Input:
        display_public = graphene.Boolean(required=False, default_value=False)
        display_shop = graphene.Boolean(required=False, default_value=False)
        auto_send_info_mail = graphene.Boolean(required=False, default_value=False)
        organization_location = graphene.ID(required=True)
        name = graphene.String(required=True)
        tagline = graphene.String(required=False, default_value="")
        preview = graphene.String(required=False, default_value="")
        description = graphene.String(required=False, default_value="")
        organization_level = graphene.ID(required=False)

    schedule_event = graphene.Field(ScheduleEventNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_schedule_event')

        # Validate input
        result = validate_create_update_input(input, update=False)

        schedule_event = ScheduleEvent(
            name=input['name'], 
        )

        schedule_event.save()

        return CreateScheduleEvent(schedule_event=schedule_event)


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