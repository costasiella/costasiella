from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, OrganizationLevel, OrganizationLocation, ScheduleEvent, ScheduleEventTicket
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
    if 'organization_level' in input:
        rid = get_rid(input['organization_level'])
        organization_level = OrganizationLevel.objects.filter(id=rid.id).first()
        result['organization_level'] = organization_level
        if not organization_level:
            raise Exception(_('Invalid Organization Level ID!'))

    # Fetch & check teacher (account)
    if 'teacher' in input:
        rid = get_rid(input['teacher'])
        teacher = Account.objects.filter(id=rid.id).first()
        result['teacher'] = teacher
        if not teacher:
            raise Exception(_('Invalid Account ID (teacher)!'))

    # Fetch & check teacher_2 (account)
    if 'teacher_2' in input:
        rid = get_rid(input['teacher_2'])
        teacher_2 = Account.objects.filter(id=rid.id).first()
        result['teacher_2'] = teacher_2
        if not teacher_2:
            raise Exception(_('Invalid Account ID (teacher2)!'))

    return result


class CreateScheduleEvent(graphene.relay.ClientIDMutation):
    class Input:
        display_public = graphene.Boolean(required=False, default_value=False)
        display_shop = graphene.Boolean(required=False, default_value=False)
        auto_send_info_mail = graphene.Boolean(required=False, default_value=False)
        organization_location = graphene.ID(required=True)
        organization_level = graphene.ID(required=False)
        name = graphene.String(required=True)
        tagline = graphene.String(required=False, default_value="")
        preview = graphene.String(required=False, default_value="")
        description = graphene.String(required=False, default_value="")
        teacher = graphene.ID(required=False)
        teacher_2 = graphene.ID(required=False)
        info_mail_content = graphene.String(required=False, default_value="")

    schedule_event = graphene.Field(ScheduleEventNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleevent')

        # Validate input
        result = validate_create_update_input(input, update=False)

        schedule_event = ScheduleEvent(
            display_public=input['display_public'],
            display_shop=input['display_shop'],
            auto_send_info_mail=input['auto_send_info_mail'],
            organization_location=result['organization_location'],
            name=input['name'],
            tagline=input['tagline'],
            description=input['description'],
            info_mail_content=input['info_mail_content']
        )

        if 'organization_level' in result:
            schedule_event.organization_level = result['organization_level']

        if 'teacher' in result:
            schedule_event.teacher = result['teacher']

        if 'teacher_' in result:
            schedule_event.teacher_2 = result['teacher_2']

        schedule_event.save()

        schedule_event_ticket = ScheduleEventTicket(
            schedule_event=schedule_event,
            display_public=True,
            full_event=True,
            deletable=False,
            name=_("Full event"),
            description="",
            price=0
        )
        schedule_event_ticket.save()


        return CreateScheduleEvent(schedule_event=schedule_event)


class UpdateScheduleEvent(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        display_public = graphene.Boolean(required=False)
        display_shop = graphene.Boolean(required=False)
        auto_send_info_mail = graphene.Boolean(required=False)
        organization_location = graphene.ID(required=False)
        organization_level = graphene.ID(required=False)
        name = graphene.String(required=False)
        tagline = graphene.String(required=False)
        preview = graphene.String(required=False)
        description = graphene.String(required=False)
        teacher = graphene.ID(required=False)
        teacher_2 = graphene.ID(required=False)
        info_mail_content = graphene.String(required=False)
        
    schedule_event = graphene.Field(ScheduleEventNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleevent')

        rid = get_rid(input['id'])
        schedule_event = ScheduleEvent.objects.filter(id=rid.id).first()
        if not schedule_event:
            raise Exception('Invalid Schedule Event ID!')

        # Validate input
        result = validate_create_update_input(input, update=True)

        if 'display_public' in input:
            schedule_event.display_public = input['display_public']
        if 'display_shop' in input:
            schedule_event.display_shop = input['display_shop']
        if 'auto_send_info_mail' in input:
            schedule_event.display_shop = input['auto_send_info_mail']
        if 'organization_location' in result:
            schedule_event.organization_location = result['organization_location']
        if 'organization_level' in result:
            schedule_event.organization_level = result['organization_level']
        if 'name' in input:
            schedule_event.name = input['name']
        if 'tagline' in input:
            schedule_event.tagline = input['tagline']
        if 'preview' in input:
            schedule_event.preview = input['preview']
        if 'description' in input:
            schedule_event.description = input['description']
        if 'teacher' in result:
            schedule_event.teacher = result['teacher']
        if 'teacher_2' in result:
            schedule_event.teacher_2 = result['teacher_2']
        if 'info_mail_content' in input:
            schedule_event.info_mail_content = input['info_mail_content']

        schedule_event.save()

        return UpdateScheduleEvent(schedule_event=schedule_event)


class ArchiveScheduleEvent(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    schedule_event = graphene.Field(ScheduleEventNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleevent')

        rid = get_rid(input['id'])
        schedule_event = ScheduleEvent.objects.filter(id=rid.id).first()
        if not schedule_event:
            raise Exception('Invalid Schedule Event ID!')

        schedule_event.archived = input['archived']
        schedule_event.save()

        return ArchiveScheduleEvent(schedule_event=schedule_event)


class ScheduleEventMutation(graphene.ObjectType):
    archive_schedule_event = ArchiveScheduleEvent.Field()
    create_schedule_event = CreateScheduleEvent.Field()
    update_schedule_event = UpdateScheduleEvent.Field()
