from django.utils.translation import gettext as _

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

import django_filters
from django.db import models

from ..modules.encrypted_fields import EncryptedTextField

import graphene
from graphql import GraphQLError
from graphql_relay import to_global_id
from graphql import GraphQLError
from django.contrib.auth import password_validation
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from graphene_django.converter import convert_django_field
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django_filters import FilterSet, OrderingFilter, CharFilter

from sorl.thumbnail import get_thumbnail

from allauth.account.models import EmailAddress
from ..models import AccountClasspass, AccountSubscription, Business, OrganizationDiscovery, OrganizationLanguage

from ..modules.gql_tools import \
    check_node_item_resolve_permission, \
    require_login, \
    require_permission, \
    require_login_and_permission, \
    require_login_and_one_of_permissions, \
    require_login_and_one_of_permission_or_own_account, \
    get_rid, \
    get_error_code, \
    get_content_file_from_base64_str

from ..modules.encrypted_fields import EncryptedTextField
from .account_classpass import AccountClasspassNode
from .account_subscription import AccountSubscriptionNode


@convert_django_field.register(EncryptedTextField)
def convert_json_field_to_string(field, registry=None):
    return graphene.String()


class UserType(DjangoObjectType):
    account_id = graphene.ID()
    profile_policy = graphene.String()
    has_complete_enough_profile = graphene.Boolean()
    has_bank_account_info = graphene.Boolean()
    has_reached_trial_limit = graphene.Boolean()
    url_image_thumbnail_small = graphene.String()

    class Meta:
        model = get_user_model()

    def resolve_has_bank_account_info(self, info):
        return self.has_bank_account_info()

    def resolve_profile_policy(self, info):
        return self.get_profile_policy()

    def resolve_has_complete_enough_profile(self, info):
        return self.has_complete_enough_profile()

    def resolve_account_id(self, info):
        return to_global_id("AccountNode", info.context.user.id)

    def resolve_has_reached_trial_limit(self, info):
        return self.has_reached_trial_limit()

    def resolve_url_image_thumbnail_small(self, info):
        if self.image:
            return get_thumbnail(self.image, '50x50', crop='center', quality=99).url
        else:
            return ''


class AccountFilter(FilterSet):
    class Meta:
        model = get_user_model()
        fields = {
            'full_name': ['icontains', 'exact'],
            'is_active': ['exact'],
            'customer': ['exact'],
            'instructor': ['exact'],
            'employee': ['exact'],
            'invoice_to_business': ['exact'],
            'key_number': ['exact', 'icontains', 'isnull'],
        }
        filter_overrides = {
            EncryptedTextField: {
                'filter_class': CharFilter,
            },
        }

    order_by = OrderingFilter(
        fields=(
            'created_at',
            'full_name'
        )
    )


class AccountNodeInterface(graphene.Interface):
    id = graphene.GlobalID()
    profile_policy = graphene.String()
    has_complete_enough_profile = graphene.Boolean()
    has_reached_trial_limit = graphene.Boolean()
    # url_image = graphene.String()
    url_image_thumbnail_small = graphene.String()
    classpasses_latest = graphene.List(AccountClasspassNode)
    subscriptions_latest = graphene.List(AccountSubscriptionNode)


class AccountNode(DjangoObjectType):
    class Meta:
        model = get_user_model()
        filterset_class = AccountFilter
        # Fields to include
        fields = (
            'is_active',
            'last_login',
            'customer',
            'instructor',
            'employee',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'gender',
            'date_of_birth',
            'address',
            'postcode',
            'city',
            'country',
            'phone',
            'mobile',
            'emergency',
            'key_number',
            'image',
            'organization_discovery',
            'organization_language',
            'invoice_to_business',
            'mollie_customer_id',
            'created_at',
            # Reverse relations
            'classpasses',
            'subscriptions',
            'accountinstructorprofile',
        )
        interfaces = (graphene.relay.Node, AccountNodeInterface,)

    def resolve_has_reached_trial_limit(self, info):
        user = info.context.user

        # Accounts can view their own status
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.has_reached_trial_limit()

    def resolve_profile_policy(self, info):
        user = info.context.user

        # Accounts can view their own status
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.get_profile_policy()

    def resolve_has_complete_enough_profile(self, info):
        user = info.context.user

        # Accounts can view their own status
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.has_complete_enough_profile()

    #TODO: Replace by protected url like account document, in case there's a use for the full res image.
    # def resolve_url_image(self, info):
    #     if self.image:
    #         return self.image.url
    #     else:
    #         return ''

    def resolve_url_image_thumbnail_small(self, info):
        user = info.context.user
        require_login_and_one_of_permissions(user, [
            'costasiella.view_account',
        ])

        if self.image:
            return get_thumbnail(self.image, '50x50', crop='center', quality=99).url
        else:
            return ''

    @classmethod
    def get_node(cls, info, id):
        user = info.context.user

        account = cls._meta.model.objects.get(id=id)
        if info.path.typename == "ScheduleEventNode":
            return account

        require_login(user)
        if not account == user:
            # Allow a user to get their own account. In all other cases, check permissions.
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
                'costasiella.view_selfcheckin'
            ])

        return account

    def resolve_address(self, info, **kwargs):
        user = info.context.user

        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.address

    def resolve_city(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.city

    def resolve_country(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.country

    def resolve_customer(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.customer

    def resolve_date_of_birth(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.date_of_birth

    def resolve_emergency(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.emergency

    def resolve_email(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.email

    def resolve_employee(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.employee

    def resolve_gender(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.gender

    def resolve_image(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.image

    def resolve_instructor(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.instructor

    def resolve_is_active(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.is_active

    def resolve_key_number(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.key_number

    def resolve_mobile(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.mobile

    def resolve_phone(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.phone

    def resolve_postcode(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.postcode

    def resolve_key_number(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.key_number

    def resolve_mollie_customer_id(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_one_of_permissions(user, [
                'costasiella.view_account',
            ])

        return self.mollie_customer_id

    def resolve_classpasses(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_permission(user, 'costasiella.view_accountclasspass')

        return self.classpasses

    def resolve_classpasses_latest(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_permission(user, 'costasiella.view_accountclasspass')

        return AccountClasspass.objects.filter(account=self.id).order_by('-date_start')[:2]

    def resolve_subscriptions(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_permission(user, 'costasiella.view_accountsubscription')

        return self.subscriptions

    def resolve_subscriptions_latest(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_permission(user, 'costasiella.view_accountsubscription')

        return AccountSubscription.objects.filter(account=self.id).order_by('-date_start')[:2]

    def resolve_accountinstructorprofile_latest(self, info, **kwargs):
        user = info.context.user
        if not user.id == self.id:
            require_login_and_permission(user, 'costasiella.view_accountinstructorprofile')

        return self.accountinstructorprofile


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


class AccountQuery(graphene.ObjectType):
    user = graphene.Field(UserType)
    account = graphene.relay.Node.Field(AccountNode)
    accounts = DjangoFilterConnectionField(AccountNode)
    instructors = DjangoFilterConnectionField(AccountNode)
    group = graphene.relay.Node.Field(GroupNode)
    groups = DjangoFilterConnectionField(GroupNode)
    permission = graphene.relay.Node.Field(PermissionNode)
    permissions = DjangoFilterConnectionField(PermissionNode)

    def resolve_user(self, info):
        user = info.context.user
        require_login(user)

        return user

    def resolve_accounts(self, info, is_active=True, **kwargs):
        user = info.context.user
        require_login_and_one_of_permissions(user, [
            'costasiella.view_account',
            'costasiella.view_selfcheckin'
        ])

        qs = get_user_model().objects.filter(
            is_active=is_active, 
            is_superuser=False
        )

        return qs.order_by('first_name')

    def resolve_instructors(self, info, **kwargs):
        # This endpoint allows instructors' names to be public, so they can be queried for the shop
        qs = get_user_model().objects.filter(
            is_active=True,
            is_superuser=False,
            instructor=True
        )

        return qs.order_by('first_name')

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

        # Setup new account
        account.new_account_setup()

        return CreateAccount(account=account)
#         return CreateAccount(user=user)


def validate_create_update_input(account, input, update=False):
    """
    Validate input
    """ 
    result = {}

    if update:
        # Check that image and image_file_name are both present in case one is set
        if 'image' in input or 'image_file_name' in input:
            if not (input.get('image', None) and input.get('image_file_name', None)):
                raise Exception(_('When setting "image" or "imageFileName", both fields need to be present and set'))

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

    # Fetch & check organization discovery
    if 'organization_discovery' in input:
        rid = get_rid(input['organization_discovery'])
        organization_discovery = OrganizationDiscovery.objects.get(pk=rid.id)
        result['organization_discovery'] = organization_discovery
        if not organization_discovery:
            raise Exception(_('Invalid Organization Discovery ID!'))

    # Fetch & check organization language
    if 'organization_language' in input:
        rid = get_rid(input['organization_language'])
        organization_language = OrganizationLanguage.objects.get(pk=rid.id)
        result['organization_language'] = organization_language
        if not organization_language:
            raise Exception(_('Invalid Organization Language ID!'))

    # Fetch & check business
    if 'invoice_to_business' in input:
        rid = get_rid(input['invoice_to_business'])
        business = Business.objects.get(pk=rid.id)
        result['invoice_to_business'] = business
        if not business:
            raise Exception(_('Invalid Business ID!'))

    return result


class UpdateAccount(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        # password = graphene.String(required=False)
        customer = graphene.Boolean(required=False)
        instructor = graphene.Boolean(required=False)
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
        key_number = graphene.String(required=False)
        organization_discovery = graphene.ID(required=False)
        organization_language = graphene.ID(required=False)
        invoice_to_business = graphene.ID(required=False)
        mollie_customer_id = graphene.String(required=False)
        image = graphene.String(required=False)
        image_file_name = graphene.String(required=False)

    account = graphene.Field(AccountNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login(user)

        rid = get_rid(input['id'])
        account = get_user_model().objects.filter(id=rid.id).first()
        if not account:
            raise Exception('Invalid Account ID!')

        change_permission = 'costasiella.change_account'

        # Allow users to update their own account without additional permissions
        if not user.id == account.id:
            require_permission(user, change_permission)

        result = validate_create_update_input(account, input, update=True)

        # Only process these fields when a user has the "change_account" permission. Users shouldn't be able to
        # change this for their own account
        if user.has_perm(change_permission):
            if 'customer' in input:
                account.customer = input['customer']
            if 'instructor' in input:
                account.instructor = input['instructor']
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
        if 'key_number' in input:
            account.key_number = input['key_number']
        if 'mollie_customer_id' in input:
            account.mollie_customer_id = input['mollie_customer_id']

        if 'organization_discovery' in result:
            account.organization_discovery = result['organization_discovery']
        if 'organization_language' in result:
            account.organization_language = result['organization_language']
        if 'invoice_to_business' in result:
            account.invoice_to_business = result['invoice_to_business']

        if 'image' in input:
            account.image = get_content_file_from_base64_str(data_str=input['image'],
                                                             file_name=input['image_file_name'])

        account.save()

        # Update allauth email address after saving account, to ensure it's in sync
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

        ok = False
        if input.get('id', False):
            # Change password for another use
            require_login_and_permission(user, 'costasiella.change_account')

            rid = get_rid(input['id'])
            account = get_user_model().objects.get(id=rid.id)
            if not account:
                raise Exception('Invalid Account ID!')

            new_password = input['password_new']
            validate_password(new_password)

            account.set_password(new_password)
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
                raise GraphQLError(_("Current password is incorrect, please try again"),
                                   extensions={'code': 'CURRENT_PASSWORD_INCORRECT'})

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

        ok = bool(account.delete())

        return DeleteAccount(ok=ok)


class AccountMutation(graphene.ObjectType):
    create_account = CreateAccount.Field()
    update_account = UpdateAccount.Field()
    update_account_active = UpdateAccountActive.Field()
    update_account_password = UpdateAccountPassword.Field()
    delete_account = DeleteAccount.Field()

