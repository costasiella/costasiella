from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import ScheduleEvent, ScheduleEventMedia
from ..modules.gql_tools import require_login_and_permission, get_rid, get_content_file_from_base64_str
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail

m = Messages()


class ScheduleEventMediaNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    url_image = graphene.String()
    url_image_thumbnail_small = graphene.String()
    url_image_thumbnail_large = graphene.String()


class ScheduleEventMediaNode(DjangoObjectType):
    class Meta:
        model = ScheduleEventMedia
        fields = (
            'schedule_event',
            'sort_order',
            'description',
            'image'
        )
        filter_fields = ['schedule_event']
        interfaces = (graphene.relay.Node, ScheduleEventMediaNodeInterface)

    @classmethod
    def get_node(self, info, id):
        # user = info.context.user
        # require_login_and_permission(user, 'costasiella.view_scheduleeventmedia')

        return self._meta.model.objects.get(id=id)

    def resolve_url_image(self, info):
        if self.image:
            return self.image.url
        else:
            return ''

    def resolve_url_image_thumbnail_small(self, info):
        if self.image:
            return get_thumbnail(self.image, '50x50', crop='center', quality=99).url
        else:
            return ''

    def resolve_url_image_thumbnail_large(self, info):
        if self.image:
            return get_thumbnail(self.image, '400x400', crop='center', quality=99).url
        else:
            return ''


class ScheduleEventMediaQuery(graphene.ObjectType):
    schedule_event_medias = DjangoFilterConnectionField(ScheduleEventMediaNode)
    schedule_event_media = graphene.relay.Node.Field(ScheduleEventMediaNode)

    def resolve_schedule_event_medias(self, info, **kwargs):
        # user = info.context.user
        # if user.is_anonymous:
        #     raise Exception(m.user_not_logged_in)

        return ScheduleEventMedia.objects.order_by('sort_order')


def validate_create_update_input(input, update=False):
    """
    Validate input
    """
    result = {}

    if 'image' in input or 'image_file_name' in input:
        if not (input.get('image', None) and input.get('image_file_name', None)):
            raise Exception(_('When setting "image" or "imageFileName", both fields need to be present and set'))

    if not update:
        # Check schedule_event
        if 'schedule_event' in input:
            if input['schedule_event']:
                rid = get_rid(input['schedule_event'])
                schedule_event = ScheduleEvent.objects.filter(id=rid.id).first()
                result['schedule_event'] = schedule_event
                if not schedule_event:
                    raise Exception(_('Invalid Schedule Event ID!'))

    return result


# Reference OrganizationDocument components in front-end for implementation reference
class CreateScheduleEventMedia(graphene.relay.ClientIDMutation):
    class Input:
        schedule_event = graphene.ID(required=True)
        sort_order = graphene.Int(required=False, default_value=0)
        description = graphene.String(required=False, default_value="")
        image = graphene.String(required=True)
        image_file_name = graphene.String(required=True)

    schedule_event_media = graphene.Field(ScheduleEventMediaNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_scheduleeventmedia')

        result = validate_create_update_input(input)

        schedule_event_media = ScheduleEventMedia(
            schedule_event=result['schedule_event'],
            sort_order=input['sort_order'],
            description=input['description'],
            image=get_content_file_from_base64_str(data_str=input['image'], file_name=input['image_file_name'])
        )
        schedule_event_media.save()

        return CreateScheduleEventMedia(schedule_event_media=schedule_event_media)


class UpdateScheduleEventMedia(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        sort_order = graphene.Int(required=False)
        description = graphene.String(required=False)
        image = graphene.String(required=False)
        image_file_name = graphene.String(required=False)

    schedule_event_media = graphene.Field(ScheduleEventMediaNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_scheduleeventmedia')

        rid = get_rid(input['id'])
        schedule_event_media = ScheduleEventMedia.objects.filter(id=rid.id).first()
        if not schedule_event_media:
            raise Exception('Invalid Schedule Event Media ID!')

        validate_create_update_input(input)

        if 'sort_order' in input:
            schedule_event_media.sort_order = input['sort_order']

        if 'description' in input:
            schedule_event_media.description = input['description']

        if 'image' in input:
            schedule_event_media.image = get_content_file_from_base64_str(data_str=input['image'],
                                                                          file_name=input['image_file_name'])

        schedule_event_media.save()

        return UpdateScheduleEventMedia(schedule_event_media=schedule_event_media)


class DeleteScheduleEventMedia(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_scheduleeventmedia')

        rid = get_rid(input['id'])
        schedule_event_media = ScheduleEventMedia.objects.filter(id=rid.id).first()
        if not schedule_event_media:
            raise Exception('Invalid Schedule Event Media ID!')

        ok = bool(schedule_event_media.delete())

        return DeleteScheduleEventMedia(ok=ok)


class ScheduleEventMediaMutation(graphene.ObjectType):
    create_schedule_event_media = CreateScheduleEventMedia.Field()
    update_schedule_event_media = UpdateScheduleEventMedia.Field()
    delete_schedule_event_media = DeleteScheduleEventMedia.Field()
