// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import ShopBase from "../ShopBase"

function ShopContactBase({ t, match, history, children, pageHeaderOptions="" }) {
  
  return (
    <ShopBase title={t("shop.title")} pageHeaderOptions={pageHeaderOptions}>
      <h4>{t("shop.contact.title")}</h4>
        {children}
    </ShopBase>
  )
}


export default withTranslation()(withRouter(ShopContactBase))