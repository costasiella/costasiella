from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import OrganizationAnnouncement
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

m = Messages()


class OrganizationAnnouncementNode(DjangoObjectType):
    class Meta:
        model = OrganizationAnnouncement
        fields = (
            'display_public',
            'display_shop',
            'display_backend',
            'title',
            'content',
            'date_start',
            'date_end',
            'priority',
            'created_at',
            'updated_at'
        )
        filter_fields = ['display_public', 'display_shop', 'display_backend']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        # require_login_and_permission(user, 'costasiella.view_organizationannouncement')
        organization_announcement = self._meta.model.objects.get(id=id)
        if user.has_perm('costasiella.view_organizationannouncement'):
            return organization_announcement
        else:
            if organization_announcement.display_public:
                return organization_announcement
            else:
                raise Exception(m.user_permission_denied)         


class OrganizationAnnouncementQuery(graphene.ObjectType):
    organization_announcements = DjangoFilterConnectionField(OrganizationAnnouncementNode)
    organization_announcement = graphene.relay.Node.Field(OrganizationAnnouncementNode)

    def resolve_organization_announcements(self, info, **kwargs):
        user = info.context.user

        display_shop = kwargs.get('display_shop', None)
        display_backend = kwargs.get('display_backend', None)

        objects = OrganizationAnnouncement.objects

        if display_shop:
            objects = objects.filter(display_shop=True)

        if display_backend:
            objects = objects.filter(display_backend=True)

        if not user.has_perm('costasiella.view_organizationannouncement'):
            objects = objects.filter(display_public=True)

        return objects.order_by('priority', '-date_start')


class CreateOrganizationAnnouncement(graphene.relay.ClientIDMutation):
    class Input:
        display_public = graphene.Boolean(required=False)
        display_shop = graphene.Boolean(required=False)
        display_backend = graphene.Boolean(required=False)
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=True)
        priority = graphene.Int(required=False)

    organization_announcement = graphene.Field(OrganizationAnnouncementNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationannouncement')

        organization_announcement = OrganizationAnnouncement(
            title=input['title'],
            content=input['content'],
            date_start=input['date_start'],
            date_end=input['date_end']
        )

        if 'display_public' in input:
            organization_announcement.display_public = input['display_public']

        if 'display_shop' in input:
            organization_announcement.display_shop = input['display_shop']

        if 'display_backend' in input:
            organization_announcement.display_backend = input['display_backend']

        if 'priority' in input:
            organization_announcement.priority = input['priority']

        organization_announcement.save()

        return CreateOrganizationAnnouncement(organization_announcement=organization_announcement)


class UpdateOrganizationAnnouncement(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        display_public = graphene.Boolean(required=False)
        display_shop = graphene.Boolean(required=False)
        display_backend = graphene.Boolean(required=False)
        title = graphene.String(required=False)
        content = graphene.String(required=False)
        date_start = graphene.types.datetime.Date(required=False)
        date_end = graphene.types.datetime.Date(required=False)
        priority = graphene.Int(required=False)
        
    organization_announcement = graphene.Field(OrganizationAnnouncementNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationannouncement')

        rid = get_rid(input['id'])

        organization_announcement = OrganizationAnnouncement.objects.filter(id=rid.id).first()
        if not organization_announcement:
            raise Exception('Invalid Organization Announcement ID!')

        if 'display_public' in input:
            organization_announcement.display_public = input['display_public']

        if 'display_shop' in input:
            organization_announcement.display_shop = input['display_shop']

        if 'display_backend' in input:
            organization_announcement.display_backend = input['display_backend']

        if 'title' in input:
            organization_announcement.title = input['title']

        if 'content' in input:
            organization_announcement.content = input['content']

        if 'date_start' in input:
            organization_announcement.date_start = input['date_start']

        if 'date_end' in input:
            organization_announcement.date_end = input['date_end']

        if 'priority' in input:
            organization_announcement.priority = input['priority']

        organization_announcement.save()

        return UpdateOrganizationAnnouncement(organization_announcement=organization_announcement)


class DeleteOrganizationAnnouncement(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationannouncement')

        rid = get_rid(input['id'])
        organization_announcement = OrganizationAnnouncement.objects.filter(id=rid.id).first()
        if not organization_announcement:
            raise Exception('Invalid Organization Announcement ID!')

        ok = bool(organization_announcement.delete())

        return DeleteOrganizationAnnouncement(ok=ok)


class OrganizationAnnouncementMutation(graphene.ObjectType):
    delete_organization_announcement = DeleteOrganizationAnnouncement.Field()
    create_organization_announcement = CreateOrganizationAnnouncement.Field()
    update_organization_announcement = UpdateOrganizationAnnouncement.Field()