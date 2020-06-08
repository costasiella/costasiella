// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import ShopBase from "../../ShopBase"

function ShopCheckoutPaymentBase({ t, match, history, children }) {
  
  return (
    <ShopBase 
      title={t("shop.title")}
      checkoutProgress="payment"
    >
      {children}
    </ShopBase>
  )
}


export default withTranslation()(withRouter(ShopCheckoutPaymentBase))