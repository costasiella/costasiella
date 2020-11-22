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
import ContentCard from "../../../general/ContentCard"

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

import ScheduleEventEditListBase from "../edit/ScheduleEventEditListBase"


function ScheduleEventTicketListBase({t, match, history, activeTab, pageInfo, onLoadMore, children}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const cardTitle = t("schedule.events.edit.title")
  const activeLink = "tickets"

  const eventId = match.params.event_id
  const returnUrl = "/schedule/events"

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
    <ScheduleEventEditListBase sidebarContent={sidebarContent} activeLink={activeLink}>
      <Card title={cardTitle}>
        <Card.Body>
          <Dimmer loading={true} active={true} />
        </Card.Body>
      </Card>
    </ScheduleEventEditListBase>
  )
}

if (error) {
  return (
    <ScheduleEventEditListBase sidebarContent={sidebarContent} activeLink={activeLink}>
      <Card title={cardTitle}>
        <Card.Body>
          {t("schedule.events.error_loading")}
        </Card.Body>
      </Card>
    </ScheduleEventEditListBase>
  )
}

const event = data.scheduleEvent
const dateStart = (event.dateStart) ? moment(event.dateStart).format(dateFormat) : ""
const cardSubTitle = (event) ? 
<span className="text-muted">
  - {event.name + " " + dateStart}
</span> : ""

return (
  <ScheduleEventEditListBase sidebarContent={sidebarContent} activeLink={activeLink}>
    <ContentCard 
      cardTitle={<span>{cardTitle} {cardSubTitle}</span>}
      pageInfo={pageInfo}
      onLoadMore={onLoadMore}
    >
      {children}
    </ContentCard>
  </ScheduleEventEditListBase>
  )
}

export default withTranslation()(withRouter(ScheduleEventTicketListBase))