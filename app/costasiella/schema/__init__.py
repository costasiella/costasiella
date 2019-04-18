import graphene
import graphql_jwt

from .finance_costcenter import FinanceCostCenterQuery, FinanceCostCenterMutation
from .finance_glaccount import FinanceGLAccountQuery, FinanceGLAccountMutation
from .finance_taxrate import FinanceTaxRateQuery, FinanceTaxRateMutation

from .organization_classpass import OrganizationClasspassQuery, OrganizationClasspassMutation
from .organization_classpass_group import OrganizationClasspassGroupQuery, OrganizationClasspassGroupMutation
from .organization_classpass_group_classpass import OrganizationClasspassGroupClasspassMutation
from .organization_classtype import OrganizationClasstypeQuery, OrganizationClasstypeMutation
from .organization_discovery import OrganizationDiscoveryQuery, OrganizationDiscoveryMutation
from .organization_location import OrganizationLocationQuery, OrganizationLocationMutation
from .organization_level import OrganizationLevelQuery, OrganizationLevelMutation
from .organization_membership import OrganizationMembershipQuery, OrganizationMembershipMutation
from .user import UserQuery, UserMutation


class Query(FinanceCostCenterQuery,
            FinanceGLAccountQuery,
            FinanceTaxRateQuery,
            OrganizationClasspassQuery,
            OrganizationClasspassGroupQuery,
            OrganizationClasstypeQuery,
            OrganizationDiscoveryQuery,
            OrganizationLocationQuery, 
            OrganizationLevelQuery, 
            OrganizationMembershipQuery,
            UserQuery, 
            graphene.ObjectType):
    node = graphene.relay.Node.Field()


class Mutation(FinanceCostCenterMutation,
               FinanceGLAccountMutation,
               FinanceTaxRateMutation,
               OrganizationClasspassMutation,
               OrganizationClasspassGroupMutation,
               OrganizationClasspassGroupClasspassMutation,
               OrganizationClasstypeMutation,
               OrganizationDiscoveryMutation,
               OrganizationLocationMutation,
               OrganizationLevelMutation,
               OrganizationMembershipMutation, 
               UserMutation, 
               graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

