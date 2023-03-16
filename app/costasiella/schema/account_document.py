from django.utils.translation import gettext as _
from django.conf import settings

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
    url_protected_document = graphene.String()


class AccountDocumentNode(DjangoObjectType):
    class Meta:
        model = AccountDocument
        # Fields to include
        fields = (
            'account',
            'description',
            'document',
            'created_at',
            'updated_at'
        )
        filter_fields = ['account']
        interfaces = (graphene.relay.Node, AccountDocumentNodeInterface)

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountdocument')

        return self._meta.model.objects.get(id=id)

    def resolve_url_protected_document(self, info):
        # This is here for compatibility reasons.
        # TODO: Update frontend to query document.url field instead
        if self.document:
            return self.document.url
        else:
            return ''


class AccountDocumentQuery(graphene.ObjectType):
    account_documents = DjangoFilterConnectionField(AccountDocumentNode)
    account_document = graphene.relay.Node.Field(AccountDocumentNode)

    def resolve_account_documents(self, info, account, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountdocument')

        rid = get_rid(account)
        account_id = rid.id

        return AccountDocument.objects.filter(account=account_id).order_by('-description')


def validate_create_input(input):
    """
    Validate input
    """
    result = {}

    if 'document' in input or 'document_file_name' in input:
        if not (input.get('document', None) and input.get('document_file_name', None)):
            raise Exception(_('When setting "document" or "documentFileName", both fields need to be present and set'))

    # Check account
    if 'account' in input:
        if input['account']:
            rid = get_rid(input['account'])
            account = Account.objects.get(id=rid.id)
            result['account'] = account
            if not account:
                raise Exception('Invalid Account ID!')

    return result


class CreateAccountDocument(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        document_file_name = graphene.String(required=True)
        document = graphene.String(required=True)  # File als base64 encoded string
        description = graphene.String(required=True)

    account_document = graphene.Field(AccountDocumentNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountdocument')

        result = validate_create_input(input)

        account_document = AccountDocument(
            account=result['account'],
            description=input['description'],
            document=get_content_file_from_base64_str(data_str=input['document'],
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

        ok = bool(account_document.delete())

        return DeleteAccountDocument(ok=ok)


class AccountDocumentMutation(graphene.ObjectType):
    delete_account_document = DeleteAccountDocument.Field()
    create_account_document = CreateAccountDocument.Field()
    update_account_document = UpdateAccountDocument.Field()
