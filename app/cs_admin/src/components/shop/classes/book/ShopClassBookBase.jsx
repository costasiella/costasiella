import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import ShopBase from "../../ShopBase"

function ShopClassBookBase({ t, match, history, children, pageHeaderOptions="" }) {
  
  return (
    <ShopBase title={t("shop.title")} pageHeaderOptions={pageHeaderOptions}>
      <h4>{t("shop.classes.book.title")}</h4>
        {children}
    </ShopBase>
  )
}


export default withTranslation()(withRouter(ShopClassBookBase))