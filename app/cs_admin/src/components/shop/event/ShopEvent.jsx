// @flow

import React, { useContext } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery, useMutation } from '@apollo/react-hooks'
import { Link } from 'react-router-dom'
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import moment from 'moment'

import {
  Card,
  GalleryCard,
  Grid,
  Icon,
  List
} from "tabler-react"
import { TimeStringToJSDateOBJ } from '../../../tools/date_tools'
import AppSettingsContext from '../../context/AppSettingsContext'

import ShopEventBase from "./ShopEventBase"
import ShopEventTicketPricingCard from "./ShopEventTicketPricingCard"

import { GET_SCHEDULE_EVENT_QUERY } from "./queries"


function ShopEvent({ t, match, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const title = t("shop.home.title")
  const eventId = match.params.event_id

  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENT_QUERY, {
    variables: { id: eventId }
  })

  if (loading) return (
    <ShopEventBase title={title} >
      {t("general.loading_with_dots")}
    </ShopEventBase>
  )
  if (error) return (
    <ShopEventBase title={title}>
      {t("shop.event.error_loading")}
    </ShopEventBase>
  )

  console.log(data)
  const event = data.scheduleEvent
  const tickets = event.tickets
  console.log(event)

  return (
    <ShopEventBase title={title}>
      <Grid.Row>
        <Grid.Col xs={12} sm={12} md={12} lg={12}>
          <h3>{event.name}</h3>
          <h5>{event.tagline}</h5>
        </Grid.Col>
      </Grid.Row>
      <Grid.Row>
        <Grid.Col xs={12} sm={12} md={6} lg={4}>
          {((event.media.edges.length) ? 
            <GalleryCard>
              <GalleryCard.Image src={(event.media.edges.length) ? event.media.edges[0].node.urlImageThumbnailLarge : ""} />
              <GalleryCard.Details>
                {(event.media.edges.length) ? event.media.edges[0].node.description : ""}
              </GalleryCard.Details>
            </GalleryCard>
          : "" )}
          <Card title={t("general.info")}>
            <Card.Body>
              <h6>{t('general.teacher')}: {(event.teacher) ? event.teacher.fullName: ""}</h6>
              <h6>{t('general.start')}: {(event.dateStart) ? moment(event.dateStart).format(dateFormat): ""}</h6>
              <h6>{t('general.end')}: {(event.dateEnd) ? moment(event.dateEnd).format(dateFormat): ""}</h6>
            </Card.Body>
          </Card>
        </Grid.Col>
        <Grid.Col xs={12} sm={12} md={6} lg={8}>
          <Card title={t("general.description")}>
            <Card.Body>
              <h5>{t('general.description')}</h5>
              <div dangerouslySetInnerHTML={{ __html: event.description}} />
            </Card.Body>
          </Card>
        </Grid.Col>
      </Grid.Row>
      <Grid.Row>
        <Grid.Col xs={12} sm={12} md={12} lg={12}>
          <h3>{t("shop.event.tickets")}</h3>
        </Grid.Col>
        {tickets.edges.map(({ node }) => (
          <Grid.Col xs={12} sm={12} md={6} lg={4}>
            <ShopEventTicketPricingCard eventID={eventId} eventTicket={node} />
          </Grid.Col>
        ))}
      </Grid.Row>
    </ShopEventBase>
  )
}


export default withTranslation()(withRouter(ShopEvent))
