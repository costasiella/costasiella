from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Organization, OrganizationDocument
from ..modules.gql_tools import require_login_and_permission, get_rid, get_content_file_from_base64_str
from ..modules.messages import Messages
from ..models.choices.organization_document_types import get_organization_document_types

m = Messages()


class OrganizationDocumentNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    url_document = graphene.String()


class OrganizationDocumentNode(DjangoObjectType):
    class Meta:
        model = OrganizationDocument
        fields = (
            'organization',
            'document_type',
            'version',
            'date_start',
            'date_end',
            'document'
        )
        filter_fields = ['document_type', 'organization']
        interfaces = (graphene.relay.Node, OrganizationDocumentNodeInterface)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        # This node is public, no need for any permission checking

        return self._meta.model.objects.get(id=id)

    def resolve_url_document(self, info):
        if self.document:
            return self.document.url
        else:
            return ''


class OrganizationDocumentQuery(graphene.ObjectType):
    organization_documents = DjangoFilterConnectionField(OrganizationDocumentNode)
    organization_document = graphene.relay.Node.Field(OrganizationDocumentNode)


def validate_document_type(document_type):
    types = get_organization_document_types()
    valid_type = False
    for t in types:
        if t[0] == document_type:
            valid_type = True
            break
    
    if not valid_type:
        raise GraphQLError(_('Invalid document type!'))        


class CreateOrganizationDocument(graphene.relay.ClientIDMutation):
    class Input:
        document_file_name = graphene.String(required=True)
        document_type = graphene.String(required=True)
        version = graphene.String(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        document = graphene.String(required=True) # File als base64 encoded string

    organization_document = graphene.Field(OrganizationDocumentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_organizationdocument')

        organization_document = OrganizationDocument(
            organization=Organization.objects.get(id=100),
            version=input['version'],
            document_type=input['document_type'],
            date_start=input['date_start'],
            document=get_content_file_from_base64_str(data_str=input['document'], file_name=input['document_file_name'])
        )

        if 'date_end' in input:
            date_end = input['date_end']    

        organization_document.save()

        return CreateOrganizationDocument(organization_document = organization_document)


class UpdateOrganizationDocument(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        # document_file_name = graphene.String(required=False)
        # document_type = graphene.String(required=False)
        version = graphene.String(required=False)
        date_start = graphene.types.datetime.Date(required=False)
        date_end = graphene.types.datetime.Date(required=False)
        # document = graphene.String(required=False)

    organization_document = graphene.Field(OrganizationDocumentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_organizationdocument')

        #TODO Validator; if supplying document_type, document_file_name is also required

        rid = get_rid(input['id'])
        organization_document = OrganizationDocument.objects.get(id=rid.id)
        if not organization_document:
            raise Exception('Invalid Organization Document ID!')

        # if 'document_type' in input:
        #     organization_document.document_type = input['document_type']

        if 'version' in input:
            organization_document.version = input['version']

        if 'date_start' in input:
            organization_document.date_start = input['date_start']

        if 'date_end' in input:
            organization_document.date_end = input['date_end']

        # if 'document' in input:
        #     organization_document.document = get_content_file_from_base64_str(data=input['document'])

        organization_document.save()

        return UpdateOrganizationDocument(organization_document=organization_document)


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

        ok = bool(organization_document.delete())

        return DeleteOrganizationDocument(ok=ok)


class OrganizationDocumentMutation(graphene.ObjectType):
    delete_organization_document = DeleteOrganizationDocument.Field()
    create_organization_document = CreateOrganizationDocument.Field()
    update_organization_document = UpdateOrganizationDocument.Field()
