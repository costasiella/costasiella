// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import ShopBase from "../ShopBase"

function ShopEventTicketBase({ t, match, history, children }) {
  const eventId = match.params.event_id
  
  return (
    <ShopBase 
      title={t("shop.title")}
      return_url={`/shop/events/${eventId}`}
      checkoutProgress="order"
    >
      {children}
    </ShopBase>
  )
}

export default withTranslation()(withRouter(ShopEventTicketBase))