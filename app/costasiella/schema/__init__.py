import graphene
import graphql_jwt

from .account import AccountQuery, AccountMutation
from .account_classpass import AccountClasspassQuery, AccountClasspassMutation
from .account_membership import AccountMembershipQuery, AccountMembershipMutation
from .account_subscription import AccountSubscriptionQuery, AccountSubscriptionMutation

from .finance_costcenter import FinanceCostCenterQuery, FinanceCostCenterMutation
from .finance_glaccount import FinanceGLAccountQuery, FinanceGLAccountMutation
from .finance_payment_method import FinancePaymentMethodQuery, FinancePaymentMethodMutation
from .finance_taxrate import FinanceTaxRateQuery, FinanceTaxRateMutation

from .organization_appointment import OrganizationAppointmentQuery, OrganizationAppointmentMutation
from .organization_appointment_category import OrganizationAppointmentCategoryQuery, OrganizationAppointmentCategoryMutation
from .organization_classpass import OrganizationClasspassQuery, OrganizationClasspassMutation
from .organization_classpass_group import OrganizationClasspassGroupQuery, OrganizationClasspassGroupMutation
from .organization_classpass_group_classpass import OrganizationClasspassGroupClasspassMutation
from .organization_classtype import OrganizationClasstypeQuery, OrganizationClasstypeMutation
from .organization_discovery import OrganizationDiscoveryQuery, OrganizationDiscoveryMutation
from .organization_location import OrganizationLocationQuery, OrganizationLocationMutation
from .organization_location_room import OrganizationLocationRoomQuery, OrganizationLocationRoomMutation
from .organization_level import OrganizationLevelQuery, OrganizationLevelMutation
from .organization_membership import OrganizationMembershipQuery, OrganizationMembershipMutation
from .organization_subscription import OrganizationSubscriptionQuery, OrganizationSubscriptionMutation
from .organization_subscription_group import OrganizationSubscriptionGroupQuery, OrganizationSubscriptionGroupMutation
from .organization_subscription_group_subscription import OrganizationSubscriptionGroupSubscriptionMutation
from .organization_subscription_price import OrganizationSubscriptionPriceQuery, OrganizationSubscriptionPriceMutation

from .schedule_item import ScheduleItemQuery, ScheduleItemMutation
from .schedule_item_organization_classpass_group import ScheduleItemOrganizationClasspassGroupQuery, ScheduleItemOrganizationClasspassGroupMutation
from .schedule_item_organization_subscription_group import ScheduleItemOrganizationSubscriptionGroupQuery, ScheduleItemOrganizationSubscriptionGroupMutation
from .schedule_item_teacher import ScheduleItemTeacherQuery, ScheduleItemTeacherMutation


class Query(AccountQuery,
            AccountClasspassQuery,
            AccountMembershipQuery,
            AccountSubscriptionQuery,
            FinanceCostCenterQuery,
            FinanceGLAccountQuery,
            FinancePaymentMethodQuery,
            FinanceTaxRateQuery,
            OrganizationAppointmentQuery,
            OrganizationAppointmentCategoryQuery,
            OrganizationClasspassQuery,
            OrganizationClasspassGroupQuery,
            OrganizationClasstypeQuery,
            OrganizationDiscoveryQuery,
            OrganizationLocationQuery, 
            OrganizationLocationRoomQuery, 
            OrganizationLevelQuery, 
            OrganizationMembershipQuery,
            OrganizationSubscriptionQuery,
            OrganizationSubscriptionGroupQuery,
            OrganizationSubscriptionPriceQuery,
            ScheduleItemQuery,
            ScheduleItemOrganizationClasspassGroupQuery,
            ScheduleItemOrganizationSubscriptionGroupQuery,
            ScheduleItemTeacherQuery,
            graphene.ObjectType):
    node = graphene.relay.Node.Field()


class Mutation(AccountMutation,
               AccountClasspassMutation,
               AccountMembershipMutation,
               AccountSubscriptionMutation,
               FinanceCostCenterMutation,
               FinanceGLAccountMutation,
               FinancePaymentMethodMutation,
               FinanceTaxRateMutation,
               OrganizationAppointmentMutation,
               OrganizationAppointmentCategoryMutation,
               OrganizationClasspassMutation,
               OrganizationClasspassGroupMutation,
               OrganizationClasspassGroupClasspassMutation,
               OrganizationClasstypeMutation,
               OrganizationDiscoveryMutation,
               OrganizationLocationMutation,
               OrganizationLocationRoomMutation,
               OrganizationLevelMutation,
               OrganizationMembershipMutation, 
               OrganizationSubscriptionMutation, 
               OrganizationSubscriptionGroupMutation, 
               OrganizationSubscriptionGroupSubscriptionMutation, 
               OrganizationSubscriptionPriceMutation, 
               ScheduleItemMutation,
               ScheduleItemOrganizationClasspassGroupMutation,
               ScheduleItemOrganizationSubscriptionGroupMutation,
               ScheduleItemTeacherMutation,
               graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

