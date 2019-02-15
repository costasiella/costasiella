from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import Q

import graphene
from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class GroupType(DjangoObjectType):
    class Meta:
        model = Group


class PermissionType(DjangoObjectType):
    class Meta:
        model = Permission


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        # username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()


class Query(graphene.AbstractType):
    user = graphene.Field(UserType)
    users = graphene.List(UserType)
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

        
