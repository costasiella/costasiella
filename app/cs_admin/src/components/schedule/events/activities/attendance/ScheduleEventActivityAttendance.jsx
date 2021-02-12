// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'


import {
  Table
} from "tabler-react"

// import { dateToLocalISO, dateToLocalISOTime, TimeStringToJSDateOBJ } from '../../../../tools/date_tools'

import { GET_SCHEDULE_ITEM_ATTENDANCES_QUERY } from "./queries"
// import { SCHEDULE_EVENT_ACTIVITY_SCHEMA } from './yupSchema'

import ScheduleEventActivityBack from "../ScheduleEventActivityBack"
import ScheduleEventActivityAttendanceBase from "./ScheduleEventActivityAttendanceBase"
// import ScheduleEventEditBase from "../edit/ScheduleEventEditBase"
// import ScheduleEventActivityForm from "./ScheduleEventActivityForm"
import BadgeBookingStatus from "../../../../ui/BadgeBookingStatus"


function ScheduleEventActivityAttendance({ t, history, match }) {
  const eventId = match.params.event_id
  const scheduleItemId = match.params.id
  const returnUrl = `/schedule/events/edit/${eventId}/activities/`
  const activeTab = 'attendance'
  const cardTitle = t("schedule.events.activities.edit")
  const activeLink = "activities"

  const { loading, error, data, fetchMore } = useQuery(GET_SCHEDULE_ITEM_ATTENDANCES_QUERY, {
    variables: {
      schedule_item: scheduleItemId
    },
    fetchPolicy: "network-only"
  })

  const sidebarContent = <ScheduleEventActivityBack />

  if (loading) return (
    <ScheduleEventActivityAttendanceBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeTab={activeTab} 
      returnUrl={returnUrl}
    >
      {t("general.loading_with_dots")}
    </ScheduleEventActivityAttendanceBase>
  )
  if (error) return (
    <ScheduleEventActivityAttendanceBase 
      sidebarContent={sidebarContent} 
      cardTitle={cardTitle} 
      activeTab={activeTab} 
      returnUrl={returnUrl}
    >
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </ScheduleEventActivityAttendanceBase>
  )

  const scheduleItemAttendances = data.scheduleItemAttendances
  console.log(data)
  const pageInfo = scheduleItemAttendances.pageInfo

  // Empty list
  if (!scheduleItemAttendances.edges.length) { return (
    <ScheduleEventActivityAttendanceBase activeLink={activeLink} sidebarContent={sidebarContent}>
      <p>{t('schedule.events.activities.attendance.empty_list')}</p>
    </ScheduleEventActivityAttendanceBase>
  )}

  const onLoadMore = () => {
    fetchMore({
      variables: {
        after: scheduleItemAttendances.pageInfo.endCursor
      },
      updateQuery: (previousResult, { fetchMoreResult }) => {
        const newEdges = fetchMoreResult.scheduleItemAttendances.edges
        const pageInfo = fetchMoreResult.scheduleItemAttendances.pageInfo

        return newEdges.length
          ? {
              // Put the new attendance items at the end of the list and update `pageInfo`
              // so we have the new `endCursor` and `hasNextPage` values
              scheduleItemAttendances: {
                __typename: previousResult.scheduleItemAttendances.__typename,
                edges: [ ...previousResult.scheduleItemAttendances.edges, ...newEdges ],
                pageInfo
              }
            }
          : previousResult
      }
    })
  }

  return (
    <ScheduleEventActivityAttendanceBase 
      // sidebarContent={sidebarContent} 
      // cardTitle={cardTitle} 
      activeTab={activeTab} 
      pageInfo={pageInfo}
      onLoadMore={onLoadMore}
    >
      <Table>
        <Table.Header>
          <Table.Row key={v4()}>
            <Table.ColHeader>{t('general.name')}</Table.ColHeader>
            <Table.ColHeader>{t('general.booking_status')}</Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {scheduleItemAttendances.edges.map(({ node }) => (
            <Table.Row key={v4()}>
              <Table.Col>
                {node.account.fullName}
              </Table.Col>
              <Table.Col>
                <BadgeBookingStatus status={node.bookingStatus} />
              </Table.Col>
            </Table.Row>
          ))}
        </Table.Body>
      </Table>
    </ScheduleEventActivityAttendanceBase>
  )
}


export default withTranslation()(withRouter(ScheduleEventActivityAttendance))