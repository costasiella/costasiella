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
        return SchoolLocation.objects.all()
