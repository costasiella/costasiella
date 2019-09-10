from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import Organization, OrganizationDocument
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail

m = Messages()

class OrganizatioNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    url_document = graphene.String()


class OrganizationClasstypeNode(DjangoObjectType):
    def resolve_url_document(self, info):
        if self.document:
            return self.document.url
        else:
            return ''
    
    class Meta:
        model = OrganizationDocument
        filter_fields = ['document_type', 'organization']
        interfaces = (graphene.relay.Node, OrganizationDocumentNodeInterface)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        # This node is public, no need for any permission checking

        return self._meta.model.objects.get(id=id)


class OrganizationDocumentQuery(graphene.ObjectType):
    organization_documents = DjangoFilterConnectionField(OrganizationDocumentNode)
    organization_document = graphene.relay.Node.Field(OrganizationDocumentNode)

    # def resolve_organization_documents(self, info, **kwargs):
    #     user = info.context.user

    #     return OrganizationClasstype.objects.all.order_by('document_type', '-date_start')


class CreateOrganizationDocument(graphene.relay.ClientIDMutation):
    class Input:
        document_type = graphene.String(required=True)

        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        document = graphene.String(required=True)

    organization_classtype = graphene.Field(OrganizationClasstypeNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationdocument')

        import base64
        from django.core.files.base import ContentFile

        def base64_file(data, name=None):
            _format, _document_str = data.split(';base64,')
            _name, ext = _format.split('/')
            if not name:
                name = _name.split(":")[-1]
            return ContentFile(base64.b64decode(_document_str), name='{}.{}'.format(name, ext))

        b64_enc_image = input['document']
        # print(b64_enc_image)
        (document_file_type, document_file) = b64_enc_image.split(',')
        # print(document_file_type)

        organization_document = OrganizationDocument(
            organization = Organization.objects.get(id=1),
            document_type = input['document_type'],
            date_start = input['date_start'],
            document = base64_file(data=b64_enc_image)
        )

        if 'date_end' in input:
            date_end = input['date_end']

     

        organization_document.save()

        return CreateOrganizationDocument(organization_document = organization_document)


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


class DeleteOrganizationDocument(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    
    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_organizationdocument')

        rid = get_rid(input['id'])
        organization_document = OrganizationDocument.objects.get(id=rid.id)
        if not organization_document:
            raise Exception('Invalid Organization Document ID!')

        ok = organization_document.delete()

        return DeleteOrganizationDocument(ok=ok)


class OrganizationDocumentMutation(graphene.ObjectType):
    delete_organization_documment = DeleteOrganizationDocument.Field()
    create_organization_document = CreateOrganizationDocument.Field()
    update_organization_document = UpdateOrganizationDocument.Field()
    