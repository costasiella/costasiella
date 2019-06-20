from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import OrganizationClasstype
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail

m = Messages()

class OrganizationClasstypeNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    url_image = graphene.String()
    url_image_thumbnail_small = graphene.String()


class OrganizationClasstypeNode(DjangoObjectType):
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
        model = OrganizationClasstype
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, OrganizationClasstypeNodeInterface)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_organizationclasstype')

        # Return only public non-archived classtypes
        return self._meta.model.objects.get(id=id)


class OrganizationClasstypeQuery(graphene.ObjectType):
    organization_classtypes = DjangoFilterConnectionField(OrganizationClasstypeNode)
    organization_classtype = graphene.relay.Node.Field(OrganizationClasstypeNode)

    def resolve_organization_classtypes(self, info, archived, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception(m.user_not_logged_in)

        # Has permission: return everything
        if user.has_perm('costasiella.view_organizationclasstype'):
            print('user has view permission')
            return OrganizationClasstype.objects.filter(archived = archived).order_by('name')

        # Return only public non-archived locations
        return OrganizationClasstype.objects.filter(display_public = True, archived = False).order_by('name')


class CreateOrganizationClasstype(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        display_public = graphene.Boolean(required=True, default_value=True)
        url_website = graphene.String(required=False, default_value="")

    organization_classtype = graphene.Field(OrganizationClasstypeNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationclasstype')

        # Validate input
        if not len(input['name']):
            print('validation error found')
            raise GraphQLError(_('Name is required'))

        url_website = input['url_website']
        if url_website:
            if not validators.url(url_website, public=True):
                raise GraphQLError(_('Invalid URL, make sure it starts with "http"'))

        organization_classtype = OrganizationClasstype(
            name=input['name'], 
            description=input['description'],
            display_public=input['display_public'],
            url_website=url_website,
        )
        organization_classtype.save()

        return CreateOrganizationClasstype(organization_classtype = organization_classtype)


class UpdateOrganizationClasstype(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        display_public = graphene.Boolean(required=True, default_value=True)
        url_website = graphene.String(required=False, default_value="")

    organization_classtype = graphene.Field(OrganizationClasstypeNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationclasstype')

        rid = get_rid(input['id'])
        classtype = OrganizationClasstype.objects.filter(id=rid.id).first()
        if not classtype:
            raise Exception('Invalid Organization Classtype ID!')

        url_website = input['url_website']
        if url_website:
            if not validators.url(url_website, public=True):
                raise GraphQLError(_('Invalid URL, make sure it starts with "http"'))
            else:
                classtype.url_website = url_website

        classtype.name = input['name']
        classtype.description = input['description']
        classtype.display_public = input['display_public']
        classtype.save(force_update=True)

        return UpdateOrganizationClasstype(organization_classtype=classtype)


class UploadOrganizationClasstypeImage(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        image = graphene.String(required=True)


    organization_classtype = graphene.Field(OrganizationClasstypeNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationclasstype')

        import base64
        from django.core.files.base import ContentFile

        def base64_file(data, name=None):
            _format, _img_str = data.split(';base64,')
            _name, ext = _format.split('/')
            if not name:
                name = _name.split(":")[-1]
            return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))

        rid = get_rid(input['id'])
        classtype = OrganizationClasstype.objects.filter(id=rid.id).first()
        if not classtype:
            raise Exception('Invalid Organization Classtype ID!')

        b64_enc_image = input['image']
        # print(b64_enc_image)
        (image_type, image_file) = b64_enc_image.split(',')
        # print(image_type)

        
        classtype.image = base64_file(data=b64_enc_image)
        classtype.save(force_update=True)

        print('new image')
        img = classtype.image
        print(img.name)
        print(img.path)
        print(img.url)

        return UpdateOrganizationClasstype(organization_classtype=classtype)


class ArchiveOrganizationClasstype(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    organization_classtype = graphene.Field(OrganizationClasstypeNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationclasstype')

        rid = get_rid(input['id'])
        classtype = OrganizationClasstype.objects.filter(id=rid.id).first()
        if not classtype:
            raise Exception('Invalid Organization Classtype ID!')

        classtype.archived = input['archived']
        classtype.save(force_update=True)

        return ArchiveOrganizationClasstype(organization_classtype=classtype)


class OrganizationClasstypeMutation(graphene.ObjectType):
    archive_organization_classtype = ArchiveOrganizationClasstype.Field()
    create_organization_classtype = CreateOrganizationClasstype.Field()
    update_organization_classtype = UpdateOrganizationClasstype.Field()
    upload_organization_classtype_image = UploadOrganizationClasstypeImage.Field()