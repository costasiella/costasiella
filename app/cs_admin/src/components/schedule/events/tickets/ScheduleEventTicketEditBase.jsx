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

import { GET_SCHEDULE_EVENT_TICKET_QUERY } from './queries'
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


function ScheduleEventTicketEditBase({t, match, history, activeTab, children, pageHeaderOptions="", searchResults=""}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const cardTitle = t("schedule.events.tickets.edit")
  const activeLink = "tickets"

  const eventId = match.params.event_id
  const ticketId = match.params.id

  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENT_QUERY, {
    variables: { id: eventId }
  })

  const { loading: loadingTicket, error: errorTicket, data: dataTicket } = useQuery(GET_SCHEDULE_EVENT_TICKET_QUERY, {
    variables: {
      id: ticketId
    }
  })

  const sidebarContent = <ScheduleEventTicketBack />

  if (loading || loadingTicket) {
    return (
      <ScheduleEventEditBaseBase pageHeaderOptions={pageHeaderOptions} sidebarContent={sidebarContent}>
        <Card title={cardTitle}>
          <ScheduleEventTicketTabs active={activeTab} eventId={eventId}  ticketId={ticketId}/>
          <Card.Body>
            <Dimmer loading={true} active={true} />
          </Card.Body>
        </Card>
      </ScheduleEventEditBaseBase>
    )
  }

  if (error || errorTicket) {
    return (
      <ScheduleEventEditBaseBase pageHeaderOptions={pageHeaderOptions} sidebarContent={sidebarContent}>
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
  const ticket = dataTicket.scheduleEventTicket
  const dateStart = (event.dateStart) ? moment(event.dateStart).format(dateFormat) : ""
  const cardSubTitle = (event) ? 
  <span className="text-muted">
    - {event.name + " " + dateStart}
  </span> : ""

  const cardTicketSubtitle = (ticket) ?
  <span className="text-muted">
    - {ticket.name}
  </span> : ""

  return (
    <ScheduleEventEditBaseBase pageHeaderOptions={pageHeaderOptions} activeLink={activeLink} sidebarContent={sidebarContent}>
      {searchResults}
      <Card>
        <Card.Header>
          <Card.Title>{cardTitle} {cardSubTitle} {cardTicketSubtitle}</Card.Title>
        </Card.Header>
        <ScheduleEventTicketTabs active={activeTab} eventId={eventId} ticketId={ticketId}/>
        {children}
      </Card>
    </ScheduleEventEditBaseBase>
  )
}

export default withTranslation()(withRouter(ScheduleEventTicketEditBase))