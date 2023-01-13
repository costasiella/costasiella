import graphene
import validators

from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, AccountBankAccount
from ..modules.gql_tools import require_login, require_login_and_permission, require_permission, get_rid
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

    if 'number' in input:
        system_setting_dude = SystemSettingDude()
        finance_bank_accounts_iban = system_setting_dude.get('finance_bank_accounts_iban')

        if finance_bank_accounts_iban == 'true':
            number = input['number'].strip()
            if not validators.iban(number):
                raise Exception(_('Number is not a valid IBAN!'))

    return result


class AccountBankAccountNode(DjangoObjectType):
    class Meta:
        model = AccountBankAccount
        # Fields to include
        fields = (
            'account',
            'number',
            'holder',
            'bic',
            'created_at',
            'updated_at',
            # Reverse relations
            'mandates'
        )
        filter_fields = ['account']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user

        account_bank_account = self._meta.model.objects.get(id=id)
        if not account_bank_account.account == user:
            require_login_and_permission(user, 'costasiella.view_accountbankaccount')

        return account_bank_account


class AccountBankAccountQuery(graphene.ObjectType):
    account_bank_accounts = DjangoFilterConnectionField(AccountBankAccountNode)
    account_bank_account = graphene.relay.Node.Field(AccountBankAccountNode)

    def resolve_account_bank_accounts(self, info, **kwargs):
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

        if user.has_perm('costasiella.view_accountbankaccount') and 'account' in kwargs and kwargs['account']:
            rid = get_rid(kwargs.get('account', user.id))
            account_id = rid.id
        else:
            account_id = user.id

        # Allow user to specify account
        return AccountBankAccount.objects.filter(account=account_id)


class CreateAccountBankAccount(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        number = graphene.String(required=True)
        holder = graphene.String(required=True)
        bic = graphene.String(required=False)

    account_bank_account = graphene.Field(AccountBankAccountNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountbankaccount')

        # Validate input
        result = validate_create_update_input(input, update=False)

        account_bank_account = AccountBankAccount(
            account=result['account'],
            number=result['number'],
            holder=result['holder'],
        )

        if 'bic' in input:
            account_bank_account.bic = input['bic']

        return CreateAccountBankAccount(account_bank_account=account_bank_account)


class UpdateAccountBankAccount(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        number = graphene.String(required=False)
        holder = graphene.String(required=False)
        bic = graphene.String(required=False)
        
    account_bank_account = graphene.Field(AccountBankAccountNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login(user)

        rid = get_rid(input['id'])
        account_bank_account = AccountBankAccount.objects.filter(id=rid.id).first()
        if not account_bank_account:
            raise Exception('Invalid Account Bank Account ID!')

        # Allow users to update their own bank account without additional permissions
        if not user.id == account_bank_account.account.id:
            require_permission(user, 'costasiella.change_accountbankaccount')

        result = validate_create_update_input(input, update=True)
        
        if 'number' in input:
            account_bank_account.number = input['number']
            
        if 'holder' in input:
            account_bank_account.holder = input['holder']
            
        if 'bic' in input:
            account_bank_account.bic = input['bic']
        
        account_bank_account.save()

        return UpdateAccountBankAccount(account_bank_account=account_bank_account)


class DeleteAccountBankAccount(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountbankaccount')

        rid = get_rid(input['id'])
        account_bank_account = AccountBankAccount.objects.filter(id=rid.id).first()
        if not account_bank_account:
            raise Exception('Invalid Account Bank Account ID!')

        ok = bool(account_bank_account.delete())

        return DeleteAccountBankAccount(ok=ok)


class AccountBankAccountMutation(graphene.ObjectType):
    # create_account_bank_account = CreateAccountBankAccount.Field()
    # delete_account_bank_account = DeleteAccountBankAccount.Field()
    update_account_bank_account = UpdateAccountBankAccount.Field()
