import graphene
from graphene_django.debug import DjangoDebug
import graphql_jwt

from .account import AccountQuery, AccountMutation
from .account_accepted_document import AccountAcceptedDocumentQuery
from .account_bank_account import AccountBankAccountQuery, AccountBankAccountMutation
from .account_bank_account_mandate import AccountBankAccountMandateQuery, AccountBankAccountMandateMutation
from .account_classpass import AccountClasspassQuery, AccountClasspassMutation
from .account_document import AccountDocumentQuery, AccountDocumentMutation
from .account_finance_payment_batch_category_item import \
    AccountFinancePaymentBatchCategoryItemQuery,\
    AccountFinancePaymentBatchCategoryItemMutation
# from .account_membership import AccountMembershipQuery, AccountMembershipMutation
from .account_note import AccountNoteQuery, AccountNoteMutation
from .account_product import AccountProductQuery, AccountProductMutation
from .account_schedule_event_ticket import AccountScheduleEventTicketQuery, AccountScheduleEventTicketMutation
from .account_subscription import AccountSubscriptionQuery, AccountSubscriptionMutation
from .account_subscription_alt_price import AccountSubscriptionAltPriceQuery, AccountSubscriptionAltPriceMutation
from .account_subscription_block import AccountSubscriptionBlockQuery, AccountSubscriptionBlockMutation
from .account_subscription_credit import AccountSubscriptionCreditQuery, AccountSubscriptionCreditMutation
from .account_subscription_pause import AccountSubscriptionPauseQuery, AccountSubscriptionPauseMutation
from .account_instructor_profile import AccountInstructorProfileQuery, AccountInstructorProfileMutation

from .app_settings import AppSettingsQuery, AppSettingsMutation

from .business import BusinessQuery, BusinessMutation

from .django_celery_result_task_result import DjangoCeleryResultTaskResultQuery

from .finance_costcenter import FinanceCostCenterQuery, FinanceCostCenterMutation
from .finance_expense import FinanceExpenseQuery, FinanceExpenseMutation
from .finance_glaccount import FinanceGLAccountQuery, FinanceGLAccountMutation
from .finance_invoice import FinanceInvoiceQuery, FinanceInvoiceMutation
from .finance_invoice_group import FinanceInvoiceGroupQuery, FinanceInvoiceGroupMutation
from .finance_invoice_group_default import FinanceInvoiceGroupDefaultQuery, FinanceInvoiceGroupDefaultMutation
from .finance_invoice_item import FinanceInvoiceItemQuery, FinanceInvoiceItemMutation
from .finance_invoice_payment import FinanceInvoicePaymentQuery, FinanceInvoicePaymentMutation
from .finance_invoice_payment_link import FinanceInvoicePaymentLinkMutation
from .finance_order import FinanceOrderQuery, FinanceOrderMutation
from .finance_order_payment_link import FinanceOrderPaymentLinkMutation
from .finance_order_item import FinanceOrderItemQuery
from .finance_payment_batch import FinancePaymentBatchQuery, FinancePaymentBatchMutation
from .finance_payment_batch_category import FinancePaymentBatchCategoryQuery, FinancePaymentBatchCategoryMutation
from .finance_payment_batch_export import FinancePaymentBatchExportQuery
from .finance_payment_batch_item import FinancePaymentBatchItemQuery
from .finance_payment_method import FinancePaymentMethodQuery, FinancePaymentMethodMutation
from .finance_quote import FinanceQuoteQuery, FinanceQuoteMutation
from .finance_quote_group import FinanceQuoteGroupQuery, FinanceQuoteGroupMutation
from .finance_quote_item import FinanceQuoteItemQuery, FinanceQuoteItemMutation
from .finance_tax_rate import FinanceTaxRateQuery, FinanceTaxRateMutation

from .insight_account_inactive import InsightAccountInactiveQuery, InsightAccountInactiveMutation
from .insight_account_inactive_account import InsightAccountInactiveAccountQuery
from .insight_classpasses import InsightClasspassesQuery
from .insight_class_attendance import InsightClassAttendanceQuery
from .insight_finance_open_invoices import InsightFinanceOpenInvoicesQuery
from .insight_finance_tax_rate_summary import InsightFinanceTaxRateSummaryQuery
from .insight_instructor_classes_month import InsightInstructorClassesMonthQuery
from .insight_subscriptions import InsightSubscriptionsQuery
from .insight_revenue import InsightRevenueQuery
from .insight_revenue_classpasses import InsightRevenueClasspassesQuery
from .insight_revenue_event_tickets import InsightRevenueEventTicketsQuery
from .insight_revenue_other import InsightRevenueOtherQuery
from .insight_revenue_subscriptions import InsightRevenueSubscriptionsQuery


from .organization import OrganizationQuery, OrganizationMutation
from .organization_announcement import OrganizationAnnouncementQuery, OrganizationAnnouncementMutation
from .organization_appointment import OrganizationAppointmentQuery, OrganizationAppointmentMutation
from .organization_appointment_category import OrganizationAppointmentCategoryQuery, OrganizationAppointmentCategoryMutation
from .organization_appointment_price import OrganizationAppointmentPriceQuery, OrganizationAppointmentPriceMutation
from .organization_classpass import OrganizationClasspassQuery, OrganizationClasspassMutation
from .organization_classpass_group import OrganizationClasspassGroupQuery, OrganizationClasspassGroupMutation
from .organization_classpass_group_classpass import OrganizationClasspassGroupClasspassMutation
from .organization_classtype import OrganizationClasstypeQuery, OrganizationClasstypeMutation
from .organization_discovery import OrganizationDiscoveryQuery, OrganizationDiscoveryMutation
from .organization_document import OrganizationDocumentQuery, OrganizationDocumentMutation
from .organization_holiday import OrganizationHolidayQuery, OrganizationHolidayMutation
from .organization_holiday_location import OrganizationHolidayLocationMutation
from .organization_location import OrganizationLocationQuery, OrganizationLocationMutation
from .organization_location_room import OrganizationLocationRoomQuery, OrganizationLocationRoomMutation
from .organization_language import OrganizationLanguageQuery, OrganizationLanguageMutation
from .organization_level import OrganizationLevelQuery, OrganizationLevelMutation
# from .organization_membership import OrganizationMembershipQuery, OrganizationMembershipMutation
from .organization_product import OrganizationProductQuery, OrganizationProductMutation
from .organization_shift import OrganizationShiftQuery, OrganizationShiftMutation
from .organization_subscription import OrganizationSubscriptionQuery, OrganizationSubscriptionMutation
from .organization_subscription_group import OrganizationSubscriptionGroupQuery, OrganizationSubscriptionGroupMutation
from .organization_subscription_group_subscription import OrganizationSubscriptionGroupSubscriptionMutation
from .organization_subscription_price import OrganizationSubscriptionPriceQuery, OrganizationSubscriptionPriceMutation

from .schedule_appointment import ScheduleAppointmentQuery, ScheduleAppointmentMutation
from .schedule_class import ScheduleClassQuery, ScheduleClassMutation
from .schedule_class_booking_option import ScheduleClassBookingOptionsQuery
from .schedule_class_enrollment_option import ScheduleClassEnrollmentOptionsQuery
from .schedule_item_weekly_otc import ScheduleItemWeeklyOTCQuery, ScheduleItemWeeklyOTCMutation
from .schedule_event import ScheduleEventQuery, ScheduleEventMutation
from .schedule_event_earlybird import ScheduleEventEarlybirdQuery, ScheduleEventEarlybirdMutation
from .schedule_event_media import ScheduleEventMediaQuery, ScheduleEventMediaMutation
from .schedule_event_subscription_group_discount import \
    ScheduleEventSubscriptionGroupDiscountQuery, ScheduleEventSubscriptionGroupDiscountMutation
from .schedule_event_ticket import ScheduleEventTicketQuery, ScheduleEventTicketMutation
from .schedule_event_ticket_schedule_item import \
    ScheduleEventTicketScheduleItemQuery, ScheduleEventTicketScheduleItemMutation
from .schedule_item import ScheduleItemQuery, ScheduleItemMutation
from .schedule_item_account import ScheduleItemAccountQuery, ScheduleItemAccountMutation
from .schedule_item_attendance import ScheduleItemAttendanceQuery, ScheduleItemAttendanceMutation
from .schedule_item_enrollment import ScheduleItemEnrollmentQuery, ScheduleItemEnrollmentMutation
from .schedule_item_organization_classpass_group import \
    ScheduleItemOrganizationClasspassGroupQuery, ScheduleItemOrganizationClasspassGroupMutation
from .schedule_item_organization_subscription_group import \
    ScheduleItemOrganizationSubscriptionGroupQuery, ScheduleItemOrganizationSubscriptionGroupMutation
from .schedule_item_price import ScheduleItemPriceQuery, ScheduleItemPriceMutation
from .schedule_item_instructor_available import \
    ScheduleItemInstructorAvailableQuery, ScheduleItemInstructorAvailableMutation
from .schedule_shift import ScheduleShiftQuery, ScheduleShiftMutation

from .system_feature_shop import SystemFeatureShopQuery, SystemFeatureShopMutation
from .system_mailchimp_list import SystemMailChimpListQuery, SystemMailChimpListMutation
from .system_mail_template import SystemMailTemplateQuery, SystemMailTemplateMutation
from .system_notification import SystemNotificationQuery
from .system_notification_account import SystemNotificationAccountQuery, SystemNotificationAccountMutation
from .system_setting import SystemSettingQuery, SystemSettingMutation


class Query(AccountQuery,
            AccountAcceptedDocumentQuery,
            AccountBankAccountQuery,
            AccountBankAccountMandateQuery,
            AccountClasspassQuery,
            AccountDocumentQuery,
            AccountFinancePaymentBatchCategoryItemQuery,
            AccountNoteQuery,
            AccountProductQuery,
            AccountScheduleEventTicketQuery,
            AccountSubscriptionQuery,
            AccountSubscriptionAltPriceQuery,
            AccountSubscriptionBlockQuery,
            AccountSubscriptionCreditQuery,
            AccountSubscriptionPauseQuery,
            AccountInstructorProfileQuery,
            AppSettingsQuery,
            BusinessQuery,
            DjangoCeleryResultTaskResultQuery,
            FinanceCostCenterQuery,
            FinanceExpenseQuery,
            FinanceGLAccountQuery,
            FinanceInvoiceQuery,
            FinanceInvoiceGroupQuery,
            FinanceInvoiceGroupDefaultQuery,
            FinanceInvoiceItemQuery,
            FinanceInvoicePaymentQuery,
            FinanceOrderQuery,
            FinanceOrderItemQuery,
            FinancePaymentBatchQuery,
            FinancePaymentBatchCategoryQuery,
            FinancePaymentBatchExportQuery,
            FinancePaymentBatchItemQuery,
            FinancePaymentMethodQuery,
            FinanceQuoteQuery,
            FinanceQuoteGroupQuery,
            FinanceQuoteItemQuery,
            FinanceTaxRateQuery,
            InsightAccountInactiveQuery,
            InsightAccountInactiveAccountQuery,
            InsightClasspassesQuery,
            InsightClassAttendanceQuery,
            InsightFinanceOpenInvoicesQuery,
            InsightFinanceTaxRateSummaryQuery,
            InsightInstructorClassesMonthQuery,
            InsightRevenueQuery,
            InsightRevenueClasspassesQuery,
            InsightRevenueEventTicketsQuery,
            InsightRevenueOtherQuery,
            InsightRevenueSubscriptionsQuery,
            InsightSubscriptionsQuery,
            OrganizationQuery,
            OrganizationAnnouncementQuery,
            OrganizationAppointmentQuery,
            OrganizationAppointmentCategoryQuery,
            OrganizationAppointmentPriceQuery,
            OrganizationClasspassQuery,
            OrganizationClasspassGroupQuery,
            OrganizationClasstypeQuery,
            OrganizationDiscoveryQuery,
            OrganizationDocumentQuery,
            OrganizationHolidayQuery,
            OrganizationLocationQuery, 
            OrganizationLocationRoomQuery,
            OrganizationLanguageQuery,
            OrganizationLevelQuery,
            OrganizationProductQuery,
            OrganizationShiftQuery,
            OrganizationSubscriptionQuery,
            OrganizationSubscriptionGroupQuery,
            OrganizationSubscriptionPriceQuery,
            ScheduleAppointmentQuery,
            ScheduleClassQuery,
            ScheduleClassBookingOptionsQuery,
            ScheduleClassEnrollmentOptionsQuery,
            ScheduleEventQuery,
            ScheduleEventEarlybirdQuery,
            ScheduleEventMediaQuery,
            ScheduleEventSubscriptionGroupDiscountQuery,
            ScheduleEventTicketQuery,
            ScheduleEventTicketScheduleItemQuery,
            ScheduleItemQuery,
            ScheduleItemAccountQuery,
            ScheduleItemAttendanceQuery,
            ScheduleItemEnrollmentQuery,
            ScheduleItemOrganizationClasspassGroupQuery,
            ScheduleItemOrganizationSubscriptionGroupQuery,
            ScheduleItemPriceQuery,
            ScheduleItemInstructorAvailableQuery,
            ScheduleItemWeeklyOTCQuery,
            ScheduleShiftQuery,
            SystemFeatureShopQuery,
            SystemMailChimpListQuery,
            SystemMailTemplateQuery,
            SystemNotificationQuery,
            SystemNotificationAccountQuery,
            SystemSettingQuery,
            graphene.ObjectType):
    node = graphene.relay.Node.Field()
    debug = graphene.Field(DjangoDebug, name="_debug")


class Mutation(AccountMutation,
               AccountBankAccountMutation,
               AccountBankAccountMandateMutation,
               AccountClasspassMutation,
               AccountDocumentMutation,
               AccountFinancePaymentBatchCategoryItemMutation,
               AccountNoteMutation,
               AccountProductMutation,
               AccountSubscriptionMutation,
               AccountScheduleEventTicketMutation,
               AccountSubscriptionAltPriceMutation,
               AccountSubscriptionBlockMutation,
               AccountSubscriptionCreditMutation,
               AccountSubscriptionPauseMutation,
               AccountInstructorProfileMutation,
               AppSettingsMutation,
               BusinessMutation,
               FinanceCostCenterMutation,
               FinanceExpenseMutation,
               FinanceGLAccountMutation,
               FinanceInvoiceMutation,
               FinanceInvoiceGroupMutation,
               FinanceInvoiceGroupDefaultMutation,
               FinanceInvoiceItemMutation,
               FinanceInvoicePaymentMutation,
               FinanceInvoicePaymentLinkMutation,
               FinanceOrderMutation,
               FinanceOrderPaymentLinkMutation,
               FinancePaymentBatchMutation,
               FinancePaymentBatchCategoryMutation,
               FinancePaymentMethodMutation,
               FinanceQuoteMutation,
               FinanceQuoteGroupMutation,
               FinanceQuoteItemMutation,
               FinanceTaxRateMutation,
               InsightAccountInactiveMutation,
               OrganizationMutation,
               OrganizationAnnouncementMutation,
               OrganizationAppointmentMutation,
               OrganizationAppointmentCategoryMutation,
               OrganizationAppointmentPriceMutation,
               OrganizationClasspassMutation,
               OrganizationClasspassGroupMutation,
               OrganizationClasspassGroupClasspassMutation,
               OrganizationClasstypeMutation,
               OrganizationDiscoveryMutation,
               OrganizationDocumentMutation,
               OrganizationHolidayMutation,
               OrganizationHolidayLocationMutation,
               OrganizationLanguageMutation,
               OrganizationLocationMutation,
               OrganizationLocationRoomMutation,
               OrganizationLevelMutation,
               OrganizationProductMutation,
               OrganizationShiftMutation,
               OrganizationSubscriptionMutation, 
               OrganizationSubscriptionGroupMutation, 
               OrganizationSubscriptionGroupSubscriptionMutation, 
               OrganizationSubscriptionPriceMutation, 
               ScheduleAppointmentMutation,
               ScheduleClassMutation,
               ScheduleEventMutation,
               ScheduleEventEarlybirdMutation,
               ScheduleEventMediaMutation,
               ScheduleEventSubscriptionGroupDiscountMutation,
               ScheduleEventTicketMutation,
               ScheduleEventTicketScheduleItemMutation,
               ScheduleItemMutation,
               ScheduleItemAccountMutation,
               ScheduleItemAttendanceMutation,
               ScheduleItemEnrollmentMutation,
               ScheduleItemOrganizationClasspassGroupMutation,
               ScheduleItemOrganizationSubscriptionGroupMutation,
               ScheduleItemPriceMutation,
               ScheduleItemInstructorAvailableMutation,
               ScheduleItemWeeklyOTCMutation,
               ScheduleShiftMutation,
               SystemFeatureShopMutation,
               SystemMailChimpListMutation,
               SystemMailTemplateMutation,
               SystemNotificationAccountMutation,
               SystemSettingMutation,
               graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()
    delete_token_cookie = graphql_jwt.DeleteJSONWebTokenCookie.Field()
    # Long running refresh tokens
    delete_refresh_token_cookie = graphql_jwt.DeleteRefreshTokenCookie.Field()


# Main schema definition
schema = graphene.Schema(query=Query, mutation=Mutation)
