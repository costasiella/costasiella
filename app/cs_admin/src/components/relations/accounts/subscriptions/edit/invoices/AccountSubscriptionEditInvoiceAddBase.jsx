// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import AccountSubscriptionEditBase from "../AccountSubscriptionEditBase"


function AccountSubscriptionEditInvoiceAddBase({ t, history, match, children}) {
  const activeTab = "invoices"
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/invoices/`

  return (
    <AccountSubscriptionEditBase active_tab={activeTab}>
      {children}
    </AccountSubscriptionEditBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditInvoiceAddBase))