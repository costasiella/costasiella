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

import { GET_SCHEDULE_EVENT_QUERY } from '../queries'
import ScheduleEventEditTabs from "../ScheduleEventEditTabs"

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

import ScheduleEventsBase from "../ScheduleEventsBase"


function ScheduleEventEditBase({t, match, history, activeTab, children,returnUrl="/schedule/events"}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const cardTitle = t("schedule.events.edit.title")

  const eventId = match.params.event_id

  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENT_QUERY, {
    variables: { id: eventId }
  })

  const sidebarContent = <Link to={returnUrl}>
      <Button color="primary btn-block mb-6">
        <Icon prefix="fe" name="chevrons-left" /> {t('general.back')}
      </Button>
    </Link>

if (loading) {
  return (
    <ScheduleEventsBase sidebarContent={sidebarContent}>
      <Card title={cardTitle}>
        <ScheduleEventEditTabs active={activeTab} eventId={eventId}/>
        <Card.Body>
          <Dimmer loading={true} active={true} />
        </Card.Body>
      </Card>
    </ScheduleEventsBase>
  )
}

if (error) {
  return (
    <ScheduleEventsBase sidebarContent={sidebarContent}>
      <Card title={cardTitle}>
        <ScheduleEventEditTabs active={activeTab} eventId={eventId}/>
        <Card.Body>
          {t("schedule.events.error_loading")}
        </Card.Body>
      </Card>
    </ScheduleEventsBase>
  )
}

const event = data.scheduleEvent
const dateStart = (event.dateStart) ? moment(event.dateStart).format(dateFormat) : ""
const cardSubTitle = (event) ? 
<span className="text-muted">
  - {event.name + " " + dateStart}
</span> : ""

return (
  <ScheduleEventsBase sidebarContent={sidebarContent}>
    <Card>
      <Card.Header>
        <Card.Title>{cardTitle} {cardSubTitle}</Card.Title>
      </Card.Header>
      <ScheduleEventEditTabs active={activeTab} eventId={eventId}/>
      {children}
    </Card>
  </ScheduleEventsBase>
  )
}

export default withTranslation()(withRouter(ScheduleEventEditBase))