// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

import CardTabs from "../../../../ui/CardTabs"

function AccountSubscriptionEditTabs({ t, active, account_id, subscription_id}) {

  return (
    <CardTabs 
      position="top"
      tabs={[
          {
            name: "general", 
            title: t("relations.account.subscriptions.menu.general"), 
            link: `/relations/accounts/${account_id}/subscriptions/edit/${subscription_id}`
          },
          {
            name: "pauses", 
            title: t("relations.account.subscriptions.menu.pauses"), 
            link: `/relations/accounts/${account_id}/subscriptions/edit/${subscription_id}/pauses`
          },
          {
            name: "blocks", 
            title: t("relations.account.subscriptions.menu.blocks"), 
            link: `/relations/accounts/${account_id}/subscriptions/edit/${subscription_id}/blocks`
          },
          {
            name: "alt_prices", 
            title: t("relations.account.subscriptions.menu.alt_prices"), 
            link: `/relations/accounts/${account_id}/subscriptions/edit/${subscription_id}/alt_prices`
          },
          {
            name: "invoices", 
            title: t("relations.account.subscriptions.menu.invoices"), 
            link: `/relations/accounts/${account_id}/subscriptions/edit/${subscription_id}/invoices`
          },
          {
            name: "credits", 
            title: t("relations.account.subscriptions.menu.credits"), 
            link: `/relations/accounts/${account_id}/subscriptions/edit/${subscription_id}/credits`
          },
      ]}
      active={active}
    />
  )
}

export default withTranslation()(AccountSubscriptionEditTabs)



