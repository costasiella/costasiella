// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import ShopBase from "../ShopBase"

function ShopClasspassBase({ t, match, history, children }) {
  
  return (
    <ShopBase 
      title={t("shop.title")}
      return_url="/shop/classpasses"
    >
      <h4>{t("shop.classpass.selected")}</h4>
        {children}
    </ShopBase>
  )
}


export default withTranslation()(withRouter(ShopClasspassBase))