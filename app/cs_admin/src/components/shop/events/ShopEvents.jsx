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
import ShopEventsBase from "./ShopEventsBase"
// import ShopClasspassPricingCard from "../classpass/ShopClasspassPricingCard"

import { GET_SCHEDULE_EVENTS_QUERY } from "./queries"

// Example:
// https://github.com/tabler/tabler-react/blob/master/example/src/interface/PricingCardsPage.react.js


function ShopEvents({ t, match, history }) {
  const title = t("shop.home.title")
  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENTS_QUERY)

  if (loading) return (
    <ShopEventsBase title={title} >
      {t("general.loading_with_dots")}
    </ShopEventsBase>
  )
  if (error) return (
    <ShopEventsBase title={title}>
      {t("shop.classpasses.error_loading")}
    </ShopEventsBase>
  )

  console.log(data)
  const scheduleEvents = data.scheduleEvents
  console.log(scheduleEvents)

  return (
    <ShopEventsBase title={title}>
        <Grid.Row>
          {scheduleEvents.edges.map(({ node }) => (
            <Grid.Col md={3}>
              {node.name}
              {/* <ShopClasspassPricingCard
                classpass={node}
                btnLink={"/shop/classpass/" + node.id}
              /> */}
              {/* <PricingCard>
                <PricingCard.Category>
                  {node.name}
                </PricingCard.Category>
                <PricingCard.Price>
                  {node.priceDisplay}
                </PricingCard.Price>
                <PricingCard.AttributeList>
                  <PricingCard.AttributeItem>
                    <b>{(node.unlimited) ? t('general.unlimited') : node.classes }</b> { " " }
                    {((node.classes != 1) || (node.unlimited))? t('general.classes'): t('general.class')}
                  </PricingCard.AttributeItem>
                  <PricingCard.AttributeItem>
                    {t('general.valid_for')} { " " }
                    <b>{node.validity}</b> {' '} {node.validityUnitDisplay}
                  </PricingCard.AttributeItem>
                </PricingCard.AttributeList>
                <Link to={"/shop/classpass/" + node.id}>
                  <PricingCard.Button >
                    {t("shop.classpasses.choose")} <Icon name="chevron-right" />
                  </PricingCard.Button>
                </Link>
              </PricingCard> */}
            </Grid.Col>
          ))}
        </Grid.Row>

        
    </ShopEventsBase>
  )
}


export default withTranslation()(withRouter(ShopEvents))


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