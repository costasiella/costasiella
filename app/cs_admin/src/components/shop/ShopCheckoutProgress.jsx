import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Grid,
  Icon,
  Container,
  Tag,
} from "tabler-react";


function ShopCheckoutProgress({ t, match, history, checkoutProgress="" }) {
  let color_order = "" 
  let color_payment = ""
  let color_complete = ""

  switch(checkoutProgress) {
    case "order":
      color_order = "info"
      break
    case "payment":
      color_order = "success"
      color_payment = "info"
      break      
    case "complete":
      color_order = "success"
      color_payment = "success"
      color_complete = "success"
      break      
  }

  return (
    <div className="d-flex justify-content-center mb-4">
    <Tag.List>
      <Tag color={color_order} addOn={<Icon name="shopping-cart"/>}>
        {t("shop.checkout_progress.order")} 
      </Tag>
      <Tag color={color_payment} addOn={<Icon name="credit-card" />}>
        {t("shop.checkout_progress.payment")} 
      </Tag>
      <Tag color={color_complete} addOn={<Icon name="check" />}>
        {t("shop.checkout_progress.complete")}
      </Tag>
    </Tag.List>
    </div>
  )
}


export default withTranslation()(withRouter(ShopCheckoutProgress))