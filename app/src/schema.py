import graphene
import graphql_jwt

import costasiella.schema


class Mutations(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


class Query(costasiella.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(
    query=Query,
    mutation=Mutations
)
