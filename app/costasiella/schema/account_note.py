import graphene
import validators

from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, AccountNote
from ..models.choices.account_note_types import get_account_note_types
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..dudes.system_setting_dude import SystemSettingDude

m = Messages()


def validate_create_update_input(input, update=False):
    """
    Validate input
    """ 
    result = {}

    # Fetch & check account
    if not update:
        # Create only
        rid = get_rid(input['account'])
        account = Account.objects.filter(id=rid.id).first()
        result['account'] = account
        if not account:
            raise Exception(_('Invalid Account ID!'))

        note_types = []
        for item in get_account_note_types():
            note_types.append(item[0])

        if input['note_type'] not in note_types:
            raise Exception(_('noteType should be INSTRUCTORS or BACKOFFICE!'))

        result['note_type'] = input['note_type']

    return result


class AccountNoteNode(DjangoObjectType):
    class Meta:
        model = AccountNote
        # Fields to include
        fields = (
            'account',
            'note_by',
            'note_type',
            'note',
            'injury',
            'processed',
            'created_at',
            'updated_at'
        )
        filter_fields = ['account', 'note_type']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountnote')

        note = self._meta.model.objects.get(id=id)
        if user.has_perm('costasiella.view_accountnoteinstructors') and note.note_type == 'INSTRUCTORS':
            return note
        elif user.has_perm('costasiella.view_accountnotebackoffice') and note.note_type == 'BACKOFFICE':
            return note


class AccountNoteQuery(graphene.ObjectType):
    account_notes = DjangoFilterConnectionField(AccountNoteNode)
    account_note = graphene.relay.Node.Field(AccountNoteNode)

    def resolve_account_notes(self, info, **kwargs):
        """
        Return bank accounts for an account
        - Require login
        - Always return users' own info when no view_accountbank_account permission
        - Allow user to specify the account
        :param info:
        :param account:
        :param kwargs:
        :return:
        """
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountnote')

        # Apply requested filter of user has the permission for it, if not don't return anything

        rid = get_rid(kwargs.get('account', user.id))
        account_id = rid.id

        return AccountNote.objects.filter(account=account_id).order_by('-created_at')


class CreateAccountNote(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        note_type = graphene.String(required=True)
        injury = graphene.Boolean(required=False)
        note = graphene.String(required=True)

    account_note = graphene.Field(AccountNoteNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountnote')

        # Validate input
        result = validate_create_update_input(input, update=False)

        account_note = AccountNote(
            account=result['account'],
            note=input['note'],
            note_type=result['note_type'],
            note_by=user
        )
            
        if 'injury' in input:
            account_note.injury = input['injury']

        account_note.save()

        return CreateAccountNote(account_note=account_note)


class UpdateAccountNote(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        injury = graphene.Boolean(required=False)
        note = graphene.String(required=True)
        
    account_note = graphene.Field(AccountNoteNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountnote')
    
        rid = get_rid(input['id'])
        account_note = AccountNote.objects.filter(id=rid.id).first()
        if not account_note:
            raise Exception('Invalid Account Note ID!')

        if 'note' in input:
            account_note.note = input['note']
            
        if 'injury' in input:
            account_note.injury = input['injury']
        
        account_note.save()

        return UpdateAccountNote(account_note=account_note)


class DeleteAccountNote(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountnote')

        rid = get_rid(input['id'])
        account_note = AccountNote.objects.filter(id=rid.id).first()
        if not account_note:
            raise Exception('Invalid Account Note ID!')

        ok = bool(account_note.delete())

        return DeleteAccountNote(ok=ok)


class AccountNoteMutation(graphene.ObjectType):
    create_account_note = CreateAccountNote.Field()
    delete_account_note = DeleteAccountNote.Field()
    update_account_note = UpdateAccountNote.Field()
