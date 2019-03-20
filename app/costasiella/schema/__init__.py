import graphene
import graphql_jwt

from .financeglaccount import FinanceGLAccountQuery, FinanceGLAccountMutation
from .financecostcenter import FinanceCostCenterQuery, FinanceCostCenterMutation

from .schoolclasstype import SchoolClasstypeQuery, SchoolClasstypeMutation
from .schoollocation import SchoolLocationQuery, SchoolLocationMutation
from .user import UserQuery, UserMutation


class Query(FinanceCostCenterQuery,
            FinanceGLAccountQuery,
            SchoolClasstypeQuery,
            SchoolLocationQuery, 
            UserQuery, 
            graphene.ObjectType):
    node = graphene.relay.Node.Field()


class Mutation(FinanceCostCenterMutation,
               FinanceGLAccountMutation,
               SchoolClasstypeMutation,
               SchoolLocationMutation, 
               UserMutation, 
               graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

