from django.utils.translation import gettext as _

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

import graphene
from graphene_django.converter import convert_django_field
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from allauth.account.models import EmailAddress

from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.encrypted_fields import EncryptedTextField

@convert_django_field.register(EncryptedTextField)
def convert_json_field_to_string(field, registry=None):
    return graphene.String()


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class AccountNode(DjangoObjectType):
    class Meta:
        model = get_user_model()
        filter_fields = ['is_active']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_account')
        #TODO: Add permission for accounts to get their own info or all info with view permission

        return self._meta.model.objects.get(id=id)


class GroupNode(DjangoObjectType):
    class Meta:
        model = Group
        filter_fields = ['name']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_group')

        return self._meta.model.objects.get(id=id)


class PermissionNode(DjangoObjectType):
    class Meta:
        model = Permission
        filter_fields = ['name']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_permission')

        return self._meta.model.objects.get(id=id)


class AccountQuery(graphene.AbstractType):
    user = graphene.Field(UserType)
    account = graphene.relay.Node.Field(AccountNode)
    accounts = DjangoFilterConnectionField(AccountNode)
    group = graphene.relay.Node.Field(GroupNode)
    groups = DjangoFilterConnectionField(GroupNode)
    permission = graphene.relay.Node.Field(PermissionNode)
    permissions = DjangoFilterConnectionField(PermissionNode)


    def resolve_user(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')

        return user


    def resolve_accounts(self, info, is_active=False, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_account')

        query_set =  get_user_model().objects.filter(
            is_active=is_active, 
            is_superuser=False
        )

        return query_set.order_by('first_name')


    def resolve_groups(self, info):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_group')

        return Group.objects.all()


    def resolve_permissions(self, info):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_permission')

        return Permission.objects.all()


class CreateAccount(graphene.relay.ClientIDMutation):
    class Input:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)

    account = graphene.Field(AccountNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_account')

        # verify email unique
        query_set = get_user_model().objects.filter(
            email = input['email']
        )

        #Don't insert duplicate records in the DB. If this records exist, fetch and return it
        if query_set.exists():
            raise Exception(_('An account is already registered with this e-mail address'))

        account = get_user_model()(
            first_name = input['first_name'],
            last_name = input['last_name'],
            email = input['email'],
            username = input['email']
        )
        account.save()

        # Insert Allauth email address 
        email_address = EmailAddress(
            user = account,
            email = account.email,
            verified = True,
            primary = True
        )
        email_address.save()

        return CreateAccount(account=account)
#         return CreateAccount(user=user)


def validate_create_update_input(account, input, update=False):
    """
    Validate input
    """ 
    # result = {}

    # verify email unique
    query_set = get_user_model().objects.filter(
        ~Q(pk=account.pk),
        Q(email=input['email'])
    )

    # Don't insert duplicate emails into the DB.
    if query_set.exists():
        raise Exception(_('Unable to save, an account is already registered with this e-mail address'))

    # Verify gender
    genders = [
        'M', 'F', 'X'
    ]

    if input['gender']:
        if not input['gender'] in genders:
            raise Exception(_("Please specify gender as M, F or X (for other)"))

    # Verify country code
    if input['country']:
        country_codes = []
        for country in settings.ISO_COUNTRY_CODES:
            country_codes.append(country['Code'])
        
        if not input['country'] in country_codes:
            raise Exception(_("Please specify the country as ISO country code, eg. 'NL'"))


class UpdateAccount(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        address = graphene.String(requires=False, default_value="")
        postcode = graphene.String(requires=False, default_value="")
        city = graphene.String(requires=False, default_value="")
        country = graphene.String(requires=False, default_value="")
        phone = graphene.String(requires=False, default_value="")
        mobile = graphene.String(requires=False, default_value="")
        emergency = graphene.String(requires=False, default_value="")
        gender = graphene.String(requires=False, default_value="")
        date_of_birth = graphene.types.datetime.Date(required=False, default_value="")

    account = graphene.Field(AccountNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_account')

        # print(input)

        rid = get_rid(input['id'])
        account = get_user_model().objects.filter(id=rid.id).first()
        if not account:
            raise Exception('Invalid Account ID!')

        validate_create_update_input(account, input, update=True)


        account.first_name = input['first_name']
        account.last_name = input['last_name']
        account.email = input['email']
        account.username = input['email']
        # Only update these fields if input has been passed
        if input['address']:
            account.address = input['address']
        if input['postcode']:
            account.postcode = input['postcode']
        if input['city']:
            account.city = input['city']
        if input['country']:
            account.country = input['country']
        if input['phone']:
            account.phone = input['phone']
        if input['mobile']:
            account.mobile = input['mobile']
        if input['emergency']:
            account.emergency = input['emergency']
        if input['gender']:
            account.gender = input['gender']
        if input['date_of_birth']:
            account.date_of_birth = input['date_of_birth']
        account.save()

        # Update Allauth email address 
        email_address = EmailAddress.objects.filter(user=account).first()
        email_address.email = account.email
        email_address.save()

        return UpdateAccount(account=account)


class UpdateAccountActive(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        is_active = graphene.Boolean(required=True)

    account = graphene.Field(AccountNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_account')

        rid = get_rid(input['id'])

        account = get_user_model().objects.filter(id=rid.id).first()
        if not account:
            raise Exception('Invalid Account ID!')

        account.is_active = input['is_active']
        account.save(force_update=True)

        return UpdateAccountActive(account=account)


class DeleteAccount(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_account')

        rid = get_rid(input['id'])
        account = get_user_model().objects.filter(id=rid.id).first()
        if not account:
            raise Exception('Invalid Account ID!')

        ok = account.delete()

        return DeleteAccount(ok=ok)


class AccountMutation(graphene.ObjectType):
    create_account = CreateAccount.Field()
    update_account = UpdateAccount.Field()
    update_account_active = UpdateAccountActive.Field()
    delete_account = DeleteAccount.Field()

