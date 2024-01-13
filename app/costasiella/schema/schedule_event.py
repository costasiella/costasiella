from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django_filters import FilterSet, OrderingFilter
from graphql_relay import to_global_id
from graphql import GraphQLError

from ..dudes import ScheduleEventDude
from ..models import Account, OrganizationLevel, OrganizationLocation, ScheduleEvent, ScheduleEventTicket
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class ScheduleEventNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    url_shop = graphene.String()


class ScheduleEventFilter(FilterSet):
    class Meta:
        model = ScheduleEvent
        fields = ['archived', 'display_public', 'display_shop']

        order_by = OrderingFilter(
            fields=(
                ('date_start', 'date_start'),
            )
        )

class ScheduleEventNode(DjangoObjectType):
    class Meta:
        model = ScheduleEvent
        filterset_class = ScheduleEventFilter
        fields = (
            # model fields
            'archived',
            'display_public',
            'display_shop',
            'auto_send_info_mail',
            'organization_location',
            'name',
            'tagline',
            'preview',
            'description',
            'organization_level',
            'instructor',
            'instructor_2',
            'date_start',
            'date_end',
            'time_start',
            'time_end',
            'info_mail_content',
            'created_at',
            'updated_at',
            # Reverse relations,
            'media',
            'schedule_items',
            'tickets'
        )
        # filter_fields = ['archived', 'display_public', 'display_shop']
        interfaces = (graphene.relay.Node, ScheduleEventNodeInterface, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        schedule_event = self._meta.model.objects.get(id=id)
        if not schedule_event.display_public and not schedule_event.display_shop:
            require_login_and_permission(user, 'costasiella.view_scheduleevent')
            return schedule_event
        else:
            return schedule_event

    def resolve_url_shop(self, info):
        try:
            scheme = info.context.scheme
            host = info.context.get_host()
            global_event_id = to_global_id("ScheduleEventNode", self.id)

            url_shop = f"{scheme}://{host}/#/shop/events/{global_event_id}"
        except AttributeError:
            # Eg. When calling from another part piece of code instead of the API, info.context won't be available
            url_shop = ""

        return url_shop

class ScheduleEventQuery(graphene.ObjectType):
    schedule_events = DjangoFilterConnectionField(ScheduleEventNode,
                                                  orderBy=graphene.List(of_type=graphene.String))
    schedule_event = graphene.relay.Node.Field(ScheduleEventNode)

    # Login is not required, public schedule events are well... public
    def resolve_schedule_events(self, info, archived=False, **kwargs):
        user = info.context.user

        order_by = kwargs.get('orderBy')
        if not order_by:
            # Smallest date first ("oldest first" makes sense as the default.
            # on websites, etc. we don't want to show the biggest date first, that looks strange")
            order_by = ['date_start']

        # order_by = '-date_start'
        # Has permission: return everything requested
        if user.has_perm('costasiella.view_scheduleevent'):
            return ScheduleEvent.objects.filter(archived=archived).order_by(*order_by)

        # Return only public non-archived events
        return ScheduleEvent.objects.filter(display_public=True, archived=False).order_by(*order_by)


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
        if input['organization_level']:
            rid = get_rid(input['organization_level'])
            organization_level = OrganizationLevel.objects.filter(id=rid.id).first()
            result['organization_level'] = organization_level
            if not organization_level:
                raise Exception(_('Invalid Organization Level ID!'))

    # Fetch & check instructor (account)
    if 'instructor' in input:
        rid = get_rid(input['instructor'])
        instructor = Account.objects.filter(id=rid.id).first()
        result['instructor'] = instructor
        if not instructor:
            raise Exception(_('Invalid Account ID (instructor)!'))

    # Fetch & check instructor_2 (account)
    if 'instructor_2' in input:
        rid = get_rid(input['instructor_2'])
        instructor_2 = Account.objects.filter(id=rid.id).first()
        result['instructor_2'] = instructor_2
        if not instructor_2:
            raise Exception(_('Invalid Account ID (instructor2)!'))

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
        instructor = graphene.ID(required=False)
        instructor_2 = graphene.ID(required=False)
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
            preview=input['preview'],
            description=input['description'],
            info_mail_content=input['info_mail_content']
        )

        if 'organization_level' in result:
            schedule_event.organization_level = result['organization_level']

        if 'instructor' in result:
            schedule_event.instructor = result['instructor']

        if 'instructor_2' in result:
            schedule_event.instructor_2 = result['instructor_2']

        schedule_event.save()

        schedule_event_ticket = ScheduleEventTicket(
            schedule_event=schedule_event,
            display_public=True,
            full_event=True,
            deletable=False,
            name=_("Full event"),
            description=_("Full event"),
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
        instructor = graphene.ID(required=False)
        instructor_2 = graphene.ID(required=False)
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
            schedule_event.auto_send_info_mail = input['auto_send_info_mail']
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
        if 'instructor' in result:
            schedule_event.instructor = result['instructor']
        if 'instructor_2' in result:
            schedule_event.instructor_2 = result['instructor_2']
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


class DuplicateScheduleEvent(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    schedule_event = graphene.Field(ScheduleEventNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleevent')

        rid = get_rid(input['id'])
        schedule_event = ScheduleEvent.objects.filter(id=rid.id).first()
        if not schedule_event:
            raise Exception('Invalid Schedule Event ID!')

        # Duplicate schedule event
        schedule_event_dude = ScheduleEventDude()
        new_schedule_event = schedule_event_dude.duplicate(schedule_event)

        # Return duplicated schedule event
        return DuplicateScheduleEvent(schedule_event=new_schedule_event)


class ScheduleEventMutation(graphene.ObjectType):
    archive_schedule_event = ArchiveScheduleEvent.Field()
    create_schedule_event = CreateScheduleEvent.Field()
    update_schedule_event = UpdateScheduleEvent.Field()
    duplicate_schedule_event = DuplicateScheduleEvent.Field()
