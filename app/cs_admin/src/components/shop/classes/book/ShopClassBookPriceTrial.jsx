// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Card,
  Grid,
} from "tabler-react";

import ShopClassBookPriceBtn from './ShopClassBookPriceBtn'

function ShopClassBookPriceTrial({ 
  t, 
  match, 
  history, 
  priceTrial
}) {

  return (
    <Grid.Col md={3}>
      <Card 
        statusColor="green"
        title={t("general.trial")} >
      <Card.Body>
        <b>{priceTrial.priceDisplay}</b><br />
        {t("shop.classes.book.trial_pay_and_book")} <br />
      </Card.Body>
      <Card.Footer>
        <ShopClassBookPriceBtn price={priceTrial} />
      </Card.Footer>
      </Card>
    </Grid.Col>
  )
}


export default withTranslation()(withRouter(ShopClassBookPriceTrial))

