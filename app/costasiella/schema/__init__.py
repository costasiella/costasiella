import graphene
import graphql_jwt

from .account import AccountQuery, AccountMutation
from .account_classpass import AccountClasspassQuery, AccountClasspassMutation
from .account_membership import AccountMembershipQuery, AccountMembershipMutation
from .account_subscription import AccountSubscriptionQuery, AccountSubscriptionMutation
from .account_teacher_profile import AccountTeacherProfileQuery, AccountTeacherProfileMutation

from .finance_costcenter import FinanceCostCenterQuery, FinanceCostCenterMutation
from .finance_glaccount import FinanceGLAccountQuery, FinanceGLAccountMutation
from .finance_invoice import FinanceInvoiceQuery, FinanceInvoiceMutation
from .finance_invoice_group import FinanceInvoiceGroupQuery, FinanceInvoiceGroupMutation
from .finance_invoice_group_default import FinanceInvoiceGroupDefaultQuery, FinanceInvoiceGroupDefaultMutation
from .finance_invoice_item import FinanceInvoiceItemQuery, FinanceInvoiceItemMutation
from .finance_payment_method import FinancePaymentMethodQuery, FinancePaymentMethodMutation
from .finance_tax_rate import FinanceTaxRateQuery, FinanceTaxRateMutation

from .organization import OrganizationQuery, OrganizationMutation
from .organization_appointment import OrganizationAppointmentQuery, OrganizationAppointmentMutation
from .organization_appointment_category import OrganizationAppointmentCategoryQuery, OrganizationAppointmentCategoryMutation
from .organization_appointment_price import OrganizationAppointmentPriceQuery, OrganizationAppointmentPriceMutation
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

from .schedule_appointment import ScheduleAppointmentQuery, ScheduleAppointmentMutation
from .schedule_class import ScheduleClassQuery, ScheduleClassMutation
from .schedule_class_booking_option import ScheduleClassBookingOptionsQuery
from .schedule_item import ScheduleItemQuery, ScheduleItemMutation
from .schedule_item_attendance import ScheduleItemAttendanceQuery, ScheduleItemAttendanceMutation
from .schedule_item_organization_classpass_group import ScheduleItemOrganizationClasspassGroupQuery, ScheduleItemOrganizationClasspassGroupMutation
from .schedule_item_organization_subscription_group import ScheduleItemOrganizationSubscriptionGroupQuery, ScheduleItemOrganizationSubscriptionGroupMutation
from .schedule_item_teacher import ScheduleItemTeacherQuery, ScheduleItemTeacherMutation
from .schedule_item_teacher_available import ScheduleItemTeacherAvailableQuery, ScheduleItemTeacherAvailableMutation


class Query(AccountQuery,
            AccountClasspassQuery,
            AccountMembershipQuery,
            AccountSubscriptionQuery,
            AccountTeacherProfileQuery,
            FinanceCostCenterQuery,
            FinanceGLAccountQuery,
            FinanceInvoiceQuery,
            FinanceInvoiceGroupQuery,
            FinanceInvoiceGroupDefaultQuery,
            FinanceInvoiceItemQuery,
            FinancePaymentMethodQuery,
            FinanceTaxRateQuery,
            OrganizationQuery,
            OrganizationAppointmentQuery,
            OrganizationAppointmentCategoryQuery,
            OrganizationAppointmentPriceQuery,
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
            ScheduleAppointmentQuery,
            ScheduleClassQuery,
            ScheduleClassBookingOptionsQuery,
            ScheduleItemQuery,
            ScheduleItemAttendanceQuery,
            ScheduleItemOrganizationClasspassGroupQuery,
            ScheduleItemOrganizationSubscriptionGroupQuery,
            ScheduleItemTeacherQuery,
            ScheduleItemTeacherAvailableQuery,
            graphene.ObjectType):
    node = graphene.relay.Node.Field()


class Mutation(AccountMutation,
               AccountClasspassMutation,
               AccountMembershipMutation,
               AccountSubscriptionMutation,
               AccountTeacherProfileMutation,
               FinanceCostCenterMutation,
               FinanceGLAccountMutation,
               FinanceInvoiceMutation,
               FinanceInvoiceGroupMutation,
               FinanceInvoiceGroupDefaultMutation,
               FinanceInvoiceItemMutation,
               FinancePaymentMethodMutation,
               FinanceTaxRateMutation,
               OrganizationMutation,
               OrganizationAppointmentMutation,
               OrganizationAppointmentCategoryMutation,
               OrganizationAppointmentPriceMutation,
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
               ScheduleAppointmentMutation,
               ScheduleClassMutation,
               ScheduleItemMutation,
               ScheduleItemAttendanceMutation,
               ScheduleItemOrganizationClasspassGroupMutation,
               ScheduleItemOrganizationSubscriptionGroupMutation,
               ScheduleItemTeacherMutation,
               ScheduleItemTeacherAvailableMutation,
               graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

