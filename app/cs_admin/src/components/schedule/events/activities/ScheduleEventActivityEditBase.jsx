// @flow

import React, { useContext } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'

import AppSettingsContext from '../../../context/AppSettingsContext'

import { GET_SCHEDULE_EVENT_ACTIVITY_QUERY } from './queries'
import { GET_SCHEDULE_EVENT_QUERY } from '../queries'

import moment from 'moment'


import {
  Dimmer,
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container
} from "tabler-react";
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import ScheduleEventActivityBack from "./ScheduleEventActivityBack"
import ScheduleEventEditBaseBase from "../edit/ScheduleEventEditBaseBase"


function ScheduleEventActivityEditBase({t, match, history, activeTab, children}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const cardTitle = t("schedule.events.activities.edit")
  const activeLink = "tickets"

  const eventId = match.params.event_id
  const activityId = match.params.id

  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENT_QUERY, {
    variables: { id: eventId }
  })

  const { loading: loadingActivity, error: errorActivity, data: dataActivity } = useQuery(GET_SCHEDULE_EVENT_ACTIVITY_QUERY, {
    variables: {
      id: activityId
    }
  })

  const sidebarContent = <ScheduleEventActivityBack />

  if (loading || loadingActivity) {
    return (
      <ScheduleEventEditBaseBase sidebarContent={sidebarContent}>
        <Card title={cardTitle}>
          <Card.Body>
            <Dimmer loading={true} active={true} />
          </Card.Body>
        </Card>
      </ScheduleEventEditBaseBase>
    )
  }

  if (error || errorActivity) {
    return (
      <ScheduleEventEditBaseBase sidebarContent={sidebarContent}>
        <Card title={cardTitle}>
          <Card.Body>
            {t("schedule.events.error_loading")}
          </Card.Body>
        </Card>
      </ScheduleEventEditBaseBase>
    )
  }

  const event = data.scheduleEvent
  const scheduleItem = dataActivity.scheduleItem
  const dateStart = (event.dateStart) ? moment(event.dateStart).format(dateFormat) : ""
  const cardSubTitle = (event) ? 
  <span className="text-muted">
    - {event.name + " " + dateStart}
  </span> : ""

  const cardActivitySubtitle = (ticket) ?
  <span className="text-muted">
    - {scheduleItem.name}
  </span> : ""

  return (
    <ScheduleEventEditBaseBase activeLink={activeLink} sidebarContent={sidebarContent}>
      <Card>
        <Card.Header>
          <Card.Title>{cardTitle} {cardSubTitle} {cardActivitySubtitle}</Card.Title>
        </Card.Header>
        {children}
      </Card>
    </ScheduleEventEditBaseBase>
  )
}

export default withTranslation()(withRouter(ScheduleEventActivityEditBase))