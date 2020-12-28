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
  Grid,
  Icon,
  List
} from "tabler-react"
import { TimeStringToJSDateOBJ } from '../../../tools/date_tools'
import AppSettingsContext from '../../context/AppSettingsContext'

import ShopEventBase from "./ShopEventBase"
// import ShopClasspassesPricingCard from "./ShopClasspassPricingCard"

import { GET_SCHEDULE_EVENT_QUERY } from "./queries"


function ShopEvent({ t, match, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const title = t("shop.home.title")
  const eventId = match.params.id

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
      {t("shop.classpass.error_loading")}
    </ShopEventBase>
  )

  console.log(data)
  const event = data.scheduleEvent
  console.log(event)

  return (
    <ShopEventBase title={title}>
      <Grid.Row>
        <Grid.Col xs={12} sm={12} md={6} lg={4}>
          {/* Add galery image here... */}
          Image here
        </Grid.Col>
        <Grid.Col xs={12} sm={12} md={6} lg={8}>
          <Card title={t("shop.event.title")}>
            <Card.Body>
              Info here
            </Card.Body>
          </Card>
        </Grid.Col>
      </Grid.Row>
      <Grid.Row>
        Description here
      </Grid.Row>
      <Grid.Row>
        Tickets here
      </Grid.Row>
    </ShopEventBase>
  )
}


export default withTranslation()(withRouter(ShopEvent))
