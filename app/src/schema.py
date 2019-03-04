import graphene
import graphql_jwt

import costasiella.schema as cs_schema


class Query(cs_schema.Query, graphene.ObjectType):
    pass


class Mutations(cs_schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(
    query=Query,
    mutation=Mutations
)

