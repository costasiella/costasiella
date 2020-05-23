// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Card,
  Grid,
} from "tabler-react";

function ShopClassBookPriceDropin({ 
  t, 
  match, 
  history, 
  priceDropin
}) {
  console.log('priceDropin')
  console.log(priceDropin)

  return (
    <Grid.Col md={3}>
      <Card 
        statusColor="blue"
        title={t("general.dropin")} >
      <Card.Body>
        <b>{priceDropin.priceDisplay}</b><br />
        {t("shop.classes.book.dropin_pay_and_book")} <br />
      </Card.Body>
      <Card.Footer>
        Button here
        {/* <ShopClassBookPriceBtn price={priceDropin} locationID={locationId} /> */}
      </Card.Footer>
      </Card>
    </Grid.Col>
  )
}


export default withTranslation()(withRouter(ShopClassBookPriceDropin))

