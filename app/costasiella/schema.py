import graphene
from graphene_django import DjangoObjectType

from .models import SchoolLocation


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
        if user.has_perm('view_schoollocation'):
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
        school_location = SchoolLocation(id=id, archived=archived, name=name, public=public)
        school_location.save(force_update=True)

        return UpdateSchoolLocation(
            id=school_location.id,
            archived=school_location.archived,
            name=school_location.name,
            public=school_location.public
        )


class Mutation(graphene.ObjectType):
    create_school_location = CreateSchoolLocation.Field()
    update_school_location = UpdateSchoolLocation.Field()