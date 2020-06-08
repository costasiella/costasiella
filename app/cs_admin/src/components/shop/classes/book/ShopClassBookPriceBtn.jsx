// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"

import {
  Button,
  Icon
} from "tabler-react";


function ShopClassBookPriceBtn({t, match, history, price}) {
  console.log(price)
  const classpassId = price.id
  const scheduleItemId = match.params.class_id
  const classDate = match.params.date

  return (
    <Link to={`/shop/classpass/${classpassId}/${scheduleItemId}/${classDate}`}>
    <Button 
      block 
      outline 
      color="primary" 
    >
      {t("shop.classes.book.pay_and_book")} <Icon name="chevron-right" />
    </Button>
    </Link>
  )
}

export default withTranslation()(withRouter(ShopClassBookPriceBtn))

