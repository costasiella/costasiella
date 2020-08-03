// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

import CardTabs from "../../../ui/CardTabs"

function AccountSubscriptionEditTabs({ t, active, account_id, subscription_id}) {

  return (
    <CardTabs 
      position="top"
      tabs={[
          {
            name: "general", 
            title: "General", 
            link: `/relations/accounts/${account_id}/subscriptions/edit/${subscription_id}`
          },
          {
            name: "credits", 
            title: "Credits", 
            link: `/relations/accounts/${account_id}/subscriptions/edit/${subscription_id}/credits`
          },
      ]}
      active={active}
    />
  )
}

export default withTranslation()(AccountSubscriptionEditTabs)



