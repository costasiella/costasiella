from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import Account, AccountMembership, FinancePaymentMethod, OrganizationMembership
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

    # Fetch & check organization membership
    rid = get_rid(input['organization_membership'])
    organization_membership = OrganizationMembership.objects.get(pk=rid.id)
    result['organization_membership'] = organization_membership
    if not organization_membership:
        raise Exception(_('Invalid Organization Membership ID!'))

    # Check finance payment method
    if 'finance_payment_method' in input:
        if input['finance_payment_method']:
            rid = get_rid(input['finance_payment_method'])
            finance_payment_method = FinancePaymentMethod.objects.filter(id=rid.id).first()
            result['finance_payment_method'] = finance_payment_method
            if not finance_payment_method:
                raise Exception(_('Invalid Finance Payment Method ID!'))

    return result


class AccountMembershipNode(DjangoObjectType):   
    class Meta:
        model = AccountMembership
        # Fields to include
        fields = (
            'account',
            'organization_membership',
            'finance_payment_method',
            'date_start',
            'date_end',
            'note',
            'created_at',
            'updated_at'
        )
        filter_fields = ['account', 'date_start', 'date_end']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountmembership')

        return self._meta.model.objects.get(id=id)


class AccountMembershipQuery(graphene.ObjectType):
    account_memberships = DjangoFilterConnectionField(AccountMembershipNode)
    account_membership = graphene.relay.Node.Field(AccountMembershipNode)

    def resolve_account_memberships(self, info, account, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountmembership')

        rid = get_rid(account)

        ## return everything:
        return AccountMembership.objects.filter(account=rid.id).order_by('date_start')


class CreateAccountMembership(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        organization_membership = graphene.ID(required=True)
        finance_payment_method = graphene.ID(required=False, default_value=None)
        date_start = graphene.types.datetime.Date(required=True)
        note = graphene.String(required=False, default_value="")

    account_membership = graphene.Field(AccountMembershipNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountmembership')

        # Validate input
        result = validate_create_update_input(input, update=False)

        sales_dude = SalesDude()
        sales_result = sales_dude.sell_membership(
            account=result['account'],
            organization_membership=result['organization_membership'],
            date_start=input['date_start'],
            finance_payment_method=result.get('finance_payment_method', None),
            note=input['note'],
            create_invoice=True,
        )

        account_membership = sales_result['account_membership']

        return CreateAccountMembership(account_membership=account_membership)


class UpdateAccountMembership(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        organization_membership = graphene.ID(required=True)
        finance_payment_method = graphene.ID(required=False, default_value="")
        date_start = graphene.types.datetime.Date(required=True)
        date_end = graphene.types.datetime.Date(required=False, default_value=None)
        note = graphene.String(required=False, default_value="")
        
    account_membership = graphene.Field(AccountMembershipNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountmembership')
    
        rid = get_rid(input['id'])
        account_membership = AccountMembership.objects.filter(id=rid.id).first()
        if not account_membership:
            raise Exception('Invalid Account Membership ID!')

        result = validate_create_update_input(input, update=True)

        account_membership.organization_membership=result['organization_membership']
        account_membership.date_start=input['date_start']

        if 'date_end' in input:
            # Allow None as a value to be able to NULL date_end
            account_membership.date_end = input['date_end']

        if 'note' in input:
            account_membership.note = input['note']

        if 'finance_payment_method' in result:
            account_membership.finance_payment_method = result['finance_payment_method']
        
        account_membership.save(force_update=True)

        return UpdateAccountMembership(account_membership=account_membership)


class DeleteAccountMembership(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountmembership')

        rid = get_rid(input['id'])
        account_membership = AccountMembership.objects.filter(id=rid.id).first()
        if not account_membership:
            raise Exception('Invalid Account Membership ID!')

        ok = bool(account_membership.delete())

        return DeleteAccountMembership(ok=ok)


class AccountMembershipMutation(graphene.ObjectType):
    create_account_membership = CreateAccountMembership.Field()
    delete_account_membership = DeleteAccountMembership.Field()
    update_account_membership = UpdateAccountMembership.Field()