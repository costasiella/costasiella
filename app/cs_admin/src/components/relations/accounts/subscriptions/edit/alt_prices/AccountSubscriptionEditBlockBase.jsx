// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import AccountSubscriptionEditBase from "../AccountSubscriptionEditBase"


function AccountSubscriptionEditAltPriceBase({ t, history, match, children}) {
  const activeTab = "alt_prices"
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/alt_prices/`

  return (
    <AccountSubscriptionEditBase active_tab={activeTab}>
      {children}
    </AccountSubscriptionEditBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditAltPriceBase))