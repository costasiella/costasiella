// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import ShopBase from "../../ShopBase"

function ShopCheckoutCompleteBase({ t, match, history, children }) {
  
  return (
    <ShopBase 
      title={t("shop.title")}
      checkoutProgress="complete"
    >
      {children}
    </ShopBase>
  )
}


export default withTranslation()(withRouter(ShopCheckoutCompleteBase))