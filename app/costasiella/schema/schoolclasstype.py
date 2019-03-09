from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from ..models import SchoolClasstype
from ..modules.gql_tools import require_login_and_permission
from ..modules.messages import Messages

m = Messages()

class SchoolClasstypeType(DjangoObjectType):
    class Meta:
        model = SchoolClasstype


class SchoolClasstypeQuery(graphene.ObjectType):
    school_classtypes = graphene.List(SchoolClasstypeType, archived=graphene.Boolean(default_value=False))
    school_classtype = graphene.Field(SchoolClasstypeType, id=graphene.ID())

    def resolve_school_classtypess(self, info, archived, **kwargs):
        user = info.context.user
        print('user authenticated:')
        print(user.is_authenticated)
        if user.is_anonymous:
            raise Exception(m.user_not_logged_in)
        # if not info.context.user.is_authenticated:
            # return SchoolLocation.objects.none()
        # else:
            # return SchoolLocation.objects.all()
        ## return everything:
        if user.has_perm('costasiella.view_schoolclasstype'):
            print('user has view permission')
            return SchoolClasstype.objects.filter(archived = archived).order_by('name')

        # Return only public non-archived locations
        return SchoolClasstype.objects.filter(display_public = True, archived = False).order_by('name')


    def resolve_school_classtype(self, info, id):
        user = info.context.user
        print('user authenticated:')
        print(user.is_authenticated)
        print(user)
        print(user.is_anonymous)
        require_login_and_permission(user, 'costasiella.view_schoolclasstype')

        # Return only public non-archived locations
        return SchoolClasstype.objects.get(id=id)


# class CreateSchoolLocation(graphene.Mutation):
#     school_location = graphene.Field(SchoolLocationType)

#     class Arguments:
#         name = graphene.String(required=True)
#         display_public = graphene.Boolean(required=True)

#     # Output = CreateSchoolLocationPayload

#     def mutate(self, info, name, display_public):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.add_schoollocation')

#         errors = []
#         if not len(name):
#             print('validation error found')
#             raise GraphQLError(_('Name is required'))
#             # errors.append(
#             #     ValidationErrorMessage(
#             #         field="name",
#             #         message=_("Name is required")
#             #     )
#             # )

#             # return ValidationErrors(
#             #     validation_errors = errors
#             # )

#         school_location = SchoolLocation(name=name, display_public=display_public)
#         school_location.save()

#         # return CreateSchoolLocationSuccess(school_location=school_location)
#         return CreateSchoolLocation(school_location=school_location)


# ''' Query like this when enabling error output using union:
# mutation {
#   createSchoolLocation(name:"", displayPublic:true) {
#     __typename
#     ... on CreateSchoolLocationSuccess {
#       schoolLocation {
#         id
#         name
#       }
#     }
#     ... on ValidationErrors {
#       validationErrors {
#         field
#         message
#       }
#     }
#   }
# }

# '''


# class UpdateSchoolLocation(graphene.Mutation):
#     school_location = graphene.Field(SchoolLocationType)

#     class Arguments:
#         id = graphene.ID()
#         name = graphene.String()
#         display_public = graphene.Boolean()


#     def mutate(self, info, id, name, display_public):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.change_schoollocation')

#         school_location = SchoolLocation.objects.filter(id=id).first()
#         if not school_location:
#             raise Exception('Invalid School Location ID!')

#         school_location.name = name
#         school_location.display_public = display_public
#         school_location.save(force_update=True)

#         return UpdateSchoolLocation(school_location=school_location)


# class ArchiveSchoolLocation(graphene.Mutation):
#     school_location = graphene.Field(SchoolLocationType)

#     class Arguments:
#         id = graphene.ID()
#         archived = graphene.Boolean()


#     def mutate(self, info, id, archived):
#         user = info.context.user
#         require_login_and_permission(user, 'costasiella.delete_schoollocation')

#         school_location = SchoolLocation.objects.filter(id=id).first()
#         if not school_location:
#             raise Exception('Invalid School Location ID!')

#         school_location.archived = archived
#         school_location.save(force_update=True)

#         return ArchiveSchoolLocation(school_location=school_location)


# class SchoolLocationMutation(graphene.ObjectType):
#     archive_school_location = ArchiveSchoolLocation.Field()
#     create_school_location = CreateSchoolLocation.Field()
#     update_school_location = UpdateSchoolLocation.Field()