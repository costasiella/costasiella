from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from .models import SchoolLocation
from .modules.gql_tools import require_login_and_permission


class SchoolLocationType(DjangoObjectType):
    class Meta:
        model = SchoolLocation


# class ValidationErrorMessage(graphene.ObjectType):
#     field = graphene.String(required=True)
#     message = graphene.String(required=True)


# class ValidationErrors(graphene.ObjectType):
# 	validation_errors = graphene.List(ValidationErrorMessage)
#     # error_message = graphene.String(required=True)


class Query(graphene.ObjectType):
    school_locations = graphene.List(SchoolLocationType, archived=graphene.Boolean(default_value=False))
    school_location = graphene.Field(SchoolLocationType, id=graphene.ID())

    def resolve_school_locations(self, info, archived, **kwargs):
        user = info.context.user
        print('user authenticated:')
        print(user.is_authenticated)
        if user.is_anonymous:
            raise Exception(_('Not logged in!'))
        # if not info.context.user.is_authenticated:
            # return SchoolLocation.objects.none()
        # else:
            # return SchoolLocation.objects.all()
        ## return everything:
        if user.has_perm('costasiella.view_schoollocation'):
            print('user has view permission')
            return SchoolLocation.objects.filter(archived = archived).order_by('name')

        # Return only public non-archived locations
        return SchoolLocation.objects.filter(display_public = True, archived = False).order_by('name')


    def resolve_school_location(self, info, id):
        user = info.context.user
        print('user authenticated:')
        print(user.is_authenticated)
        if user.is_anonymous:
            raise Exception(_('Not logged in!'))

        if not user.has_perm('costasiella.view_schoollocation'):
            raise Exception(_('Permission denied!'))

        # Return only public non-archived locations
        return SchoolLocation.objects.get(id=id)


# class CreateSchoolLocationSuccess(graphene.ObjectType):
# 	school_location = graphene.Field(SchoolLocationType, required=True)


# class CreateSchoolLocationPayload(graphene.Union):
#     class Meta:
#         types = (ValidationErrors, CreateSchoolLocationSuccess)


class CreateSchoolLocation(graphene.Mutation):
    id = graphene.Int()
    name = graphene.String()
    display_public = graphene.Boolean()

    class Arguments:
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)

    # Output = CreateSchoolLocationPayload

    def mutate(self, info, name, display_public):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_schoollocation')

        errors = []
        if not len(name):
            print('validation error found')
            raise GraphQLError(_('Name is requires'))
            # errors.append(
            #     ValidationErrorMessage(
            #         field="name",
            #         message=_("Name is required")
            #     )
            # )

            # return ValidationErrors(
            #     validation_errors = errors
            # )

        school_location = SchoolLocation(name=name, display_public=display_public)
        school_location.save()

        # return CreateSchoolLocationSuccess(school_location=school_location)
        return CreateSchoolLocation(
            id=school_location.id,
            name=school_location.name,
            display_public=school_location.display_public
        )

''' Query like this when enabling error output using union:
mutation {
  createSchoolLocation(name:"", displayPublic:true) {
    __typename
    ... on CreateSchoolLocationSuccess {
      schoolLocation {
        id
        name
      }
    }
    ... on ValidationErrors {
      validationErrors {
        field
        message
      }
    }
  }
}

'''


class UpdateSchoolLocation(graphene.Mutation):
    id = graphene.ID()
    name = graphene.String()
    display_public = graphene.Boolean()

    class Arguments:
        id = graphene.ID()
        name = graphene.String()
        display_public = graphene.Boolean()


    def mutate(self, info, id, name, display_public):
        user = info.context.user
        if not user.has_perm('costasiella.change_schoollocation'):
            raise Exception('Permission denied!')

        school_location = SchoolLocation.objects.filter(id=id).first()
        if not school_location:
            raise Exception('Invalid School Location ID!')

        print('mutate vars')
        print(id)
        print(name)
        print(display_public)

        school_location.name = name
        school_location.display_public = display_public
        school_location.save(force_update=True)

        return UpdateSchoolLocation(
            id=school_location.id,
            name=school_location.name,
            display_public=school_location.display_public
        )


# class ArchiveSchoolLocation(graphene.Mutation):
#     id = graphene.Int()
#     archived = graphene.Boolean()

#     class Arguments:
#         id = graphene.Int()
#         archived = graphene.Boolean()

#     def mutate(self, info, id):
#         user = info.context.user
#         if not user.has_perm('costasiella.delete_schoollocation'):
#             raise Exception('Permission denied!')

#         school_location = SchoolLocation.objects.filter(id=id).first()
#         if not school_location:
#             raise Exception('Invalid School Location ID!')

#         school_location.archived = archvied

#         return ArchiveSchoolLocation(
#             # This returns None for the id if successful
#             id=school_location.id
#         )


class Mutation(graphene.ObjectType):
    create_school_location = CreateSchoolLocation.Field()
    update_school_location = UpdateSchoolLocation.Field()