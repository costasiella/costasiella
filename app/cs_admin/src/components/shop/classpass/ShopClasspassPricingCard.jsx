// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'

import {
  Grid,
  Icon,
  List,
  PricingCard
} from "tabler-react";
import ShopClasspassesBase from "./ShopClasspassBase"

import { GET_ORGANIZATION_CLASSPASS_QUERY } from "./queries"

// Example:
// https://github.com/tabler/tabler-react/blob/master/example/src/interface/PricingCardsPage.react.js


function ShopClasspassPricingCard({ t, classpass, link }) {
  // classpass should be an object with at least the following values from an organizationClasspass object:
  // id, name, priceDisplay, unlimited, classes, validity, link
  return (
    <PricingCard>
      <PricingCard.Category>
        {classpass.name}
      </PricingCard.Category>
      <PricingCard.Price>
        {classpass.priceDisplay}
      </PricingCard.Price>
      <PricingCard.AttributeList>
        <PricingCard.AttributeItem>
          <b>{(classpass.unlimited) ? t('general.unlimited') : classpass.classes }</b> { " " }
          {((classpass.classes != 1) || (classpass.unlimited))? t('general.classes'): t('general.class')}
        </PricingCard.AttributeItem>
        <PricingCard.AttributeItem>
          {t('general.valid_for')} { " " }
          <b>{classpass.validity}</b> {' '} {classpass.validityUnitDisplay}
        </PricingCard.AttributeItem>
      </PricingCard.AttributeList>
      <Link to={link}>
        <PricingCard.Button >
          {t("shop.classpasses.choose")} <Icon name="chevron-right" />
        </PricingCard.Button>
      </Link>
    </PricingCard>
  )
}


export default withTranslation()(withRouter(ShopClasspassPricingCard))


{/* <Grid.Col sm={6} lg={3}>
<PricingCard active>
  <PricingCard.Category>{"Premium"}</PricingCard.Category>
  <PricingCard.Price>{"$49"} </PricingCard.Price>
  <PricingCard.AttributeList>
    <PricingCard.AttributeItem>
      <strong>10 </strong>
      {"Users"}
    </PricingCard.AttributeItem>
    <PricingCard.AttributeItem hasIcon available>
      {"Sharing Tools"}
    </PricingCard.AttributeItem>
    <PricingCard.AttributeItem hasIcon available>
      {"Design Tools"}
    </PricingCard.AttributeItem>
    <PricingCard.AttributeItem hasIcon available={false}>
      {"Private Messages"}
    </PricingCard.AttributeItem>
    <PricingCard.AttributeItem hasIcon available={false}>
      {"Twitter API"}
    </PricingCard.AttributeItem>
  </PricingCard.AttributeList>
  <PricingCard.Button active>{"Choose plan"} </PricingCard.Button>
</PricingCard>
</Grid.Col> */}