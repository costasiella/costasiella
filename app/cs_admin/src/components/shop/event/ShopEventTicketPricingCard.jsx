// @flow

import React, { useContext } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'

import moment from 'moment'

import {
  Grid,
  Icon,
  List,
  PricingCard
} from "tabler-react";

import AppSettingsContext from '../../context/AppSettingsContext'

// Example:
// https://github.com/tabler/tabler-react/blob/master/example/src/interface/PricingCardsPage.react.js


function ShopEventTicketPricingCard({ t, eventTicket, btnLink, active=false }) {
  // eventTicket should be an object with at least the following values from an organizationClasspass object:
  // id, name, priceDisplay, 
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  const scheduleItems = eventTicket.scheduleItems

  return (
    <PricingCard active={active}>
      <PricingCard.Category>
        {eventTicket.name}
      </PricingCard.Category>
      <PricingCard.Price>
        {eventTicket.priceDisplay}
      </PricingCard.Price>
      <PricingCard.AttributeList>
        {scheduleItems.edges.map(({ node }) => (
          <PricingCard.AttributeItem>
            <b>
              {moment(node.dateStart).format(dateFormat)} {" "}
              {/* Start & end time */}
              {moment(node.dateStart + ' ' + node.timeStart).format(timeFormat)} {' - '}
              {moment(node.dateStart + ' ' + node.timeEnd).format(timeFormat)} { ' ' }
            </b><br />
            {node.name} {t("general.at").toLowerCase()} {node.organizationLocationRoom.organizationLocation.name}
          </PricingCard.AttributeItem>
        ))}
      </PricingCard.AttributeList>
      {/* {(btnLink) ?
        <Link to={btnLink}>
          <PricingCard.Button >
            {t("shop.classpasses.choose")} <Icon name="chevron-right" />
          </PricingCard.Button>
        </Link>
        : ""
      } */}
    </PricingCard>
  )
}


export default withTranslation()(withRouter(ShopEventTicketPricingCard))


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