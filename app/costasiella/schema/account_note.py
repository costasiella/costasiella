import graphene
import validators

from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, AccountNote
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
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

    if 'teacher_note' not in input and 'backoffice_note' not in input:
        raise Exception(_('Either teacherNote or backofficeNote has to be set!'))

    return result


class AccountNoteNode(DjangoObjectType):
    class Meta:
        model = AccountNote
        filter_fields = ['account', 'teacher_note', 'backoffice_note']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountnote')

        return self._meta.model.objects.get(id=id)


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
        require_login_and_permission(user, 'costasiella.view_account_note')

        rid = get_rid(kwargs.get('account', user.id))
        account_id = rid.id

        return AccountNote.objects.filter(account=account_id).order_by('-created_at')


class CreateAccountNote(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        backoffice_note = graphene.Boolean(required=False)
        teacher_note = graphene.Boolean(required=False)
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
            note_by=user
        )

        if 'teacher_note' in input:
            account_note.teacher_note = input['teacher_note']
            
        if 'backoffice_note' in input:
            account_note.backoffice_note = input['backoffice_note']
            
        if 'injury' in input:
            account_note.injury = input['injury']

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

        ok = account_note.delete()

        return DeleteAccountNote(ok=ok)


class AccountNoteMutation(graphene.ObjectType):
    create_account_note = CreateAccountNote.Field()
    delete_account_note = DeleteAccountNote.Field()
    update_account_note = UpdateAccountNote.Field()
