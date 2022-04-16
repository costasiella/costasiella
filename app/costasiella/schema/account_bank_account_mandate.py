import graphene
import uuid

from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import AccountBankAccount, AccountBankAccountMandate
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
        rid = get_rid(input['account_bank_account'])
        account_bank_account = AccountBankAccount.objects.filter(id=rid.id).first()
        result['account_bank_account'] = account_bank_account
        if not account_bank_account:
            raise Exception(_('Invalid Account Bank Account ID!'))

    return result


class AccountBankAccountMandateNode(DjangoObjectType):
    class Meta:
        model = AccountBankAccountMandate
        # Fields to include
        fields = (
            'account_bank_account',
            'reference',
            'content',
            'signature_date',
            'created_at',
            'updated_at'
        )
        filter_fields = ['account_bank_account']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountbankaccountmandate')

        return self._meta.model.objects.get(id=id)


class AccountBankAccountMandateQuery(graphene.ObjectType):
    account_bank_account_mandates = DjangoFilterConnectionField(AccountBankAccountMandateNode)
    account_bank_account_mandate = graphene.relay.Node.Field(AccountBankAccountMandateNode)

    def resolve_account_bank_account_mandates(self, info, **kwargs):
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
        require_login(user)

        if user.has_perm('costasiella.view_accountbankaccountmandate') and 'account_bank_account' in kwargs:
            rid = get_rid(kwargs['account_bank_account'])
            account_bank_account_id = rid.id
        else:
            # Fetch bank account for user
            qs = AccountBankAccount.objects.filter(account=user)
            account_bank_account = qs.first()
            account_bank_account_id = account_bank_account.id

        # Allow user to specify account
        return AccountBankAccountMandate.objects.filter(account_bank_account=account_bank_account_id)


class CreateAccountBankAccountMandate(graphene.relay.ClientIDMutation):
    class Input:
        account_bank_account = graphene.ID(required=True)
        reference = graphene.String(required=False, default_value=str(uuid.uuid4()))
        content = graphene.String(required=False)
        signature_date = graphene.types.datetime.Date()

    account_bank_account_mandate = graphene.Field(AccountBankAccountMandateNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountbankaccountmandate')

        # Validate input
        result = validate_create_update_input(input, update=False)

        account_bank_account_mandate = AccountBankAccountMandate(
            account_bank_account=result['account_bank_account']
        )

        if 'reference' in input:
            account_bank_account_mandate.reference = input['reference']

        if 'content' in input:
            account_bank_account_mandate.content = input['content']

        if 'signature_date' in input:
            account_bank_account_mandate.signature_date = input['signature_date']

        account_bank_account_mandate.save()

        return CreateAccountBankAccountMandate(account_bank_account_mandate=account_bank_account_mandate)


class UpdateAccountBankAccountMandate(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        reference = graphene.String(required=False)
        content = graphene.String(required=False)
        signature_date = graphene.types.datetime.Date()
        
    account_bank_account_mandate = graphene.Field(AccountBankAccountMandateNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountbankaccountmandate')
    
        rid = get_rid(input['id'])
        account_bank_account_mandate = AccountBankAccountMandate.objects.filter(id=rid.id).first()
        if not account_bank_account_mandate:
            raise Exception('Invalid Account Bank Account Mandate ID!')

        if 'reference' in input:
            account_bank_account_mandate.reference = input['reference']

        if 'content' in input:
            account_bank_account_mandate.content = input['content']

        if 'signature_date' in input:
            account_bank_account_mandate.signature_date = input['signature_date']
        
        account_bank_account_mandate.save()

        return UpdateAccountBankAccountMandate(account_bank_account_mandate=account_bank_account_mandate)


class DeleteAccountBankAccountMandate(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountbankaccountmandate')

        rid = get_rid(input['id'])
        account_bank_account_mandate = AccountBankAccountMandate.objects.filter(id=rid.id).first()
        if not account_bank_account_mandate:
            raise Exception('Invalid Account Bank Account Mandate ID!')

        ok = bool(account_bank_account_mandate.delete())

        return DeleteAccountBankAccountMandate(ok=ok)


class AccountBankAccountMandateMutation(graphene.ObjectType):
    create_account_bank_account_mandate = CreateAccountBankAccountMandate.Field()
    delete_account_bank_account_mandate = DeleteAccountBankAccountMandate.Field()
    update_account_bank_account_mandate = UpdateAccountBankAccountMandate.Field()
