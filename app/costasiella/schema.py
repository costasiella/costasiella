import graphene
from graphene_django import DjangoObjectType

from .models import SchoolLocation
from .modules.gql_tools import require_login_and_permission


class SchoolLocationType(DjangoObjectType):
    class Meta:
        model = SchoolLocation


class Query(graphene.ObjectType):
    school_locations = graphene.List(SchoolLocationType)

    def resolve_school_locations(self, info, **kwargs):
        user = info.context.user
        print('user authenticated:')
        print(user.is_authenticated)
        if user.is_anonymous:
            raise Exception('Not logged in!')
        # if not info.context.user.is_authenticated:
            # return SchoolLocation.objects.none()
        # else:
            # return SchoolLocation.objects.all()
        ## return everything:
        if user.has_perm('costasiella.view_schoollocation'):
            return SchoolLocation.objects.all().order_by('name')

        # Return only public non-archived locations
        return SchoolLocation.objects.filter(public = True, archived = False).order_by('name')


class CreateSchoolLocation(graphene.Mutation):
    id = graphene.Int()
    name = graphene.String()
    public = graphene.Boolean()

    class Arguments:
        name = graphene.String()
        public = graphene.Boolean()


    def mutate(self, info, name, public):
        user = info.context.user
        require_login_and_permission(user, 'costasiella.add_schoollocation')

        school_location = SchoolLocation(name=name, public=public)
        school_location.save()

        return CreateSchoolLocation(
            id=school_location.id,
            # archived=school_location.archived,
            name=school_location.name,
            public=school_location.public
        )


class UpdateSchoolLocation(graphene.Mutation):
    id = graphene.Int()
    archived = graphene.Boolean()
    name = graphene.String()
    public = graphene.Boolean()

    class Arguments:
        id = graphene.Int()
        archived = graphene.Boolean()
        name = graphene.String()
        public = graphene.Boolean()

    def mutate(self, info, id, archived, name, public):
        user = info.context.user
        if not user.has_perm('costasiella.change_schoollocation'):
            raise Exception('Permission denied!')

        school_location = SchoolLocation.objects.filter(id=id).first()
        if not school_location:
            raise Exception('Invalid School Location ID!')

        school_location.archived = archived
        school_location.name = name
        school_location.public = public
        school_location.save(force_update=True)

        return UpdateSchoolLocation(
            id=school_location.id,
            archived=school_location.archived,
            name=school_location.name,
            public=school_location.public
        )


class DeleteSchoolLocation(graphene.Mutation):
    id = graphene.Int()

    class Arguments:
        id = graphene.Int()

    def mutate(self, info, id):
        user = info.context.user
        if not user.has_perm('costasiella.delete_schoollocation'):
            raise Exception('Permission denied!')

        school_location = SchoolLocation.objects.filter(id=id).first()
        if not school_location:
            raise Exception('Invalid School Location ID!')

        school_location.delete()

        return DeleteSchoolLocation(
            # This returns None for the id if successful
            id=school_location.id
        )


class Mutation(graphene.ObjectType):
    create_school_location = CreateSchoolLocation.Field()
    update_school_location = UpdateSchoolLocation.Field()
    delete_school_location = DeleteSchoolLocation.Field()