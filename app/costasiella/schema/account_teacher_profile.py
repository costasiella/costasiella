from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

import validators

from ..models import Account, AccountTeacherProfile
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
    # organization_classpass = OrganizationTeacherProfile.objects.get(pk=rid.id)
    # result['organization_classpass'] = organization_classpass
    # if not organization_classpass:
    #     raise Exception(_('Invalid Organization TeacherProfile ID!'))



    return result


class AccountTeacherProfileNode(DjangoObjectType):   
    class Meta:
        model = AccountTeacherProfile
        filter_fields = ['account', ]
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountteacherprofile')

        return self._meta.model.objects.get(id=id)


class AccountTeacherProfileQuery(graphene.ObjectType):
    account_teacher_profiles = DjangoFilterConnectionField(AccountTeacherProfileNode)
    account_teacher_profile = graphene.relay.Node.Field(AccountTeacherProfileNode)


    def resolve_account_teacher_profiles(self, info, account, **kwargs):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_accountteacherprofile')

        rid = get_rid(account)

        ## return everything:
        return AccountTeacherProfile.objects.filter(account=rid.id).order_by('date_start')


class CreateAccountTeacherProfile(graphene.relay.ClientIDMutation):
    class Input:
        account = graphene.ID(required=True)
        classes = graphene.Boolean(required=False, default_value=True)
        appointments = graphene.Boolean(required=False, default_value=False)
        events = graphene.Boolean(required=False, default_value=False)
        role = graphene.String(required=False, default_value="")
        education = graphene.String(required=False, default_value="")
        bio = graphene.String(required=False, default_value="")
        url_bio = graphene.String(required=False, default_value="")
        url_website = graphene.String(required=False, default_value="")        

    account_teacher_profile = graphene.Field(AccountTeacherProfileNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_accountteacherprofile')

        # Validate input
        result = validate_create_update_input(input, update=False)

        account_teacher_profile = AccountTeacherProfile(
            account=result['account'],
        )

        if 'classes' in input:
            account_teacher_profile.classes = input['classes']

        if 'appointments' in input:
            account_teacher_profile.appointments = input['appointments']

        if 'events' in input:
            account_teacher_profile.events = input['events']

        if 'role' in input:
            account_teacher_profile.role = input['role']

        if 'education' in input:
            account_teacher_profile.education = input['education']

        if 'bio' in input:
            account_teacher_profile.bio = input['bio']

        if 'url_bio' in input:
            account_teacher_profile.url_bio = input['url_bio']

        if 'url_website' in input:
            account_teacher_profile.url_website = input['url_website']

        account_teacher_profile.save()

        return CreateAccountTeacherProfile(account_teacher_profile=account_teacher_profile)


class UpdateAccountTeacherProfile(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        classes = graphene.Boolean(required=False)
        appointments = graphene.Boolean(required=False)
        events = graphene.Boolean(required=False)
        role = graphene.String(required=False)
        education = graphene.String(required=False)
        bio = graphene.String(required=False)
        url_bio = graphene.String(required=False)
        url_website = graphene.String(required=False)    
        
    account_teacher_profile = graphene.Field(AccountTeacherProfileNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_accountteacherprofile')

        rid = get_rid(input['id'])
        account_teacher_profile = AccountTeacherProfile.objects.filter(id=rid.id).first()
        if not account_teacher_profile:
            raise Exception('Invalid Account TeacherProfile ID!')

        if 'classes' in input:
            account_teacher_profile.classes = input['classes']

        if 'appointments' in input:
            account_teacher_profile.appointments = input['appointments']

        if 'events' in input:
            account_teacher_profile.events = input['events']

        if 'role' in input:
            account_teacher_profile.role = input['role']

        if 'education' in input:
            account_teacher_profile.education = input['education']

        if 'bio' in input:
            account_teacher_profile.bio = input['bio']

        if 'url_bio' in input:
            account_teacher_profile.url_bio = input['url_bio']

        if 'url_website' in input:
            account_teacher_profile.url_website = input['url_website']
        
        account_teacher_profile.save()

        return UpdateAccountTeacherProfile(account_teacher_profile=account_teacher_profile)


class DeleteAccountTeacherProfile(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_accountteacherprofile')

        rid = get_rid(input['id'])
        account_teacher_profile = AccountTeacherProfile.objects.filter(id=rid.id).first()
        if not account_teacher_profile:
            raise Exception('Invalid Account TeacherProfile ID!')

        ok = account_teacher_profile.delete()

        return DeleteAccountTeacherProfile(ok=ok)


class AccountTeacherProfileMutation(graphene.ObjectType):
    create_account_teacher_profile = CreateAccountTeacherProfile.Field()
    update_account_teacher_profile = UpdateAccountTeacherProfile.Field()
    delete_account_teacher_profile = DeleteAccountTeacherProfile.Field()
    