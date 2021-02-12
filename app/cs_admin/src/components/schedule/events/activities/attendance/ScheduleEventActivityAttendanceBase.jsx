// @flow

import React, { useContext } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'

import AppSettingsContext from '../../../../context/AppSettingsContext'
import ContentCard from "../../../../general/ContentCard"

import { GET_SCHEDULE_EVENT_ACTIVITY_QUERY } from '../queries'
import { GET_SCHEDULE_EVENT_QUERY } from '../../queries'

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
import HasPermissionWrapper from "../../../../HasPermissionWrapper"

import ScheduleEventActivityBack from "../ScheduleEventActivityBack"
import ScheduleEventEditBaseBase from "../../edit/ScheduleEventEditBaseBase"
import ScheduleEventActivityTabs from "../ScheduleEventActivityTabs"


function ScheduleEventActivityAttendanceBase({t, match, history, activeTab, onLoadMore, pageInfo, children}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const cardTitle = t("schedule.events.activities.edit")
  const activeLink = "activities"

  const eventId = match.params.event_id
  const scheduleItemId = match.params.id

  const { loading, error, data } = useQuery(GET_SCHEDULE_EVENT_QUERY, {
    variables: { id: eventId }
  })

  const { loading: loadingActivity, error: errorActivity, data: dataActivity } = useQuery(GET_SCHEDULE_EVENT_ACTIVITY_QUERY, {
    variables: {
      id: scheduleItemId
    }
  })

  const sidebarContent = <ScheduleEventActivityBack />

  if (loading || loadingActivity) {
    return (
      <ScheduleEventEditBaseBase  activeLink={activeLink} sidebarContent={sidebarContent}>
        <Card title={cardTitle}>
          <ScheduleEventActivityTabs active={activeTab} eventId={eventId} scheduleItemId={scheduleItemId}/>
          <Card.Body>
            <Dimmer loading={true} active={true} />
          </Card.Body>
        </Card>
      </ScheduleEventEditBaseBase>
    )
  }

  if (error || errorActivity) {
    return (
      <ScheduleEventEditBaseBase activeLink={activeLink} sidebarContent={sidebarContent}>
        <Card title={cardTitle}>
          <ScheduleEventActivityTabs active={activeTab} eventId={eventId} scheduleItemId={scheduleItemId}/>
          <Card.Body>
            {t("schedule.event.error_loading")}
          </Card.Body>
        </Card>
      </ScheduleEventEditBaseBase>
    )
  }

  const event = data.scheduleEvent
  const scheduleItem = dataActivity.scheduleItem
  const dateStart = (event.dateStart) ? moment(event.dateStart).format(dateFormat) : ""
  const cardSubTitle = (scheduleItem) ? 
  <span className="text-muted">
    - {event.name + " " + dateStart}
  </span> : ""

  const cardActivitySubtitle = (scheduleItem) ?
  <span className="text-muted">
    - {scheduleItem.name}
  </span> : ""

  return (
    <ScheduleEventEditBaseBase activeLink={activeLink} sidebarContent={sidebarContent}>
      <ContentCard 
        cardTitle={<span>{cardTitle} {cardSubTitle} {cardActivitySubtitle}</span>}
        cardTabs={<ScheduleEventActivityTabs active={activeTab} eventId={eventId} scheduleItemId={scheduleItemId}/>}
        pageInfo={pageInfo}
        onLoadMore={onLoadMore}
      >
        
        {children}
      </ContentCard>
      {/* <Card>
        <Card.Header>
          <Card.Title>{cardTitle} {cardSubTitle} {cardActivitySubtitle}</Card.Title>
        </Card.Header>
        <ScheduleEventActivityTabs active={activeTab} eventId={eventId} scheduleItemId={scheduleItemId}/>
        {children}
      </Card> */}
    </ScheduleEventEditBaseBase>
  )
}

export default withTranslation()(withRouter(ScheduleEventActivityAttendanceBase))