from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from .gql_tools import get_rid
import validators

from ..models import SchoolClasstype
from ..modules.gql_tools import require_login_and_permission
from ..modules.messages import Messages

m = Messages()

class SchoolClasstypeNode(DjangoObjectType):
    class Meta:
        model = SchoolClasstype
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_schoolclasstype')

        # Return only public non-archived classtypes
        return self._meta.model.objects.get(id=id)


class SchoolClasstypeQuery(graphene.ObjectType):
    school_classtypes = DjangoFilterConnectionField(SchoolClasstypeNode)
    school_classtype = graphene.relay.Node.Field(SchoolClasstypeNode)

    def resolve_school_classtypes(self, info, archived, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception(m.user_not_logged_in)

        # Has permission: return everything
        if user.has_perm('costasiella.view_schoolclasstype'):
            print('user has view permission')
            return SchoolClasstype.objects.filter(archived = archived).order_by('name')

        # Return only public non-archived locations
        return SchoolClasstype.objects.filter(display_public = True, archived = False).order_by('name')


class CreateSchoolClasstype(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        display_public = graphene.Boolean(required=True, default_value=True)
        url_website = graphene.String(required=False, default_value="")

    school_classtype = graphene.Field(SchoolClasstypeNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_schoolclasstype')

        # Validate input
        if not len(input['name']):
            print('validation error found')
            raise GraphQLError(_('Name is required'))

        url_website = input['url_website']
        if url_website:
            if not validators.url(url_website, public=True):
                raise GraphQLError(_('Invalid URL, make sure it starts with "http"'))

        school_classtype = SchoolClasstype(
            name=input['name'], 
            description=input['description'],
            display_public=input['display_public'],
            url_website=url_website,
        )
        school_classtype.save()

        return CreateSchoolClasstype(school_classtype = school_classtype)


class UpdateSchoolClasstype(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        description = graphene.String(required=False, default_value="")
        display_public = graphene.Boolean(required=True, default_value=True)
        url_website = graphene.String(required=False, default_value="")

    school_classtype = graphene.Field(SchoolClasstypeNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_schoolclasstype')

        rid = get_rid(input['id'])
        classtype = SchoolClasstype.objects.filter(id=rid.id).first()
        if not classtype:
            raise Exception('Invalid School Classtype ID!')

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

        return UpdateSchoolClasstype(school_classtype=classtype)


class UploadSchoolClasstypeImage(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        image = graphene.String(required=True)


    school_classtype = graphene.Field(SchoolClasstypeNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_schoolclasstype')

        import base64
        from django.core.files.base import ContentFile

        def base64_file(data, name=None):
            _format, _img_str = data.split(';base64,')
            _name, ext = _format.split('/')
            if not name:
                name = _name.split(":")[-1]
            return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))

        rid = get_rid(input['id'])
        classtype = SchoolClasstype.objects.filter(id=rid.id).first()
        if not classtype:
            raise Exception('Invalid School Classtype ID!')

        b64_enc_image = input['image']
        # print(b64_enc_image)
        (image_type, image_file) = b64_enc_image.split(',')
        # print(image_type)

        # print('current image')
        # img = classtype.image
        # print(img.name)
        # print(img.url)

        classtype.image = base64_file(data=b64_enc_image, name="image <3")
        classtype.save(force_update=True)

        return UpdateSchoolClasstype(school_classtype=classtype)


class ArchiveSchoolClasstype(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    school_classtype = graphene.Field(SchoolClasstypeNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_schoolclasstype')

        rid = get_rid(input['id'])
        classtype = SchoolClasstype.objects.filter(id=rid.id).first()
        if not classtype:
            raise Exception('Invalid School Classtype ID!')

        classtype.archived = input['archived']
        classtype.save(force_update=True)

        return ArchiveSchoolClasstype(school_classtype=classtype)


class SchoolClasstypeMutation(graphene.ObjectType):
    archive_school_classtype = ArchiveSchoolClasstype.Field()
    create_school_classtype = CreateSchoolClasstype.Field()
    update_school_classtype = UpdateSchoolClasstype.Field()
    upload_school_classtype_image = UploadSchoolClasstypeImage.Field()