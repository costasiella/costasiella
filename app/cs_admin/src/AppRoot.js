// import React, { Component } from 'react';
// import logo from './logo.svg';

import React, { Component } from 'react'
import {
  Route, 
  Switch, 
  HashRouter,
  Redirect
} from 'react-router-dom'
import { withTranslation } from 'react-i18next'
import { useQuery, useMutation } from "react-apollo"
import { toast } from 'react-toastify'

import { GET_APP_SETTINGS_QUERY } from "./components/settings/general/date_time/queries"
import { GET_ORGANIZATION_QUERY } from "./components/organization/organization/queries"
import { TOKEN_REFRESH } from "./queries/system/auth"

// Import moment locale
import moment from 'moment'
import 'moment/locale/nl'

import { AppSettingsProvider } from "./components/context/AppSettingsContext"
import { OrganizationProvider } from "./components/context/OrganizationContext"

import HomeHome from './components/home/home/HomeHome'

import AutomationHome from './components/automation/home/AutomationHome'
import AutomationAccountSubscriptionCredits from './components/automation/account/subscription/credits/AutomationAccountSubscriptionCredits'
import AutomationAccountSubscriptionInvoices from './components/automation/account/subscription/invoices/AutomationAccountSubscriptionInvoices'
import AutomationAccountSubscriptionInvoicesAdd from './components/automation/account/subscription/invoices/AutomationAccountSubscriptionInvoicesAdd'
import AutomationAccountSubscriptionCreditAdd from './components/automation/account/subscription/credits/AutomationAccountSubscriptionCreditAdd'
import AutomationAccountSubscriptionMollieCollections 
  from './components/automation/account/subscription/mollie_collection/AutomationAccountSubscriptionMollieCollections'
import AutomationAccountSubscriptionMollieCollectionAdd
  from './components/automation/account/subscription/mollie_collection/AutomationAccountSubscriptionMollieCollectionAdd'

import FinanceHome from './components/finance/home/FinanceHome'
import FinanceCostCenters from './components/finance/costcenters/FinanceCostCenters'
import FinanceCostCenterAdd from './components/finance/costcenters/FinanceCostCenterAdd'
import FinanceCostCenterEdit from './components/finance/costcenters/FinanceCostCenterEdit'
import FinanceGLAccounts from './components/finance/glaccounts/FinanceGLAccounts'
import FinanceGLAccountAdd from './components/finance/glaccounts/FinanceGLAccountAdd'
import FinanceGLAccountEdit from './components/finance/glaccounts/FinanceGLAccountEdit'
import FinanceInvoices from './components/finance/invoices/FinanceInvoices'
import FinanceInvoiceEdit from './components/finance/invoices/edit/FinanceInvoiceEdit'
import FinanceInvoiceGroups from './components/finance/invoices/groups/FinanceInvoiceGroups'
import FinanceInvoiceGroupAdd from './components/finance/invoices/groups/FinanceInvoiceGroupAdd'
import FinanceInvoiceGroupEdit from './components/finance/invoices/groups/FinanceInvoiceGroupEdit'
import FinanceInvoiceGroupDefaults from './components/finance/invoices/groups/defaults/FinanceInvoiceGroupDefaults'
import FinanceInvoicePaymentAdd from './components/finance/invoices/payments/FinanceInvoicePaymentAdd'
import FinanceInvoicePaymentEdit from './components/finance/invoices/payments/FinanceInvoicePaymentEdit'
import FinanceOrders from './components/finance/orders/FinanceOrders'
import FinancePaymentBatches from './components/finance/payment_batches/FinancePaymentBatches'
import FinancePaymentBatchAddWhat from './components/finance/payment_batches/FinancePaymentBatchAddWhat'
import FinancePaymentBatchView from './components/finance/payment_batches/FinancePaymentBatchView'
import FinancePaymentCollectionBatchAdd from './components/finance/payment_batches/FinancePaymentCollectionBatchAdd'
import FinancePaymentCollectionBatchEdit from './components/finance/payment_batches/FinancePaymentCollectionBatchEdit'
import FinancePaymentBatchCategories from './components/finance/payment_batch_categories/FinancePaymentBatchCategories'
import FinancePaymentBatchCategoryAdd from './components/finance/payment_batch_categories/FinancePaymentBatchCategoryAdd'
import FinancePaymentBatchCategoryEdit from './components/finance/payment_batch_categories/FinancePaymentBatchCategoryEdit'
import FinanceOrderEdit from './components/finance/orders/edit/FinanceOrderEdit'
import FinancePaymentMethods from './components/finance/payment_methods/FinancePaymentMethods'
import FinancePaymentMethodAdd from './components/finance/payment_methods/FinancePaymentMethodAdd'
import FinancePaymentMethodEdit from './components/finance/payment_methods/FinancePaymentMethodEdit'
import FinanceTaxRates from './components/finance/taxrates/FinanceTaxRates'
import FinanceTaxRatesAdd from './components/finance/taxrates/FinanceTaxRateAdd'
import FinanceTaxRatesEdit from './components/finance/taxrates/FinanceTaxRateEdit'

import InsightHome from './components/insight/home/InsightHome'
import InsightClasspasses from './components/insight/classpasses/InsightClasspasses'
import InsightSubscriptions from './components/insight/subscriptions/InsightSubscriptions'

import OrganizationHome from './components/organization/home/OrganizationHome'
import OrganizationEdit from './components/organization/organization/OrganizationEdit'
import OrganizationBranding from './components/organization/organization/branding/OrganizationBranding'
import OrganizationBrandingEdit from './components/organization/organization/branding/OrganizationBrandingEdit'
import OrganizationAnnouncements from './components/organization/announcements/OrganizationAnnouncements'
import OrganizationAnnouncementAdd from './components/organization/announcements/OrganizationAnnouncementAdd'
import OrganizationAnnouncementEdit from './components/organization/announcements/OrganizationAnnouncementEdit'
import OrganizationAppointments from './components/organization/appointment_categories/appointments/OrganizationAppointments'
import OrganizationAppointmentAdd from './components/organization/appointment_categories/appointments/OrganizationAppointmentAdd'
import OrganizationAppointmentEdit from './components/organization/appointment_categories/appointments/OrganizationAppointmentEdit'
import OrganizationAppointmentCategories from './components/organization/appointment_categories/OrganizationAppointmentCategories'
import OrganizationAppointmentCategoryAdd from './components/organization/appointment_categories/OrganizationAppointmentCategoryAdd'
import OrganizationAppointmentCategoryEdit from './components/organization/appointment_categories/OrganizationAppointmentCategoryEdit'
import OrganizationAppointmentPrices from './components/organization/appointment_categories/appointments/prices/OrganizationAppointmentPrices'
import OrganizationAppointmentPriceAdd from './components/organization/appointment_categories/appointments/prices/OrganizationAppointmentPriceAdd'
import OrganizationAppointmentPriceEdit from './components/organization/appointment_categories/appointments/prices/OrganizationAppointmentPriceEdit'
import OrganizationClasspasses from './components/organization/classpasses/OrganizationClasspasses'
import OrganizationClasspassAdd from './components/organization/classpasses/OrganizationClasspassAdd'
import OrganizationClasspassEdit from './components/organization/classpasses/OrganizationClasspassEdit'
import OrganizationClasspassesGroups from './components/organization/classpasses_groups/OrganizationClasspassesGroups'
import OrganizationClasspassesGroupAdd from './components/organization/classpasses_groups/OrganizationClasspassesGroupAdd'
import OrganizationClasspassesGroupEdit from './components/organization/classpasses_groups/OrganizationClasspassesGroupEdit'
import OrganizationClasspassesGroupEditPasses from './components/organization/classpasses_groups/OrganizationClasspassesGroupEditPasses'
import OrganizationClasstypes from './components/organization/classtypes/OrganizationClasstypes'
import OrganizationClasstypeAdd from './components/organization/classtypes/OrganizationClasstypeAdd'
import OrganizationClasstypeEdit from './components/organization/classtypes/OrganizationClasstypeEdit'
import OrganizationClasstypeEditImage from './components/organization/classtypes/OrganizationClasstypeEditImage'
import OrganizationDiscoveries from './components/organization/discovery/OrganizationDiscoveries'
import OrganizationDiscoveryAdd from './components/organization/discovery/OrganizationDiscoveryAdd'
import OrganizationDiscoveryEdit from './components/organization/discovery/OrganizationDiscoveryEdit'
import OrganizationDocuments from './components/organization/organization/documents/OrganizationDocuments'
import OrganizationListDocuments from './components/organization/organization/documents/OrganizationListDocuments'
import OrganizationDocumentAdd from './components/organization/organization/documents/OrganizationDocumentAdd'
import OrganizationDocumentEdit from './components/organization/organization/documents/OrganizationDocumentEdit'
import OrganizationLocations from './components/organization/locations/OrganizationLocations'
import OrganizationLocationAdd from './components/organization/locations/OrganizationLocationAdd'
import OrganizationLocationEdit from './components/organization/locations/OrganizationLocationEdit'
import OrganizationLocationRooms from './components/organization/locations/rooms/OrganizationLocationRooms'
import OrganizationLocationRoomAdd from './components/organization/locations/rooms/OrganizationLocationRoomAdd'
import OrganizationLocationRoomEdit from './components/organization/locations/rooms/OrganizationLocationRoomEdit'
import OrganizationLevels from './components/organization/levels/OrganizationLevels'
import OrganizationLevelAdd from './components/organization/levels/OrganizationLevelAdd'
import OrganizationLevelEdit from './components/organization/levels/OrganizationLevelEdit'
import OrganizationMemberships from './components/organization/memberships/OrganizationMemberships'
import OrganizationMembershipAdd from './components/organization/memberships/OrganizationMembershipAdd'
import OrganizationMembershipEdit from './components/organization/memberships/OrganizationMembershipEdit'
import OrganizationSubscriptions from './components/organization/subscriptions/OrganizationSubscriptions'
import OrganizationSubscriptionAdd from './components/organization/subscriptions/OrganizationSubscriptionAdd'
import OrganizationSubscriptionEdit from './components/organization/subscriptions/OrganizationSubscriptionEdit'
import OrganizationSubscriptionsGroups from './components/organization/subscriptions_groups/OrganizationSubscriptionsGroups'
import OrganizationSubscriptionsGroupAdd from './components/organization/subscriptions_groups/OrganizationSubscriptionsGroupAdd'
import OrganizationSubscriptionsGroupEdit from './components/organization/subscriptions_groups/OrganizationSubscriptionsGroupEdit'
import OrganizationSubscriptionsGroupEditSubscriptions from './components/organization/subscriptions_groups/OrganizationSubscriptionsGroupEditSubscriptions'
import OrganizationSubscriptionsPrices from './components/organization/subscriptions/prices/OrganizationSubscriptionsPrices'
import OrganizationSubscriptionPriceAdd from './components/organization/subscriptions/prices/OrganizationSubscriptionPriceAdd'
import OrganizationSubscriptionPriceEdit from './components/organization/subscriptions/prices/OrganizationSubscriptionPriceEdit'

import RelationsHome from './components/relations/home/RelationsHome'
import RelationsAccounts from './components/relations/accounts/RelationsAccounts'
import RelationsAccountAdd from './components/relations/accounts/RelationsAccountAdd'
import RelationsAccountProfile from './components/relations/accounts/RelationsAccountProfile'
import AccountAcceptedDocuments from './components/relations/accounts/accepted_documents/AcceptedDocuments.jsx'
import RelationsAccountBankAccount from './components/relations/accounts/bank_accounts/RelationsAccountBankAccount'
import RelationsAccountBankAccountMandateAdd from './components/relations/accounts/bank_accounts/mandates/RelationsAccountBankAccountMandateAdd'
import RelationsAccountBankAccountMandateEdit from './components/relations/accounts/bank_accounts/mandates/RelationsAccountBankAccountMandateEdit'
import RelationsAccountClasses from './components/relations/accounts/classes/AccountClasses'
import AccountClasspasses from './components/relations/accounts/classpasses/AccountClasspasses'
import AccountClasspassAdd from './components/relations/accounts/classpasses/AccountClasspassAdd'
import AccountClasspassEdit from './components/relations/accounts/classpasses/AccountClasspassEdit'
import AccountFinancePaymentBatchCategoryItems from 
  './components/relations/accounts/finance_payment_batch_category_items/AccountFinancePaymentBatchCategoryItems'
import AccountFinancePaymentBatchCategoryItemAdd from 
'./components/relations/accounts/finance_payment_batch_category_items/AccountFinancePaymentBatchCategoryItemAdd'
import AccountFinancePaymentBatchCategoryItemEdit from 
'./components/relations/accounts/finance_payment_batch_category_items/AccountFinancePaymentBatchCategoryItemEdit'
import AccountInvoices from './components/relations/accounts/invoices/AccountInvoices'
import AccountInvoiceAdd from './components/relations/accounts/invoices/AccountInvoiceAdd'
import AccountMemberships from './components/relations/accounts/memberships/AccountMemberships'
import AccountMembershipAdd from './components/relations/accounts/memberships/AccountMembershipAdd'
import AccountMembershipEdit from './components/relations/accounts/memberships/AccountMembershipEdit'
import AccountNotes from './components/relations/accounts/notes/AccountNotes.jsx'
import AccountNoteAdd from './components/relations/accounts/notes/AccountNoteAdd.jsx'
import AccountNoteEdit from './components/relations/accounts/notes/AccountNoteEdit.jsx'
import AccountOrders from './components/relations/accounts/orders/AccountOrders'
import AccountScheduleEventTickets from './components/relations/accounts/schedule_event_tickets/AccountScheduleEventTickets'
import AccountSubscriptions from './components/relations/accounts/subscriptions/AccountSubscriptions'
import AccountSubscriptionAdd from './components/relations/accounts/subscriptions/AccountSubscriptionAdd'
import AccountSubscriptionEdit from './components/relations/accounts/subscriptions/edit/AccountSubscriptionEdit'
import AccountSubscriptionEditAltPrices from './components/relations/accounts/subscriptions/edit/alt_prices/AccountSubscriptionEditAltPrices'
import AccountSubscriptionEditAltPriceAdd from './components/relations/accounts/subscriptions/edit/alt_prices/AccountSubscriptionEditAltPriceAdd'
import AccountSubscriptionEditAltPriceEdit from './components/relations/accounts/subscriptions/edit/alt_prices/AccountSubscriptionEditAltPriceEdit'
import AccountSubscriptionEditBlocks from './components/relations/accounts/subscriptions/edit/blocks/AccountSubscriptionEditBlocks'
import AccountSubscriptionEditBlockAdd from './components/relations/accounts/subscriptions/edit/blocks/AccountSubscriptionEditBlockAdd'
import AccountSubscriptionEditBlockEdit from './components/relations/accounts/subscriptions/edit/blocks/AccountSubscriptionEditBlockEdit'
import AccountSubscriptionEditCredits from './components/relations/accounts/subscriptions/edit/credits/AccountSubscriptionEditCredits'
import AccountSubscriptionEditCreditAdd from './components/relations/accounts/subscriptions/edit/credits/AccountSubscriptionEditCreditAdd'
import AccountSubscriptionEditCreditEdit from './components/relations/accounts/subscriptions/edit/credits/AccountSubscriptionEditCreditEdit'
import AccountSubscriptionEditInvoices from './components/relations/accounts/subscriptions/edit/invoices/AccountSubscriptionEditInvoices'
import AccountSubscriptionEditInvoiceAdd from './components/relations/accounts/subscriptions/edit/invoices/AccountSubscriptionEditInvoiceAdd'
import AccountSubscriptionEditPauses from './components/relations/accounts/subscriptions/edit/pauses/AccountSubscriptionEditPauses'
import AccountSubscriptionEditPauseAdd from './components/relations/accounts/subscriptions/edit/pauses/AccountSubscriptionEditPauseAdd'
import AccountSubscriptionEditPauseEdit from './components/relations/accounts/subscriptions/edit/pauses/AccountSubscriptionEditPauseEdit'
import RelationsAccountTeacherProfile from './components/relations/accounts/teacher_profile/RelationsAccountTeacherProfile'
import RelationsB2B from './components/relations/b2b/RelationsB2B'
import RelationsB2BAdd from './components/relations/b2b/RelationsB2BAdd.jsx'
import RelationsB2BEdit from './components/relations/b2b/RelationsB2BEdit.jsx'

import ScheduleHome from './components/schedule/home/ScheduleHome'
import ScheduleAppointments from './components/schedule/appointments/ScheduleAppointments'
import ScheduleAppointmentAdd from './components/schedule/appointments/ScheduleAppointmentAdd'
import ScheduleAppointmentEditAll from './components/schedule/appointments/all/edit/ScheduleAppointmentEditAll'
import ScheduleClasses from './components/schedule/classes/ScheduleClasses'
import ScheduleClassAdd from './components/schedule/classes/ScheduleClassAdd'
import ScheduleClassEditAll from './components/schedule/classes/all/edit/ScheduleClassEditAll'
import ScheduleClassClasspasses from './components/schedule/classes/all/classpasses/ScheduleClassClasspasses'
import ScheduleClassSubscriptions from './components/schedule/classes/all/subscriptions/ScheduleClassSubscriptions'
import ScheduleClassTeachers from './components/schedule/classes/all/teachers/ScheduleClassTeachers'
import ScheduleClassTeacherAdd from './components/schedule/classes/all/teachers/ScheduleClassTeacherAdd'
import ScheduleClassTeacherEdit from './components/schedule/classes/all/teachers/ScheduleClassTeacherEdit'
import ScheduleClassAttendance from './components/schedule/classes/class/attendance/ScheduleClassAttendance'
import ScheduleClassBook from './components/schedule/classes/class/book/ScheduleClassBook'
import ScheduleClassEdit from './components/schedule/classes/class/edit/ScheduleClassEdit'
import ScheduleClassPrices from './components/schedule/classes/all/prices/ScheduleClassPrices'
import ScheduleClassPriceAdd from './components/schedule/classes/all/prices/ScheduleClassPriceAdd'
import ScheduleClassPriceEdit from './components/schedule/classes/all/prices/ScheduleClassPriceEdit'
import ScheduleEvents from './components/schedule/events/ScheduleEvents'
import ScheduleEventAdd from './components/schedule/events/ScheduleEventAdd'
import ScheduleEventEdit from './components/schedule/events/edit/ScheduleEventEdit'
import ScheduleEventActivities from './components/schedule/events/activities/ScheduleEventActivities'
import ScheduleEventActivityAdd from './components/schedule/events/activities/ScheduleEventActivityAdd'
import ScheduleEventActivityEdit from './components/schedule/events/activities/ScheduleEventActivityEdit'
import ScheduleEventActivityAttendance from './components/schedule/events/activities/attendance/ScheduleEventActivityAttendance'
import ScheduleEventEarlybirds from './components/schedule/events/earlybirds/ScheduleEventEarlybirds'
import ScheduleEventEarlybirdAdd from './components/schedule/events/earlybirds/ScheduleEventEarlybirdAdd'
import ScheduleEventEarlybirdEdit from './components/schedule/events/earlybirds/ScheduleEventEarlybirdEdit'
import ScheduleEventMedia from './components/schedule/events/media/ScheduleEventMedia'
import ScheduleEventMediaAdd from './components/schedule/events/media/ScheduleEventMediaAdd'
import ScheduleEventMediaEdit from './components/schedule/events/media/ScheduleEventMediaEdit'
import ScheduleEventTickets from './components/schedule/events/tickets/ScheduleEventTickets'
import ScheduleEventTicketAdd from './components/schedule/events/tickets/ScheduleEventTicketAdd'
import ScheduleEventTicketEdit from './components/schedule/events/tickets/ScheduleEventTicketEdit'
import ScheduleEventTicketEditActivities from './components/schedule/events/tickets/activities/ScheduleEventTicketEditActivities'
import ScheduleEventTicketEditCustomers from './components/schedule/events/tickets/customers/ScheduleEventTicketEditCustomers'

import SelfCheckinCheckin from './components/selfcheckin/Checkin/Checkin'
import SelfCheckinBookingOptions from './components/selfcheckin/BookingOptions/BookingOptions'
import SelfCheckinLocations from './components/selfcheckin/Locations/Locations'
import SelfCheckinLocationClasses from './components/selfcheckin/LocationClasses/LocationClasses'

import SettingsAbout from './components/settings/about/SettingsAbout'
import SettingsFinanceBankAccounts from './components/settings/finance/bank_accounts/SettingsFinanceBankAccounts'
import SettingsFinanceCurrency from './components/settings/finance/currency/SettingsFinanceCurrency'
import SettingsGeneralDateTime from './components/settings/general/date_time/SettingsGeneralDateTime'
import SettingsGeneralSystem from './components/settings/general/system/SettingsGeneralSystem'
import SettingsHome from './components/settings/home/SettingsHome'
import SettingsIntegrationMollie from './components/settings/integration/mollie/SettingsIntegrationMollie'
import SettingsMailTemplates from './components/settings/mail/SettingsMailTemplates'
import SettingsMailTemplateEdit from './components/settings/mail/SettingsMailTemplateEdit'
import SettingsShopFeatures from './components/settings/shop/features/SettingsShopFeatures'
import SettingsWorkflowClassBooking from './components/settings/workflow/class_booking/SettingsWorkflowClassBooking'

import ShopAccountHome from './components/shop/account/home/ShopAccountHome'
import ShopAccountClassCancel from './components/shop/account/class_cancel/ShopAccountClassCancel'
import ShopAccountClassInfo from './components/shop/account/class_info/ShopAccountClassInfo'
import ShopAccountClasspasses from './components/shop/account/classpasses/ShopAccountClasspasses'
import ShopAccountEventTickets from './components/shop/account/event_tickets/ShopAccountEventTickets'
import ShopAccountInvoices from './components/shop/account/invoices/ShopAccountInvoices'
import ShopAccountOrders from './components/shop/account/orders/ShopAccountOrders'
import ShopAccountProfile from './components/shop/account/profile/ShopAccountProfile'
import ShopAccountSubscriptions from './components/shop/account/subscriptions/ShopAccountSubscriptions'
import ShopClassBook from './components/shop/classes/book/ShopClassBook'
import ShopClassBooked from './components/shop/classes/booked/ShopClassBooked'
import ShopClassesSchedule from './components/shop/classes/schedule/ShopClassesSchedule'
import ShopContact from './components/shop/contact/ShopContact'
import ShopEvents from './components/shop/events/ShopEvents'
import ShopEvent from './components/shop/event/ShopEvent'
import ShopEventTicket from './components/shop/event_ticket/ShopEventTicket'
import ShopHome from './components/shop/home/ShopHome'
import ShopCheckoutPayment from './components/shop/checkout/payment/ShopCheckoutPayment'
import ShopCheckoutComplete from './components/shop/checkout/complete/ShopCheckoutComplete'
import ShopClasses from './components/shop/account/classes/ShopAccountClasses'
import ShopClasspasses from './components/shop/classpasses/ShopClasspasses'
import ShopClasspass from './components/shop/classpass/ShopClasspass'
import ShopSubscriptions from './components/shop/subscriptions/ShopSubscriptions'
import ShopSubscription from './components/shop/subscription/ShopSubscription'

import UserChangePassword from './components/user/password/UserPasswordChange'
import UserLogin from './components/user/login/UserLogin'
import UserLoginRequired from './components/user/login/UserLoginRequired'
import UserLogout from './components/user/login/UserLogout'
import UserSessionExpired from './components/user/session/UserSessionExpired'
import UserWelcome from './components/user/welcome/UserWelcome'


import Error404 from "./components/Error404"

import CSLS from "./tools/cs_local_storage"
import { CSAuth } from './tools/authentication'


function SetCurrentUrlAsNext() {
  console.log("Storing current location as next in local storage")
  const currentUrl = window.location.href
  const next = currentUrl.split("#")[1]
  console.log(next)
  localStorage.setItem(CSLS.AUTH_LOGIN_NEXT, next)
}


const PrivateRoute = ({ component: Component, ...rest }) => {
  const [doTokenRefresh] = useMutation(TOKEN_REFRESH)
  let authTokenExpired = false
  console.log(rest.path)

  const ContinueAsYouAre = <Route {...rest} render={(props) => ( <Component {...props} /> )} />
  const LoginRequired = <Route {...rest} render={(props) => ( <Redirect to='/user/login/required' /> )} />
  const SessionExpired = <Route {...rest} render={(props) => ( <Redirect to='/user/session/expired' /> )} />
  
  // Check expiration
  const tokenExp = localStorage.getItem(CSLS.AUTH_TOKEN_EXP)
  if ((new Date() / 1000) >= tokenExp) {
    authTokenExpired = true
  }

  if (authTokenExpired) {
    const refreshTokenExp = localStorage.getItem(CSLS.AUTH_TOKEN_REFRESH_EXP)
    if (refreshTokenExp == null) {
      SetCurrentUrlAsNext()
      
      return LoginRequired
    } else if ((new Date() / 1000) >= refreshTokenExp) {
      console.log("refresh token expired or not found")
      console.log(new Date() / 1000)
      console.log(refreshTokenExp)
      SetCurrentUrlAsNext()

      return SessionExpired
    } else {
      // Refresh token
      console.log("auth token expired")
      console.log(new Date() / 1000)
      console.log(refreshTokenExp)

      doTokenRefresh().then(({ data }) => {
        console.log('got refresh data', data)
        CSAuth.updateTokenInfo(data.refreshToken)
        return ContinueAsYouAre
      }).catch((error) => {
        toast.error('general.toast_server_error' + ': ' +  error, {
          position: toast.POSITION.BOTTOM_RIGHT
        })
        console.log('there was an error refreshing the token', error) 
        SetCurrentUrlAsNext()
        console.log("REDIRECT BACK TO LOGIN")
        window.location.href = "/#/user/login"
        window.location.reload()
      })
    }
  } else {
    return ContinueAsYouAre
  }
  return null
}


function AppRoot({ t }) {
  const { loading: loadingAppSettings, error: errorAppSettings, data: dataAppSettings } = useQuery(GET_APP_SETTINGS_QUERY)
  const { loading: loadingOrganization, error: errorOrganization, data: dataOrganization } = useQuery(GET_ORGANIZATION_QUERY, {
    variables: {id: "T3JnYW5pemF0aW9uTm9kZToxMDA="}
  })

  if (loadingAppSettings || loadingOrganization) return t('general.loading_with_dots')
  if (errorAppSettings || errorOrganization) return (
    <div>
      { t('settings.error_loading') } <br />
      { errorAppSettings.message } <br /><br />
      { errorOrganization.message}
    </div>
  )

  // Register "US" locale for moment
  // moment.locale('en-US')
  let appSettings = dataAppSettings.appSettings
  console.log(appSettings)
  let organization = dataOrganization.organization
  console.log(organization)

  return (
    <AppSettingsProvider value={appSettings}>
      <OrganizationProvider value={organization}>
        <HashRouter>
          <Switch>
            {/* BACKEND HOME */}
            <PrivateRoute exact path="/backend" component={HomeHome} />

            {/* AUTOMATION */}
            <PrivateRoute exact path="/automation" component={AutomationHome} />
            <PrivateRoute exact path="/automation/account/subscriptions/credits" 
                                component={AutomationAccountSubscriptionCredits} />
            <PrivateRoute exact path="/automation/account/subscriptions/credits/add" 
                                component={AutomationAccountSubscriptionCreditAdd} />
            <PrivateRoute exact path="/automation/account/subscriptions/invoices" 
                                component={AutomationAccountSubscriptionInvoices} />    
            <PrivateRoute exact path="/automation/account/subscriptions/invoices/add" 
                                component={AutomationAccountSubscriptionInvoicesAdd} />    
            <PrivateRoute exact path="/automation/account/subscriptions/mollie_collections" 
                                component={AutomationAccountSubscriptionMollieCollections} />
            <PrivateRoute exact path="/automation/account/subscriptions/mollie_collections/add" 
                                component={AutomationAccountSubscriptionMollieCollectionAdd} />

            
            {/* FINANCE */}
            <PrivateRoute exact path="/finance" component={FinanceHome} />
            <PrivateRoute exact path="/finance/costcenters" component={FinanceCostCenters} />
            <PrivateRoute exact path="/finance/costcenters/add" component={FinanceCostCenterAdd} />
            <PrivateRoute exact path="/finance/costcenters/edit/:id" component={FinanceCostCenterEdit} />
            <PrivateRoute exact path="/finance/invoices" component={FinanceInvoices} />
            <PrivateRoute exact path="/finance/invoices/edit/:id" component={FinanceInvoiceEdit} />
            <PrivateRoute exact path="/finance/invoices/groups" component={FinanceInvoiceGroups} />
            <PrivateRoute exact path="/finance/invoices/groups/add" component={FinanceInvoiceGroupAdd} />
            <PrivateRoute exact path="/finance/invoices/groups/edit/:id" component={FinanceInvoiceGroupEdit} />
            <PrivateRoute exact path="/finance/invoices/groups/defaults" component={FinanceInvoiceGroupDefaults} />
            <PrivateRoute exact path="/finance/invoices/:invoice_id/payment/add" component={FinanceInvoicePaymentAdd} />
            <PrivateRoute exact path="/finance/invoices/:invoice_id/payment/edit/:id" component={FinanceInvoicePaymentEdit} />
            <PrivateRoute exact path="/finance/glaccounts" component={FinanceGLAccounts} />
            <PrivateRoute exact path="/finance/glaccounts/add" component={FinanceGLAccountAdd} />
            <PrivateRoute exact path="/finance/glaccounts/edit/:id" component={FinanceGLAccountEdit} />
            <PrivateRoute exact path="/finance/orders" component={FinanceOrders} />
            <PrivateRoute exact path="/finance/orders/edit/:id" component={FinanceOrderEdit} />
            <PrivateRoute exact path="/finance/paymentbatches/:batch_type" component={FinancePaymentBatches} />
            <PrivateRoute exact path="/finance/paymentbatches/:batch_type/add_what" component={FinancePaymentBatchAddWhat} />
            <PrivateRoute exact path="/finance/paymentbatches/:batch_type/view/:id" component={FinancePaymentBatchView} />
            <PrivateRoute exact path="/finance/paymentbatches/:batch_type/add/:category_type" component={FinancePaymentCollectionBatchAdd} />
            <PrivateRoute exact path="/finance/paymentbatches/:batch_type/edit/:id" component={FinancePaymentCollectionBatchEdit} />
            <PrivateRoute exact path="/finance/paymentbatchcategories" component={FinancePaymentBatchCategories} />
            <PrivateRoute exact path="/finance/paymentbatchcategories/add" component={FinancePaymentBatchCategoryAdd} />
            <PrivateRoute exact path="/finance/paymentbatchcategories/edit/:id" component={FinancePaymentBatchCategoryEdit} />
            <PrivateRoute exact path="/finance/paymentmethods" component={FinancePaymentMethods} />
            <PrivateRoute exact path="/finance/paymentmethods/add" component={FinancePaymentMethodAdd} />
            <PrivateRoute exact path="/finance/paymentmethods/edit/:id" component={FinancePaymentMethodEdit} />
            <PrivateRoute exact path="/finance/taxrates" component={FinanceTaxRates} />
            <PrivateRoute exact path="/finance/taxrates/add" component={FinanceTaxRatesAdd} />
            <PrivateRoute exact path="/finance/taxrates/edit/:id" component={FinanceTaxRatesEdit} />
            
            {/* ORGANIZATION */}
            <PrivateRoute exact path="/organization" component={OrganizationHome} />
            <PrivateRoute exact path="/organization/edit/:id" component={OrganizationEdit} />
            <PrivateRoute exact path="/organization/edit/:id/branding" component={OrganizationBranding} />
            <PrivateRoute exact path="/organization/edit/:id/branding/:update_field" component={OrganizationBrandingEdit} />
            <PrivateRoute exact path="/organization/documents/:organization_id" component={OrganizationDocuments} />
            <PrivateRoute exact path="/organization/documents/:organization_id/:document_type" component={OrganizationListDocuments} />
            <PrivateRoute exact path="/organization/documents/:organization_id/:document_type/add" component={OrganizationDocumentAdd} />
            <PrivateRoute exact path="/organization/documents/:organization_id/:document_type/edit/:id" component={OrganizationDocumentEdit} />
            <PrivateRoute exact path="/organization/announcements" component={OrganizationAnnouncements} />
            <PrivateRoute exact path="/organization/announcements/add" component={OrganizationAnnouncementAdd} />
            <PrivateRoute exact path="/organization/announcements/edit/:id" component={OrganizationAnnouncementEdit} />
            <PrivateRoute exact path="/organization/appointment_categories" component={OrganizationAppointmentCategories} />
            <PrivateRoute exact path="/organization/appointment_categories/add" component={OrganizationAppointmentCategoryAdd} />
            <PrivateRoute exact path="/organization/appointment_categories/edit/:id" component={OrganizationAppointmentCategoryEdit} />
            <PrivateRoute exact path="/organization/appointment_categories/:category_id/appointments" component={OrganizationAppointments} />
            <PrivateRoute exact path="/organization/appointment_categories/:category_id/appointments/add/" component={OrganizationAppointmentAdd} />
            <PrivateRoute exact path="/organization/appointment_categories/:category_id/appointments/edit/:id" component={OrganizationAppointmentEdit} />
            <PrivateRoute exact path="/organization/appointment_categories/:category_id/appointments/prices/:appointment_id" 
                  component={OrganizationAppointmentPrices} />
            <PrivateRoute exact path="/organization/appointment_categories/:category_id/appointments/prices/:appointment_id/add" 
                  component={OrganizationAppointmentPriceAdd} />
            <PrivateRoute exact path="/organization/appointment_categories/:category_id/appointments/prices/:appointment_id/edit/:id" 
                  component={OrganizationAppointmentPriceEdit} />
            <PrivateRoute exact path="/organization/classpasses" component={OrganizationClasspasses} />
            <PrivateRoute exact path="/organization/classpasses/add" component={OrganizationClasspassAdd} />
            <PrivateRoute exact path="/organization/classpasses/edit/:id" component={OrganizationClasspassEdit} />    
            <PrivateRoute exact path="/organization/classpasses/groups" component={OrganizationClasspassesGroups} />
            <PrivateRoute exact path="/organization/classpasses/groups/add" component={OrganizationClasspassesGroupAdd} />
            <PrivateRoute exact path="/organization/classpasses/groups/edit/:id" component={OrganizationClasspassesGroupEdit} />
            <PrivateRoute exact path="/organization/classpasses/groups/edit/passes/:id" component={OrganizationClasspassesGroupEditPasses} />
            <PrivateRoute exact path="/organization/classtypes" component={OrganizationClasstypes} />
            <PrivateRoute exact path="/organization/classtypes/add" component={OrganizationClasstypeAdd} />
            <PrivateRoute exact path="/organization/classtypes/edit/:id" component={OrganizationClasstypeEdit} />
            <PrivateRoute exact path="/organization/classtypes/edit_image/:id" component={OrganizationClasstypeEditImage} />
            <PrivateRoute exact path="/organization/discoveries" component={OrganizationDiscoveries} />
            <PrivateRoute exact path="/organization/discoveries/add" component={OrganizationDiscoveryAdd} /> 
            <PrivateRoute exact path="/organization/discoveries/edit/:id" component={OrganizationDiscoveryEdit} /> 
            <PrivateRoute exact path="/organization/levels" component={OrganizationLevels} />
            <PrivateRoute exact path="/organization/levels/add" component={OrganizationLevelAdd} />
            <PrivateRoute exact path="/organization/levels/edit/:id" component={OrganizationLevelEdit} />
            <PrivateRoute exact path="/organization/locations" component={OrganizationLocations} />
            <PrivateRoute exact path="/organization/locations/add" component={OrganizationLocationAdd} />
            <PrivateRoute exact path="/organization/locations/edit/:id" component={OrganizationLocationEdit} />
            <PrivateRoute exact path="/organization/locations/rooms/:location_id" component={OrganizationLocationRooms} />
            <PrivateRoute exact path="/organization/locations/rooms/add/:location_id" component={OrganizationLocationRoomAdd} />
            <PrivateRoute exact path="/organization/locations/rooms/edit/:location_id/:id" component={OrganizationLocationRoomEdit} />
            <PrivateRoute exact path="/organization/memberships" component={OrganizationMemberships} />
            <PrivateRoute exact path="/organization/memberships/add" component={OrganizationMembershipAdd} />
            <PrivateRoute exact path="/organization/memberships/edit/:id" component={OrganizationMembershipEdit} /> 
            <PrivateRoute exact path="/organization/subscriptions" component={OrganizationSubscriptions} />
            <PrivateRoute exact path="/organization/subscriptions/add" component={OrganizationSubscriptionAdd} />
            <PrivateRoute exact path="/organization/subscriptions/edit/:id" component={OrganizationSubscriptionEdit} />
            <PrivateRoute exact path="/organization/subscriptions/groups" component={OrganizationSubscriptionsGroups} />
            <PrivateRoute exact path="/organization/subscriptions/groups/add" component={OrganizationSubscriptionsGroupAdd} />
            <PrivateRoute exact path="/organization/subscriptions/groups/edit/:id" component={OrganizationSubscriptionsGroupEdit} />
            <PrivateRoute exact path="/organization/subscriptions/groups/edit/subscriptions/:id" component={OrganizationSubscriptionsGroupEditSubscriptions} />
            <PrivateRoute exact path="/organization/subscriptions/prices/:subscription_id" component={OrganizationSubscriptionsPrices} />
            <PrivateRoute exact path="/organization/subscriptions/prices/add/:subscription_id" component={OrganizationSubscriptionPriceAdd} />
            <PrivateRoute exact path="/organization/subscriptions/prices/edit/:subscription_id/:id" component={OrganizationSubscriptionPriceEdit} />

            {/* RELATIONS */}
            <PrivateRoute exact path="/relations" component={RelationsHome} />
            <PrivateRoute exact path="/relations/accounts" component={RelationsAccounts} />
            <PrivateRoute exact path="/relations/accounts/add" component={RelationsAccountAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/profile" component={RelationsAccountProfile} />
            <PrivateRoute exact path="/relations/accounts/:account_id/accepted_documents" component={AccountAcceptedDocuments} />
            <PrivateRoute exact path="/relations/accounts/:account_id/bank_accounts" component={RelationsAccountBankAccount} />
            <PrivateRoute exact path="/relations/accounts/:account_id/bank_accounts/:bank_account_id/mandates/add" 
                          component={RelationsAccountBankAccountMandateAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/bank_accounts/:bank_account_id/mandates/edit/:id" 
                          component={RelationsAccountBankAccountMandateEdit} />
            <PrivateRoute exact path="/relations/accounts/:account_id/classes" component={RelationsAccountClasses} />
            <PrivateRoute exact path="/relations/accounts/:account_id/classpasses" component={AccountClasspasses} />
            <PrivateRoute exact path="/relations/accounts/:account_id/classpasses/add" component={AccountClasspassAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/classpasses/edit/:id" component={AccountClasspassEdit} />
            <PrivateRoute exact path="/relations/accounts/:account_id/finance_payment_batch_category_items" 
                          component={AccountFinancePaymentBatchCategoryItems} />
            <PrivateRoute exact path="/relations/accounts/:account_id/finance_payment_batch_category_items/add" 
                          component={AccountFinancePaymentBatchCategoryItemAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/finance_payment_batch_category_items/edit/:id" 
                          component={AccountFinancePaymentBatchCategoryItemEdit} />
            <PrivateRoute exact path="/relations/accounts/:account_id/invoices" component={AccountInvoices} />
            <PrivateRoute exact path="/relations/accounts/:account_id/invoices/add" component={AccountInvoiceAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/memberships" component={AccountMemberships} />
            <PrivateRoute exact path="/relations/accounts/:account_id/memberships/add" component={AccountMembershipAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/memberships/edit/:id" component={AccountMembershipEdit} />
            <PrivateRoute exact path="/relations/accounts/:account_id/notes" component={AccountNotes} />
            <PrivateRoute exact path="/relations/accounts/:account_id/notes/add" component={AccountNoteAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/notes/edit/:id" component={AccountNoteEdit} />
            <PrivateRoute exact path="/relations/accounts/:account_id/orders" component={AccountOrders} />
            <PrivateRoute exact path="/relations/accounts/:account_id/event_tickets" component={AccountScheduleEventTickets} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions" component={AccountSubscriptions} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/add" component={AccountSubscriptionAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id" 
                          component={AccountSubscriptionEdit} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/alt_prices" 
                          component={AccountSubscriptionEditAltPrices} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/alt_prices/add" 
                          component={AccountSubscriptionEditAltPriceAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/alt_prices/edit/:id" 
                          component={AccountSubscriptionEditAltPriceEdit} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/blocks" component={AccountSubscriptionEditBlocks} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/blocks/add" component={AccountSubscriptionEditBlockAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/blocks/edit/:id" 
                          component={AccountSubscriptionEditBlockEdit} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/credits" component={AccountSubscriptionEditCredits} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/credits/add" component={AccountSubscriptionEditCreditAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/credits/edit/:id" 
                          component={AccountSubscriptionEditCreditEdit} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/invoices" 
              component={AccountSubscriptionEditInvoices} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/invoices/add" 
              component={AccountSubscriptionEditInvoiceAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/pauses" component={AccountSubscriptionEditPauses} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/pauses/add" component={AccountSubscriptionEditPauseAdd} />
            <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:subscription_id/pauses/edit/:id" 
                          component={AccountSubscriptionEditPauseEdit} />
            <PrivateRoute exact path="/relations/accounts/:account_id/teacher_profile" component={RelationsAccountTeacherProfile} />
            <PrivateRoute exact path="/relations/b2b" component={RelationsB2B} />
            <PrivateRoute exact path="/relations/b2b/add" component={RelationsB2BAdd} />
            <PrivateRoute exact path="/relations/b2b/:business_id/edit" component={RelationsB2BEdit} />

            {/* SCHEDULE */}
            <PrivateRoute exact path="/schedule" component={ScheduleHome} />
            <PrivateRoute exact path="/schedule/appointments" component={ScheduleAppointments} />
            <PrivateRoute exact path="/schedule/appointments/add" component={ScheduleAppointmentAdd} />
            <PrivateRoute exact path="/schedule/appointments/all/edit/:appointment_id" component={ScheduleAppointmentEditAll} />
            <PrivateRoute exact path="/schedule/classes" component={ScheduleClasses} />
            <PrivateRoute exact path="/schedule/classes/add/" component={ScheduleClassAdd} />
            <PrivateRoute exact path="/schedule/classes/all/edit/:class_id/" component={ScheduleClassEditAll} />
            <PrivateRoute exact path="/schedule/classes/all/classpasses/:class_id/" component={ScheduleClassClasspasses} />
            <PrivateRoute exact path="/schedule/classes/all/prices/:class_id/" component={ScheduleClassPrices} />
            <PrivateRoute exact path="/schedule/classes/all/prices/:class_id/add" component={ScheduleClassPriceAdd} />
            <PrivateRoute exact path="/schedule/classes/all/prices/:class_id/edit/:id" component={ScheduleClassPriceEdit} />
            <PrivateRoute exact path="/schedule/classes/all/subscriptions/:class_id/" component={ScheduleClassSubscriptions} />
            <PrivateRoute exact path="/schedule/classes/all/teachers/:class_id/" component={ScheduleClassTeachers} />
            <PrivateRoute exact path="/schedule/classes/all/teachers/:class_id/add" component={ScheduleClassTeacherAdd} />
            <PrivateRoute exact path="/schedule/classes/all/teachers/:class_id/edit/:id" component={ScheduleClassTeacherEdit} />
            <PrivateRoute exact path="/schedule/classes/class/attendance/:class_id/:date" component={ScheduleClassAttendance} />
            <PrivateRoute exact path="/schedule/classes/class/book/:class_id/:date/:account_id" component={ScheduleClassBook} />
            <PrivateRoute exact path="/schedule/classes/class/edit/:class_id/:date" component={ScheduleClassEdit} />
            <PrivateRoute exact path="/schedule/events" component={ScheduleEvents} />
            <PrivateRoute exact path="/schedule/events/add" component={ScheduleEventAdd} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id" component={ScheduleEventEdit} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/activities" component={ScheduleEventActivities} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/activities/add" component={ScheduleEventActivityAdd} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/activities/edit/:id" component={ScheduleEventActivityEdit} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/activities/edit/:id/attendance" 
                          component={ScheduleEventActivityAttendance} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/earlybirds" component={ScheduleEventEarlybirds} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/earlybirds/add" component={ScheduleEventEarlybirdAdd} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/earlybirds/edit/:id" component={ScheduleEventEarlybirdEdit} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/media" component={ScheduleEventMedia} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/media/add" component={ScheduleEventMediaAdd} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/media/edit/:id" component={ScheduleEventMediaEdit} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/tickets" component={ScheduleEventTickets} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/tickets/add" component={ScheduleEventTicketAdd} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/tickets/edit/:id" component={ScheduleEventTicketEdit} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/tickets/edit/:id/activities" component={ScheduleEventTicketEditActivities} />
            <PrivateRoute exact path="/schedule/events/edit/:event_id/tickets/edit/:id/customers" component={ScheduleEventTicketEditCustomers} />

            {/* Insight */}
            <PrivateRoute exact path="/insight" component={InsightHome} />
            <PrivateRoute exact path="/insight/classpasses" component={InsightClasspasses} />
            <PrivateRoute exact path="/insight/subscriptions" component={InsightSubscriptions} />

            {/* Self Check-in */}
            <PrivateRoute exact path="/selfcheckin/checkin/:location_id/:class_id/:date" component={SelfCheckinCheckin} />
            <PrivateRoute exact path="/selfcheckin/book/:location_id/:class_id/:date/:account_id" 
                                component={SelfCheckinBookingOptions} />
            <PrivateRoute exact path="/selfcheckin" component={SelfCheckinLocations} />
            <PrivateRoute exact path="/selfcheckin/location/:location_id" component={SelfCheckinLocationClasses} />

            {/* Shop */}
            <Route exact path = "/" component={ShopHome} />
            <PrivateRoute exact path = "/shop/account" component={ShopAccountHome} />
            <PrivateRoute exact path = "/shop/account/class_cancel/:class_id/:date/:attendance_id" 
                                component={ShopAccountClassCancel} />
            <PrivateRoute exact path = "/shop/account/class_info/:class_id/:date" component={ShopAccountClassInfo} />
            <PrivateRoute exact path = "/shop/account/classes" component={ShopClasses} />
            <PrivateRoute exact path = "/shop/account/classpasses" component={ShopAccountClasspasses} />
            <PrivateRoute exact path = "/shop/account/event_tickets" component={ShopAccountEventTickets} />
            <PrivateRoute exact path = "/shop/account/invoices" component={ShopAccountInvoices} />
            <PrivateRoute exact path = "/shop/account/orders" component={ShopAccountOrders} />
            <PrivateRoute exact path = "/shop/account/profile" component={ShopAccountProfile} />
            <PrivateRoute exact path = "/shop/account/subscriptions" component={ShopAccountSubscriptions} />
            <PrivateRoute exact path = "/shop/checkout/payment/:id" component={ShopCheckoutPayment} />
            <PrivateRoute exact path = "/shop/checkout/complete/:id" component={ShopCheckoutComplete} />
            <Route exact path = "/shop/classes" component={ShopClassesSchedule} />
            <PrivateRoute exact path = "/shop/classes/book/:class_id/:date" component={ShopClassBook} />
            <PrivateRoute exact path = "/shop/classes/booked/:class_id/:date" component={ShopClassBooked} />
            <Route exact path = "/shop/classpasses" component={ShopClasspasses} />
            <Route exact path = "/shop/classpass/:id" component={ShopClasspass} />
            <Route exact path = "/shop/classpass/:id/:class_id/:date" component={ShopClasspass} />
            <Route exact path = "/shop/contact" component={ShopContact} />
            <Route exact path = "/shop/events" component={ShopEvents} />
            <Route exact path = "/shop/events/:event_id" component={ShopEvent} />
            <Route exact path = "/shop/events/:event_id/ticket/:id" component={ShopEventTicket} />
            <Route exact path = "/shop/subscriptions" component={ShopSubscriptions} />
            <Route exact path = "/shop/subscription/:id" component={ShopSubscription} />

            {/* Settings */}
            <PrivateRoute exact path="/settings" component={SettingsHome} />
            <PrivateRoute exact path="/settings/about" component={SettingsAbout} />
            <PrivateRoute exact path="/settings/finance/bank_accounts" component={SettingsFinanceBankAccounts} />
            <PrivateRoute exact path="/settings/finance/currency" component={SettingsFinanceCurrency} />
            <PrivateRoute exact path="/settings/general/datetime" component={SettingsGeneralDateTime} />
            <PrivateRoute exact path="/settings/general/system" component={SettingsGeneralSystem} />
            <PrivateRoute exact path="/settings/integration/mollie" component={SettingsIntegrationMollie} />
            <PrivateRoute exact path="/settings/mail/templates" component={SettingsMailTemplates} />
            <PrivateRoute exact path="/settings/mail/templates/edit/:id" component={SettingsMailTemplateEdit} />
            <PrivateRoute exact path="/settings/shop/features" component={SettingsShopFeatures} />
            <PrivateRoute exact path="/settings/workflow/class_booking" component={SettingsWorkflowClassBooking} />

            {/* User */}
            <PrivateRoute exact path="/user/password/change" component={UserChangePassword} />
            <Route exact path="/user/login" component={UserLogin} />
            <Route exact path="/user/login/required" component={UserLoginRequired} />
            <Route exact path="/user/logout" component={UserLogout} />
            <Route exact path="/user/session/expired" component={UserSessionExpired} />
            <Route exact path="/user/welcome" component={UserWelcome} />
            
            <Route component={Error404} />
          </Switch>
        </HashRouter>
      </OrganizationProvider>
    </AppSettingsProvider>
  )
}

export default withTranslation()(AppRoot)

