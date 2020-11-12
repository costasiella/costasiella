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
import ScheduleEventTicketTabs from "./ScheduleEventTicketTabs"

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

import ScheduleEventTicketBack from "./ScheduleEventTicketBack"
import ScheduleEventEditBaseBase from "../edit/ScheduleEventEditBaseBase"


function ScheduleEventTicketEditBase({t, match, history, activeTab, children}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const cardTitle = t("schedule.events.edit.title")
  const activeLink = "tickets"

  const eventId = match.params.event_id
  const ticketId = match.params.id

  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENT_QUERY, {
    variables: { id: eventId }
  })

  const sidebarContent = <ScheduleEventTicketBack />

if (loading) {
  return (
    <ScheduleEventEditBaseBase sidebarContent={sidebarContent}>
      <Card title={cardTitle}>
        <ScheduleEventTicketTabs active={activeTab} eventId={eventId}  ticketId={ticketId}/>
        <Card.Body>
          <Dimmer loading={true} active={true} />
        </Card.Body>
      </Card>
    </ScheduleEventEditBaseBase>
  )
}

if (error) {
  return (
    <ScheduleEventEditBaseBase sidebarContent={sidebarContent}>
      <Card title={cardTitle}>
        <ScheduleEventTicketTabs active={activeTab} eventId={eventId} ticketId={ticketId}/>
        <Card.Body>
          {t("schedule.events.error_loading")}
        </Card.Body>
      </Card>
    </ScheduleEventEditBaseBase>
  )
}

const event = data.scheduleEvent
const dateStart = (event.dateStart) ? moment(event.dateStart).format(dateFormat) : ""
const cardSubTitle = (event) ? 
<span className="text-muted">
  - {event.name + " " + dateStart}
</span> : ""

return (
  <ScheduleEventEditBaseBase activeLink={activeLink} sidebarContent={sidebarContent}>
    <Card>
      <Card.Header>
        <Card.Title>{cardTitle} {cardSubTitle}</Card.Title>
      </Card.Header>
      <ScheduleEventTicketTabs active={activeTab} eventId={eventId} ticketId={ticketId}/>
      {children}
    </Card>
  </ScheduleEventEditBaseBase>
  )
}

export default withTranslation()(withRouter(ScheduleEventTicketEditBase))