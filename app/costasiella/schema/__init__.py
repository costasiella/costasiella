import graphene
import graphql_jwt

from .schoolclasstype import SchoolClasstypeQuery, SchoolClasstypeMutation
from .schoollocation import SchoolLocationQuery, SchoolLocationMutation
from .user import UserQuery, UserMutation


class Query(SchoolClasstypeQuery,
            SchoolLocationQuery, 
            UserQuery, 
            graphene.ObjectType):
    node = graphene.relay.Node.Field()


class Mutation(SchoolClasstypeMutation,
               SchoolLocationMutation, 
               UserMutation, 
               graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

