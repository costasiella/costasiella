import graphene
import costasiella.schema as cs_schema


class Query(cs_schema.Query, graphene.ObjectType):
    pass


class Mutation(cs_schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
