from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import Account, AccountInstructorProfile
from ..modules.gql_tools import require_login_and_permission, get_rid
from ..modules.messages import Messages

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

    # # Fetch & check organization classpass
    # rid = get_rid(input['organization_classpass'])
    # organization_classpass = OrganizationInstructorProfile.objects.get(pk=rid.id)
    # result['organization_classpass'] = organization_classpass
    # if not organization_classpass:
    #     raise Exception(_('Invalid Organization InstructorProfile ID!'))

    return result


class AccountInstructorProfileNode(DjangoObjectType):   
    class Meta:
        model = AccountInstructorProfile
        # Fields to include
        fields = (
            'account',
            'classes',
            'appointments',
            'events',
            'role',
            'education',
            'bio',
            'url_bio',
            'url_website',
            'created_at',
            'updated_at'
        )
        filter_fields = [
            'account', 
            'classes', 
            'appointments', 
            'events', 
            'account__is_active'
        ]
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountinstructorprofile')

        return self._meta.model.objects.get(id=id)


class AccountInstructorProfileQuery(graphene.ObjectType):
    account_instructor_profiles = DjangoFilterConnectionField(AccountInstructorProfileNode)
    ## At some point, figure out which id is required. Node expects "AccountInstructorProfileNode ID", but the id will come
    # From "Account"
    # account_instructor_profile = graphene.relay.Node.Field(AccountInstructorProfileNode)

    def resolve_account_instructor_profiles(self, info, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountinstructorprofile')

        # return everything:
        return AccountInstructorProfile.objects.all().order_by('account__full_name')


# class CreateAccountInstructorProfile(graphene.relay.ClientIDMutation):
#     class Input:
#         account = graphene.ID(required=True)
#         classes = graphene.Boolean(required=False, default_value=True)
#         appointments = graphene.Boolean(required=False, default_value=False)
#         events = graphene.Boolean(required=False, default_value=False)
#         role = graphene.String(required=False, default_value="")
#         education = graphene.String(required=False, default_value="")
#         bio = graphene.String(required=False, default_value="")
#         url_bio = graphene.String(required=False, default_value="")
#         url_website = graphene.String(required=False, default_value="")        

#     account_instructor_profile = graphene.Field(AccountInstructorProfileNode)

#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.add_accountinstructorprofile')

#         # Validate input
#         result = validate_create_update_input(input, update=False)

#         account_instructor_profile = AccountInstructorProfile(
#             account=result['account'],
#         )

#         if 'classes' in input:
#             account_instructor_profile.classes = input['classes']

#         if 'appointments' in input:
#             account_instructor_profile.appointments = input['appointments']

#         if 'events' in input:
#             account_instructor_profile.events = input['events']

#         if 'role' in input:
#             account_instructor_profile.role = input['role']

#         if 'education' in input:
#             account_instructor_profile.education = input['education']

#         if 'bio' in input:
#             account_instructor_profile.bio = input['bio']

#         if 'url_bio' in input:
#             account_instructor_profile.url_bio = input['url_bio']

#         if 'url_website' in input:
#             account_instructor_profile.url_website = input['url_website']

#         account_instructor_profile.save()

#         return CreateAccountInstructorProfile(account_instructor_profile=account_instructor_profile)


class UpdateAccountInstructorProfile(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        classes = graphene.Boolean(required=False)
        appointments = graphene.Boolean(required=False)
        events = graphene.Boolean(required=False)
        role = graphene.String(required=False)
        education = graphene.String(required=False)
        bio = graphene.String(required=False)
        url_bio = graphene.String(required=False)
        url_website = graphene.String(required=False)    
        
    account_instructor_profile = graphene.Field(AccountInstructorProfileNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountinstructorprofile')

        rid = get_rid(input['account'])
        account_instructor_profile = AccountInstructorProfile.objects.filter(account=rid.id).first()
        if not account_instructor_profile:
            raise Exception('Invalid Account Instructor Profile ID!')

        if 'classes' in input:
            account_instructor_profile.classes = input['classes']

        if 'appointments' in input:
            account_instructor_profile.appointments = input['appointments']

        if 'events' in input:
            account_instructor_profile.events = input['events']

        if 'role' in input:
            account_instructor_profile.role = input['role']

        if 'education' in input:
            account_instructor_profile.education = input['education']

        if 'bio' in input:
            account_instructor_profile.bio = input['bio']

        if 'url_bio' in input:
            account_instructor_profile.url_bio = input['url_bio']

        if 'url_website' in input:
            account_instructor_profile.url_website = input['url_website']
        
        account_instructor_profile.save()

        return UpdateAccountInstructorProfile(account_instructor_profile=account_instructor_profile)


# class DeleteAccountInstructorProfile(graphene.relay.ClientIDMutation):
#     class Input:
#         id = graphene.ID(required=True)

#     ok = graphene.Boolean()

#     @classmethod
#     def mutate_and_get_payload(self, root, info, **input):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.delete_accountinstructorprofile')

#         rid = get_rid(input['id'])
#         account_instructor_profile = AccountInstructorProfile.objects.filter(id=rid.id).first()
#         if not account_instructor_profile:
#             raise Exception('Invalid Account InstructorProfile ID!')

#         ok = account_instructor_profile.delete()

#         return DeleteAccountInstructorProfile(ok=ok)


class AccountInstructorProfileMutation(graphene.ObjectType):
    # create_account_instructor_profile = CreateAccountInstructorProfile.Field()
    update_account_instructor_profile = UpdateAccountInstructorProfile.Field()
    # delete_account_instructor_profile = DeleteAccountInstructorProfile.Field()
    