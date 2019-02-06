import graphene

import costasiella.schema


class Query(costasiella.schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
