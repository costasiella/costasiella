from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from .gql_tools import get_rid

from ..models import SchoolLocation
from ..modules.gql_tools import require_login_and_permission
from ..modules.messages import Messages

m = Messages()

class SchoolLocationNode(DjangoObjectType):
    class Meta:
        model = SchoolLocation
        filter_fields = ['archived']
        interfaces = (graphene.relay.Node, )

    @classmethod
    def get_node(self, info, id):
        print("info:")
        print(info)
        user = info.context.user
        print('user authenticated:')
        print(user.is_authenticated)
        print(user)
        print(user.is_anonymous)
        require_login_and_permission(user, 'costasiella.view_schoollocation')

        # Return only public non-archived locations
        return self._meta.model.objects.get(id=id)


# class ValidationErrorMessage(graphene.ObjectType):
#     field = graphene.String(required=True)
#     message = graphene.String(required=True)


# class ValidationErrors(graphene.ObjectType):
# 	validation_errors = graphene.List(ValidationErrorMessage)
#     # error_message = graphene.String(required=True)


class SchoolLocationQuery(graphene.ObjectType):
    school_locations = DjangoFilterConnectionField(SchoolLocationNode)
    school_location = graphene.relay.Node.Field(SchoolLocationNode)

    def resolve_school_locations(self, info, archived=False, **kwargs):
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
        if user.has_perm('costasiella.view_schoollocation'):
            print('user has view permission')
            return SchoolLocation.objects.filter(archived = archived).order_by('name')

        # Return only public non-archived locations
        return SchoolLocation.objects.filter(display_public = True, archived = False).order_by('name')


    # def resolve_school_location(self, info, id):
    #     user = info.context.user
    #     print('user authenticated:')
    #     print(user.is_authenticated)
    #     print(user)
    #     print(user.is_anonymous)
    #     require_login_and_permission(user, 'costasiella.view_schoollocation')

    #     # Return only public non-archived locations
    #     return SchoolLocation.objects.get(id=id)


# # class CreateSchoolLocationSuccess(graphene.ObjectType):
# # 	school_location = graphene.Field(SchoolLocationType, required=True)


# # class CreateSchoolLocationPayload(graphene.Union):
# #     class Meta:
# #         types = (ValidationErrors, CreateSchoolLocationSuccess)


class CreateSchoolLocation(graphene.relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)

    school_location = graphene.Field(SchoolLocationNode)

    # Output = CreateSchoolLocationPayload

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_schoollocation')

        errors = []
        if not len(input['name']):
            print('validation error found')
            raise GraphQLError(_('Name is required'))
            # errors.append(
            #     ValidationErrorMessage(
            #         field="name",
            #         message=_("Name is required")
            #     )
            # )

            # return ValidationErrors(
            #     validation_errors = errors
            # )

        school_location = SchoolLocation(
            name=input['name'], 
            display_public=input['display_public']
        )
        school_location.save()

        # return CreateSchoolLocationSuccess(school_location=school_location)
        return CreateSchoolLocation(school_location=school_location)


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

class UpdateSchoolLocation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        display_public = graphene.Boolean(required=True)
        
    school_location = graphene.Field(SchoolLocationNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_schoollocation')

        rid = get_rid(input['id'])

        school_location = SchoolLocation.objects.filter(id=rid.id).first()
        if not school_location:
            raise Exception('Invalid School Location ID!')

        school_location.name = input['name']
        school_location.display_public = input['display_public']
        school_location.save(force_update=True)

        return UpdateSchoolLocation(school_location=school_location)


class ArchiveSchoolLocation(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        archived = graphene.Boolean(required=True)

    school_location = graphene.Field(SchoolLocationNode)

    @classmethod
    def mutate_and_get_payload(self, root, info, **input):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.delete_schoollocation')

        rid = get_rid(input['id'])

        school_location = SchoolLocation.objects.filter(id=rid.id).first()
        if not school_location:
            raise Exception('Invalid School Location ID!')

        school_location.archived = input['archived']
        school_location.save(force_update=True)

        return ArchiveSchoolLocation(school_location=school_location)


class SchoolLocationMutation(graphene.ObjectType):
    archive_school_location = ArchiveSchoolLocation.Field()
    create_school_location = CreateSchoolLocation.Field()
    update_school_location = UpdateSchoolLocation.Field()