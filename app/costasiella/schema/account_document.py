from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import Account, AccountDocument
from ..modules.gql_tools import require_login_and_permission, get_rid, get_content_file_from_base64_str
from ..modules.messages import Messages

from sorl.thumbnail import get_thumbnail

m = Messages()

class AccountDocumentNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    url_document = graphene.String()


class AccountDocumentNode(DjangoObjectType):
    def resolve_url_document(self, info):
        if self.document:
            return self.document.url
        else:
            return ''
    
    class Meta:
        model = AccountDocument
        filter_fields = ['account']
        interfaces = (graphene.relay.Node, AccountDocumentNodeInterface)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountdocument')

        return self._meta.model.objects.get(id=id)


class AccountDocumentQuery(graphene.ObjectType):
    account_documents = DjangoFilterConnectionField(AccountDocumentNode)
    account_document = graphene.relay.Node.Field(AccountDocumentNode)

    def resolve_account_documents(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountdocument')

        return AccountDocument.objects.all.order_by('-description')


class CreateAccountDocument(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        document_file_name = graphene.String(required=True)
        document = graphene.String(required=True) # File als base64 encoded string
        description = graphene.String(required=True)

    account_document = graphene.Field(AccountDocumentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountdocument')

        account_document = AccountDocument(
            account = Account.objects.get(id=100),
            description = input['ddescription'],
            document = get_content_file_from_base64_str(data_str=input['document'],
                                                        file_name=input['document_file_name'])
        )

        account_document.save()

        return CreateAccountDocument(account_document=account_document)


class UpdateAccountDocument(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        description = graphene.String(required=False)

    account_document = graphene.Field(AccountDocumentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountdocument')

        rid = get_rid(input['id'])
        account_document = AccountDocument.objects.get(id=rid.id)
        if not account_document:
            raise Exception('Invalid Account Document ID!')

        if 'description' in input:
            account_document.description = input['description']

        account_document.save()

        return UpdateAccountDocument(account_document=account_document)


class DeleteAccountDocument(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    
    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountdocument')

        rid = get_rid(input['id'])
        account_document = AccountDocument.objects.get(id=rid.id)
        if not account_document:
            raise Exception('Invalid Account Document ID!')

        ok = account_document.delete()

        return DeleteAccountDocument(ok=ok)


class AccountDocumentMutation(graphene.ObjectType):
    delete_account_document = DeleteAccountDocument.Field()
    create_account_document = CreateAccountDocument.Field()
    update_account_document = UpdateAccountDocument.Field()
