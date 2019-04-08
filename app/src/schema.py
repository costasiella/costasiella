import graphene
import graphql_jwt

import costasiella.schema as cs_schema

class Query(cs_schema.Query, graphene.ObjectType):
    pass


class Mutations(cs_schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(
    query=Query,
    mutation=Mutations
)

