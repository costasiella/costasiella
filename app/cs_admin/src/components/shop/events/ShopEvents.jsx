// @flow

import React, {Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'

import {
  Button,
  Grid,
  Icon,
  List,
  GalleryCard
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
            <Grid.Col xs={12} sm={12} md={6} lg={4} key={v4()}>
              <GalleryCard>
                {(node.media.edges.length) ?
                  <GalleryCard.Image 
                    src={(node.media.edges.length) ? node.media.edges[0].node.urlImageThumbnailLarge: ""} 
                    href={`/shop/events/${node.id}`}
                  /> : "" }
                <GalleryCard.Footer>
                  <h4>{node.name}</h4>
                </GalleryCard.Footer>
                <GalleryCard.Footer>                  
                  <GalleryCard.Details
                    fullName={<span className="">{(node.teacher) ? node.teacher.fullName: ""}</span>}
                    dateString={node.organizationLocation.name}
                  />
                  <GalleryCard.IconGroup>
                  <GalleryCard.IconItem 
                    name="calendar"
                    label={node.dateStart}
                    right={false}
                    RootComponent="span"
                  />
                  </GalleryCard.IconGroup>
                </GalleryCard.Footer>
                <Link to={`/shop/events/${node.id}`}>
                  <GalleryCard.Footer pt={10}>
                    <Button
                      block
                      color="link"
                    >
                      {t("shop.events.tell_me_more")} <Icon name="chevron-right" />
                    </Button>
                  </GalleryCard.Footer>
                </Link>
              </GalleryCard>
            </Grid.Col>
          ))}
        </Grid.Row>

        
    </ShopEventsBase>
  )
}


export default withTranslation()(withRouter(ShopEvents))
