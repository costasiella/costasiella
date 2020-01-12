// import React, { Component } from 'react';
// import logo from './logo.svg';

import React from 'react'
import {
  Route, 
  Switch, 
  HashRouter,
  Redirect
} from 'react-router-dom'
import { withTranslation } from 'react-i18next'
import { useQuery } from "react-apollo"
import { toast } from 'react-toastify'

import { GET_APP_SETTINGS_QUERY } from "./components/app_settings/queries"

// Import moment locale
import moment from 'moment'
import 'moment/locale/nl'

import { AppSettingsProvider } from "./components/context/AppSettingsContext"

import AppSettingsGeneral from './components/app_settings/general/AppSettingsGeneral'

import HomeHome from './components/home/home/HomeHome'

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
import FinancePaymentMethods from './components/finance/payment_methods/FinancePaymentMethods'
import FinancePaymentMethodAdd from './components/finance/payment_methods/FinancePaymentMethodAdd'
import FinancePaymentMethodEdit from './components/finance/payment_methods/FinancePaymentMethodEdit'
import FinanceTaxRates from './components/finance/taxrates/FinanceTaxRates'
import FinanceTaxRatesAdd from './components/finance/taxrates/FinanceTaxRateAdd'
import FinanceTaxRatesEdit from './components/finance/taxrates/FinanceTaxRateEdit'

import OrganizationHome from './components/organization/home/OrganizationHome'
import OrganizationEdit from './components/organization/organization/OrganizationEdit'
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
import AccountClasspasses from './components/relations/accounts/classpasses/AccountClasspasses'
import AccountClasspassAdd from './components/relations/accounts/classpasses/AccountClasspassAdd'
import AccountClasspassEdit from './components/relations/accounts/classpasses/AccountClasspassEdit'
import AccountInvoices from './components/relations/accounts/invoices/AccountInvoices'
import AccountInvoiceAdd from './components/relations/accounts/invoices/AccountInvoiceAdd'
import AccountMemberships from './components/relations/accounts/memberships/AccountMemberships'
import AccountMembershipAdd from './components/relations/accounts/memberships/AccountMembershipAdd'
import AccountMembershipEdit from './components/relations/accounts/memberships/AccountMembershipEdit'
import AccountSubscriptions from './components/relations/accounts/subscriptions/AccountSubscriptions'
import AccountSubscriptionAdd from './components/relations/accounts/subscriptions/AccountSubscriptionAdd'
import AccountSubscriptionEdit from './components/relations/accounts/subscriptions/AccountSubscriptionEdit'
import RelationsAccountTeacherProfile from './components/relations/accounts/teacher_profile/RelationsAccountTeacherProfile'

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

import SelfCheckinLocations from './components/selfcheckin/Locations'

import UserChangePassword from './components/user/password/UserPasswordChange'
import UserLogin from './components/user/login/UserLogin'
import UserLogout from './components/user/login/UserLogout'
import UserSessionExpired from './components/user/session/UserSessionExpired'

import Error404 from "./components/Error404"

import CSLS from "./tools/cs_local_storage"
import { CSAuth } from './tools/authentication'


const PrivateRoute = ({ component: Component, ...rest }) => {
  let tokenExpired = false
  console.log(rest.path)
  
  // Check expiration
  const tokenExp = localStorage.getItem(CSLS.AUTH_TOKEN_EXP)
  if ((new Date() / 1000) >= tokenExp) {
    CSAuth.logout(true)
    tokenExpired = true
  }

  return (
    <Route {...rest} render={(props) => (
      tokenExpired 
        ? <Redirect to='/user/session/expired' />
        : <Component {...props} />
    )} />
  )
}


function AppRoot({ t }) {
  const { loading, error, data } = useQuery(GET_APP_SETTINGS_QUERY)

  if (loading) return t('general.loading_with_dots')
  if (error) return (
    <div>
      { t('settings.error_loading') } <br />
      { error.message }
    </div>
  )

  // Register "US" locale for moment
  // moment.locale('en-US')
  let appSettings = data.appSettings
  console.log(appSettings)
  if (appSettings.timeFormat == 24) {
    appSettings.timeFormatMoment = "HH:mm"
  } else {
    appSettings.timeFormatMoment = "hh:mm a"
  }

  return (
    <AppSettingsProvider value={appSettings}>
      <HashRouter>
        <Switch>
          <PrivateRoute exact path="/" component={HomeHome} />
          
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
          <PrivateRoute exact path="/finance/paymentmethods" component={FinancePaymentMethods} />
          <PrivateRoute exact path="/finance/paymentmethods/add" component={FinancePaymentMethodAdd} />
          <PrivateRoute exact path="/finance/paymentmethods/edit/:id" component={FinancePaymentMethodEdit} />
          <PrivateRoute exact path="/finance/taxrates" component={FinanceTaxRates} />
          <PrivateRoute exact path="/finance/taxrates/add" component={FinanceTaxRatesAdd} />
          <PrivateRoute exact path="/finance/taxrates/edit/:id" component={FinanceTaxRatesEdit} />
          
          {/* ORGANIZATION */}
          <PrivateRoute exact path="/organization" component={OrganizationHome} />
          <PrivateRoute exact path="/organization/edit/:id" component={OrganizationEdit} />
          <PrivateRoute exact path="/organization/documents/:organization_id" component={OrganizationDocuments} />
          <PrivateRoute exact path="/organization/documents/:organization_id/:document_type" component={OrganizationListDocuments} />
          <PrivateRoute exact path="/organization/documents/:organization_id/:document_type/add" component={OrganizationDocumentAdd} />
          <PrivateRoute exact path="/organization/documents/:organization_id/:document_type/edit/:id" component={OrganizationDocumentEdit} />
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
          <PrivateRoute exact path="/relations/accounts/:account_id/classpasses" component={AccountClasspasses} />
          <PrivateRoute exact path="/relations/accounts/:account_id/classpasses/add" component={AccountClasspassAdd} />
          <PrivateRoute exact path="/relations/accounts/:account_id/classpasses/edit/:id" component={AccountClasspassEdit} />
          <PrivateRoute exact path="/relations/accounts/:account_id/invoices" component={AccountInvoices} />
          <PrivateRoute exact path="/relations/accounts/:account_id/invoices/add" component={AccountInvoiceAdd} />
          <PrivateRoute exact path="/relations/accounts/:account_id/memberships" component={AccountMemberships} />
          <PrivateRoute exact path="/relations/accounts/:account_id/memberships/add" component={AccountMembershipAdd} />
          <PrivateRoute exact path="/relations/accounts/:account_id/memberships/edit/:id" component={AccountMembershipEdit} />
          <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions" component={AccountSubscriptions} />
          <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/add" component={AccountSubscriptionAdd} />
          <PrivateRoute exact path="/relations/accounts/:account_id/subscriptions/edit/:id" component={AccountSubscriptionEdit} />
          <PrivateRoute exact path="/relations/accounts/:account_id/teacher_profile" component={RelationsAccountTeacherProfile} />

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

          {/* Self Check-in */}
          <PrivateRoute exact path="/selfcheckin" component={SelfCheckinLocations} />

          {/* Settings */}
          <PrivateRoute exact path="/settings/general" component={AppSettingsGeneral} />

          {/* User */}
          <PrivateRoute exact path="/user/password/change" component={UserChangePassword} />
          <Route exact path="/user/login" component={UserLogin} />
          <Route exact path="/user/logout" component={UserLogout} />
          <Route exact path="/user/session/expired" component={UserSessionExpired} />

          <Route component={Error404} />
        </Switch>
      </HashRouter>
    </AppSettingsProvider>
  )
}

export default withTranslation()(AppRoot)

