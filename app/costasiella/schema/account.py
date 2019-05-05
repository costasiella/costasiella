from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

import graphene
from graphene_django import DjangoObjectType


class AccountType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class GroupType(DjangoObjectType):
    class Meta:
        model = Group


class PermissionType(DjangoObjectType):
    class Meta:
        model = Permission


class CreateAccount(graphene.Mutation):
    user = graphene.Field(AccountType)

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    # def mutate(self, info, username, password, email):
    def mutate(self, info, password, email):
        user = get_user_model()(
            email=email,
        )
        user.set_password(password)
        user.save()

        return CreateAccount(user=user)


class AccountMutation(graphene.ObjectType):
    create_user = CreateAccount.Field()


class AccountQuery(graphene.AbstractType):
    user = graphene.Field(AccountType)
    users = graphene.List(AccountType)
    group = graphene.List(GroupType, search=graphene.String())
    permission = graphene.List(PermissionType)

    def resolve_user(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')

        return user

    def resolve_users(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')

        return get_user_model().objects.all()

    def resolve_group(self, info, search=None):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        if search:
            filter = (
                Q(name__icontains=search)
            )
            return Groups.objects.filter(filter)

        return Group.objects.all()


    def resolve_permission(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')
        return Permission.objects.all()
        # user = info.context.user
        # if user.is_anonymous:
        #     raise Exception('Not logged in!')
        # if user:
        #     return Permission.objects.filter(user=user)

        
