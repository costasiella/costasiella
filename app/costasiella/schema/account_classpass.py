import graphene

from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from ..models import Account, AccountClasspass, FinancePaymentMethod, OrganizationClasspass
from ..modules.gql_tools import require_login, require_login_and_permission, get_rid
from ..modules.messages import Messages
from ..dudes import SalesDude

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


class AccountClasspassInterface(graphene.Interface):
    id = graphene.GlobalID()
    classes_remaining_display = graphene.String()
    is_expired = graphene.Boolean()


class AccountClasspassNode(DjangoObjectType):   
    class Meta:
        model = AccountClasspass
        # Fields to include
        fields = (
            'account',
            'organization_classpass',
            'date_start',
            'date_end',
            'note',
            'classes_remaining',
            'created_at',
            'updated_at',
            # Reverse relations
            'classes',
            'invoice_items'
        )
        filter_fields = {
            'account': ['exact'],
            'date_start': ['exact', 'lte', 'gte'],
            'date_end': ['exact', 'lte', 'gte'],
            'organization_classpass__trial_pass': ['exact']
        }
        interfaces = (graphene.relay.Node, AccountClasspassInterface, )

    def resolve_classes_remaining_display(self, info):
        if self.organization_classpass.unlimited:
            return _('Unlimited')
        else:
            return self.classes_remaining

    def resolve_is_expired(self, info):
        return self.is_expired()

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountclasspass')

        return self._meta.model.objects.get(id=id)


class AccountClasspassQuery(graphene.ObjectType):
    account_classpasses = DjangoFilterConnectionField(AccountClasspassNode)
    account_classpass = graphene.relay.Node.Field(AccountClasspassNode)

    def resolve_account_classpasses(self, info, **kwargs):
        """
        Return classpasses for an account
        - Require login
        - Always return users' own info when no view_accountclasspass permission
        - Allow user to specify the account
        :param info:
        :param account:
        :param kwargs:
        :return:
        """
        user = info.context.user
        require_login(user)

        if user.has_perm('costasiella.view_accountclasspass') and 'account' in kwargs and kwargs['account']:
            rid = get_rid(kwargs.get('account', user.id))
            account_id = rid.id
            qs = AccountClasspass.objects.filter(account=account_id)
        elif user.has_perm('costasiella.view_accountclasspass'):
            qs = AccountClasspass.objects.all()
        else:
            # A safeguard that ensures users without permission can only query their own classpasses
            account_id = user.id
            qs = AccountClasspass.objects.filter(account=account_id)

        # Allow user to specify account
        return qs.order_by('-date_start')


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
            account=result['account'],
            organization_classpass=result['organization_classpass'],
            date_start=input['date_start'],
            note=input['note'] if 'note' in input else "",
            create_invoice=True
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
        account_classpass.organization_classpass = result['organization_classpass']
        account_classpass.date_start = input['date_start']

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

        ok = bool(account_classpass.delete())

        return DeleteAccountClasspass(ok=ok)


class AccountClasspassMutation(graphene.ObjectType):
    create_account_classpass = CreateAccountClasspass.Field()
    delete_account_classpass = DeleteAccountClasspass.Field()
    update_account_classpass = UpdateAccountClasspass.Field()