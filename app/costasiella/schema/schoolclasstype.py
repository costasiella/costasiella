from django.utils.translation import gettext as _

import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError

import validators

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

    def resolve_school_classtypes(self, info, archived, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception(m.user_not_logged_in)

        # Has permission: return everything
        if user.has_perm('costasiella.view_schoolclasstype'):
            print('user has view permission')
            return SchoolClasstype.objects.filter(archived = archived).order_by('name')

        # Return only public non-archived locations
        return SchoolClasstype.objects.filter(display_public = True, archived = False).order_by('name')


    def resolve_school_classtype(self, info, id):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.view_schoolclasstype')

        # Return only public non-archived classtypes
        return SchoolClasstype.objects.get(id=id)


class CreateSchoolClasstype(graphene.Mutation):
    school_classtype = graphene.Field(SchoolClasstypeType)

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()
        display_public = graphene.Boolean(required=True)
        url_website = graphene.String()

    # Output = CreateSchoolLocationPayload

    def mutate(self, info, name, description, display_public, url_website):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_schoolclasstype')

        # Validate input
        if not len(name):
            print('validation error found')
            raise GraphQLError(_('Name is required'))

        if url_website:
            if not validators.url(url_website, public=True):
                raise GraphQLError(_('Invalid URL, make sure it starts with "http"'))


        school_classtype = SchoolClasstype(
            name=name, 
            description=description,
            display_public=display_public,
            url_website=url_website
        )
        school_classtype.save()

        # return CreateSchoolLocationSuccess(school_location=school_location)
        return CreateSchoolClasstype(school_classtype = school_classtype)


class UpdateSchoolClasstype(graphene.Mutation):
    school_classtype = graphene.Field(SchoolClasstypeType)

    class Arguments:
        id = graphene.ID()
        name = graphene.String()
        description = graphene.String()
        display_public = graphene.Boolean()
        url_website = graphene.String()

    def mutate(self, info, id, name, description=None, display_public=False, url_website=None):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.change_schoolclasstype')

        school_classtype = SchoolClasstype.objects.filter(id=id).first()
        if not school_classtype:
            raise Exception('Invalid School Classtype ID!')

        school_classtype.name = name
        school_classtype.description = description
        school_classtype.display_public = display_public
        school_classtype.url_website = url_website
        school_classtype.save(force_update=True)

        return UpdateSchoolClasstype(school_classtype=school_classtype)


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


class SchoolClasstypeMutation(graphene.ObjectType):
#     archive_school_location = ArchiveSchoolLocation.Field()
    create_school_classtype = CreateSchoolClasstype.Field()
    update_school_classtype = UpdateSchoolClasstype.Field()