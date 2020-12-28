// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import ShopBase from "../ShopBase"

function ShopEventsBase({ t, match, history, children }) {
  
  return (
    <ShopBase 
      title={t("shop.title")}
      return_url="/shop/events"
      checkoutProgress="order"
    >
      {children}
    </ShopBase>
  )
}


export default withTranslation()(withRouter(ShopEventsBase))