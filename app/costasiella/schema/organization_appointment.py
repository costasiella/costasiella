from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import OrganizationAppointment
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail

m = Messages()

class OrganizationAppointmentNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    url_image = graphene.String()
    url_image_thumbnail_small = graphene.String()


class OrganizationAppointmentNode(DjangoObjectType):
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
    
    class Meta:
        model = OrganizationAppointment
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, OrganizationAppointmentNodeInterface)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationappointment')

        # Return only public non-archived appointments
        return self._meta.model.objects.get(id=id)


class OrganizationAppointmentQuery(graphene.ObjectType):
    organization_appointments = DjangoFilterConnectionField(OrganizationAppointmentNode)
    organization_appointment = graphene.relay.Node.Field(OrganizationAppointmentNode)

    def resolve_organization_appointments(self, info, archived, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception(m.user_not_logged_in)

        # Has permission: return everything
        if user.has_perm('costasiella.view_organizationappointment'):
            print('user has view permission')
            return OrganizationAppointment.objects.filter(archived = archived).order_by('name')

        # Return only public non-archived locations
        return OrganizationAppointment.objects.filter(display_public = True, archived = False).order_by('name')


class CreateOrganizationAppointment(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        display_public = graphene.Boolean(required=True, default_value=True)
        url_website = graphene.String(required=False, default_value="")

    organization_appointment = graphene.Field(OrganizationAppointmentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationappointment')

        # Validate input
        if not len(input['name']):
            print('validation error found')
            raise GraphQLError(_('Name is required'))

        url_website = input['url_website']
        if url_website:
            if not validators.url(url_website, public=True):
                raise GraphQLError(_('Invalid URL, make sure it starts with "http"'))

        organization_appointment = OrganizationAppointment(
            name=input['name'], 
            description=input['description'],
            display_public=input['display_public'],
            url_website=url_website,
        )
        organization_appointment.save()

        return CreateOrganizationAppointment(organization_appointment = organization_appointment)


class UpdateOrganizationAppointment(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        display_public = graphene.Boolean(required=True, default_value=True)
        url_website = graphene.String(required=False, default_value="")

    organization_appointment = graphene.Field(OrganizationAppointmentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationappointment')

        rid = get_rid(input['id'])
        appointment = OrganizationAppointment.objects.filter(id=rid.id).first()
        if not appointment:
            raise Exception('Invalid Organization Appointment ID!')

        url_website = input['url_website']
        if url_website:
            if not validators.url(url_website, public=True):
                raise GraphQLError(_('Invalid URL, make sure it starts with "http"'))
            else:
                appointment.url_website = url_website

        appointment.name = input['name']
        appointment.description = input['description']
        appointment.display_public = input['display_public']
        appointment.save(force_update=True)

        return UpdateOrganizationAppointment(organization_appointment=appointment)


class UploadOrganizationAppointmentImage(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        image = graphene.String(required=True)


    organization_appointment = graphene.Field(OrganizationAppointmentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationappointment')

        import base64
        from django.core.files.base import ContentFile

        def base64_file(data, name=None):
            _format, _img_str = data.split(';base64,')
            _name, ext = _format.split('/')
            if not name:
                name = _name.split(":")[-1]
            return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))

        rid = get_rid(input['id'])
        appointment = OrganizationAppointment.objects.filter(id=rid.id).first()
        if not appointment:
            raise Exception('Invalid Organization Appointment ID!')

        b64_enc_image = input['image']
        # print(b64_enc_image)
        (image_type, image_file) = b64_enc_image.split(',')
        # print(image_type)

        
        appointment.image = base64_file(data=b64_enc_image)
        appointment.save(force_update=True)

        print('new image')
        img = appointment.image
        print(img.name)
        print(img.path)
        print(img.url)

        return UpdateOrganizationAppointment(organization_appointment=appointment)


class ArchiveOrganizationAppointment(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_appointment = graphene.Field(OrganizationAppointmentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationappointment')

        rid = get_rid(input['id'])
        appointment = OrganizationAppointment.objects.filter(id=rid.id).first()
        if not appointment:
            raise Exception('Invalid Organization Appointment ID!')

        appointment.archived = input['archived']
        appointment.save(force_update=True)

        return ArchiveOrganizationAppointment(organization_appointment=appointment)


class OrganizationAppointmentMutation(graphene.ObjectType):
    archive_organization_appointment = ArchiveOrganizationAppointment.Field()
    create_organization_appointment = CreateOrganizationAppointment.Field()
    update_organization_appointment = UpdateOrganizationAppointment.Field()
    upload_organization_appointment_image = UploadOrganizationAppointmentImage.Field()