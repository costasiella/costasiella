from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import Account, AccountClasspass, FinancePaymentMethod, OrganizationClasspass
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..dudes.sales_dude import SalesDude

from sorl.thumbnail import get_thumbnail

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

    # Fetch & check organization classpass
    rid = get_rid(input['organization_classpass'])
    organization_classpass = OrganizationClasspass.objects.get(pk=rid.id)
    result['organization_classpass'] = organization_classpass
    if not organization_classpass:
        raise Exception(_('Invalid Organization Classpass ID!'))



    return result


class AccountClasspassNode(DjangoObjectType):   
    class Meta:
        model = AccountClasspass
        filter_fields = ['account', 'date_start', 'date_end']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountclasspass')

        return self._meta.model.objects.get(id=id)


class AccountClasspassQuery(graphene.ObjectType):
    account_classpasses = DjangoFilterConnectionField(AccountClasspassNode)
    account_classpass = graphene.relay.Node.Field(AccountClasspassNode)


    def resolve_account_classpasses(self, info, account, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountclasspass')

        rid = get_rid(account)

        ## return everything:
        return AccountClasspass.objects.filter(account=rid.id).order_by('date_start')


class CreateAccountClasspass(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        organization_classpass = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        note = graphene.String(required=False, default_value="")
        

    account_classpass = graphene.Field(AccountClasspassNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountclasspass')

        # Validate input
        result = validate_create_update_input(input, update=False)

        sales_dude = SalesDude()
        sales_result = sales_dude.sell_classpass(
            account = result['account'],
            organization_classpass = result['organization_classpass'],
            date_start = input['date_start'],
            note = input['note'] if 'note' in input else "",
            create_invoice = True
        )

        account_classpass = sales_result['account_classpass']

        return CreateAccountClasspass(account_classpass=account_classpass)


class UpdateAccountClasspass(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        organization_classpass = graphene.ID(required=True)
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        note = graphene.String(required=False, default_value="")
        
    account_classpass = graphene.Field(AccountClasspassNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountclasspass')

    
        rid = get_rid(input['id'])
        account_classpass = AccountClasspass.objects.filter(id=rid.id).first()
        if not account_classpass:
            raise Exception('Invalid Account Classpass ID!')

        result = validate_create_update_input(input, update=True)

        account_classpass.organization_classpass=result['organization_classpass']
        account_classpass.date_start=input['date_start']

        if 'date_end' in input:
            # Allow None as a value to be able to NULL date_end
            account_classpass.date_end = input['date_end']

        if 'note' in input:
            account_classpass.note = input['note']
        
        account_classpass.save(force_update=True)

        return UpdateAccountClasspass(account_classpass=account_classpass)


class DeleteAccountClasspass(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountclasspass')

        rid = get_rid(input['id'])
        account_classpass = AccountClasspass.objects.filter(id=rid.id).first()
        if not account_classpass:
            raise Exception('Invalid Account Classpass ID!')

        ok = account_classpass.delete()

        return DeleteAccountClasspass(ok=ok)


class AccountClasspassMutation(graphene.ObjectType):
    create_account_classpass = CreateAccountClasspass.Field()
    delete_account_classpass = DeleteAccountClasspass.Field()
    update_account_classpass = UpdateAccountClasspass.Field()