from django.utils.translation import gettext as _

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

import graphene
from graphql import GraphQLError
from graphql_relay import to_global_id
from graphql import GraphQLError
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password
from graphene_django.converter import convert_django_field
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from allauth.account.models import EmailAddress
from ..models import AccountBankAccount, AccountTeacherProfile

from ..modules.gql_tools import require_login, \
    require_permission, \
    require_login_and_permission, \
    require_login_and_one_of_permissions, \
    require_login_and_one_of_permission_or_own_account, \
    get_rid, \
    get_error_code

from ..modules.encrypted_fields import EncryptedTextField


@convert_django_field.register(EncryptedTextField)
def convert_json_field_to_string(field, registry=None):
    return graphene.String()


class UserType(DjangoObjectType):
    account_id = graphene.ID()

    class Meta:
        model = get_user_model()

    def resolve_account_id(self, info):
        return to_global_id("AccountNode", info.context.user.id)


class AccountNode(DjangoObjectType):
    class Meta:
        model = get_user_model()
        
        # fields=() # Fields to include
        exclude = ['password']  # Fields to exclude
        filter_fields = {
            'full_name': ['icontains', 'exact'],
            'is_active': ['exact'],
            'customer': ['exact'],
            'teacher': ['exact'],
            'employee': ['exact'],
        }
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_one_of_permissions(user, [
            'costasiella.view_account',
            'costasiella.view_selfcheckin'
        ])

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
        require_login(user)

        return user

    def resolve_accounts(self, info, is_active=False, **kwargs):
        user = info.context.user
        require_login_and_one_of_permissions(user, [
            'costasiella.view_account',
            'costasiella.view_selfcheckin'
        ])

        query_set = get_user_model().objects.filter(
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
            email=input['email']
        )

        # Don't insert duplicate records in the DB. If this records exist, fetch and return it
        if query_set.exists():
            raise Exception(_('An account is already registered with this e-mail address'))

        account = get_user_model()(
            first_name=input['first_name'],
            last_name=input['last_name'],
            email=input['email'],
            username=input['email']
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

        # Create Teacher profile
        account_teacher_profile = AccountTeacherProfile(
            account=account
        )
        account_teacher_profile.save()

        # Create Bank account record
        account_bank_account = AccountBankAccount(
            account=account
        )
        account_bank_account.save()

        return CreateAccount(account=account)
#         return CreateAccount(user=user)


def validate_create_update_input(account, input, update=False):
    """
    Validate input
    """ 
    # result = {}

    # verify email unique
    if 'email' in input:
        query_set = get_user_model().objects.filter(
            ~Q(pk=account.pk),
            Q(email=input['email'])
        )
        # Don't insert duplicate emails into the DB.
        if query_set.exists():
            raise Exception(_('Unable to save, an account is already registered with this e-mail address'))

    # Verify gender
    if input.get('gender', None):
        genders = ['M', 'F', 'X']
        if not input['gender'] in genders:
            raise Exception(_("Please specify gender as M, F or X (for other)"))

    # Verify country code
    if input.get('country', None):
        country_codes = []
        for country in settings.ISO_COUNTRY_CODES:
            country_codes.append(country['Code'])
        
        if not input['country'] in country_codes:
            raise Exception(_("Please specify the country as ISO country code, eg. 'NL'"))


class UpdateAccount(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        # password = graphene.String(required=False)
        customer = graphene.Boolean(required=False)
        teacher = graphene.Boolean(required=False)
        employee = graphene.Boolean(required=False)
        first_name = graphene.String(required=False)
        last_name = graphene.String(required=False)
        email = graphene.String(required=False)
        address = graphene.String(required=False)
        postcode = graphene.String(required=False)
        city = graphene.String(required=False)
        country = graphene.String(required=False)
        phone = graphene.String(required=False)
        mobile = graphene.String(required=False)
        emergency = graphene.String(required=False)
        gender = graphene.String(required=False)
        date_of_birth = graphene.types.datetime.Date(required=False)

    account = graphene.Field(AccountNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login(user)
        # print(input)

        rid = get_rid(input['id'])
        account = get_user_model().objects.filter(id=rid.id).first()
        if not account:
            raise Exception('Invalid Account ID!')

        change_permission = 'costasiella.change_account'

        # Allow users to update their own account without additional permissions
        if not user.id == account.id:
            require_permission(user, change_permission)

        validate_create_update_input(account, input, update=True)

        # Only process these fields when a user has the "change_account" permission. Users shouldn't be able to
        # change this for their own account
        if user.has_perm(change_permission):
            if 'customer' in input:
                account.customer = input['customer']
            if 'teacher' in input:
                account.teacher = input['teacher']
            if 'employee' in input:
                account.employee = input['employee']

        # Users can change these fields
        if 'first_name' in input:
            account.first_name = input['first_name']
        if 'last_name' in input:
            account.last_name = input['last_name']
        if 'email' in input:
            account.email = input['email']
            account.username = input['email']

        # Only update these fields if input has been passed
        # if 'password' in input:
        #     account.set_password(input['password'])
        if 'address' in input:
            account.address = input['address']
        if 'postcode' in input:
            account.postcode = input['postcode']
        if 'city' in input:
            account.city = input['city']
        if 'country' in input:
            account.country = input['country']
        if 'phone' in input:
            account.phone = input['phone']
        if 'mobile' in input:
            account.mobile = input['mobile']
        if 'emergency' in input:
            account.emergency = input['emergency']
        if 'gender' in input:
            account.gender = input['gender']
        if 'date_of_birth' in input:
            account.date_of_birth = input['date_of_birth']

        account.save()

        # Update allauth email address
        email_address = EmailAddress.objects.filter(user=account).first()
        email_address.email = account.email
        email_address.save()

        return UpdateAccount(account=account)


class UpdateAccountPassword(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=False)
        password_current = graphene.String(required=False)
        password_new = graphene.String(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user

        print(user)
        print(input)

        ok = False
        if input.get('id', False):
            # Change password for another use
            require_login_and_permission(user, 'costasiella.change_account')

            rid = get_rid(input['id'])
            account = get_user_model().objects.get(id=rid.id)
            if not account:
                raise Exception('Invalid Account ID!')

            account.set_password(input['password_new'])
            account.save()
        else:
            # Change password for current user
            require_login(user)

            # Check if current password exists
            if not input['password_current']:
                raise GraphQLError(_("Current password can't be empty"), extensions={'code': 'CURRENT_PASSWORD_EMPTY'})

            # Check current password
            # https://docs.djangoproject.com/en/2.2/topics/auth/customizing/
            if not check_password(input['password_current'], user.password):
                raise GraphQLError(_("Current password is incorrect, please try again"), extensions={'code': 'CURRENT_PASSWORD_INCORRECT'})

            # Check strength of new password
            # https://docs.djangoproject.com/en/2.2/topics/auth/passwords/
            password_validation.validate_password(
                password=input['password_new'], 
                user=user, 
                password_validators=password_validation.get_password_validators(
                    settings.AUTH_PASSWORD_VALIDATORS
                )
            )

            user.set_password(input['password_new'])
            user.save()

        ok = True

        return UpdateAccountPassword(ok=ok)


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

        if account == user:
            raise GraphQLError(
                _("Can't deactivate currently logged in account."),
                extensions={'code': get_error_code('USER_CURRENTLY_LOGGED_IN')}
            )

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

        if account == user:
            raise GraphQLError(
                _("Can't delete currently logged in account."),
                extensions={'code': get_error_code('USER_CURRENTLY_LOGGED_IN')}
            )

        ok = account.delete()

        return DeleteAccount(ok=ok)


class AccountMutation(graphene.ObjectType):
    create_account = CreateAccount.Field()
    update_account = UpdateAccount.Field()
    update_account_active = UpdateAccountActive.Field()
    update_account_password = UpdateAccountPassword.Field()
    delete_account = DeleteAccount.Field()

