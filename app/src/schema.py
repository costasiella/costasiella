import graphene
import graphql_jwt

import costasiella.schema
import users.schema


class Query(costasiella.schema.Query, users.schema.Query, graphene.ObjectType):
    pass


class Mutations(users.schema.Mutation, costasiella.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(
    query=Query,
    mutation=Mutations
)

