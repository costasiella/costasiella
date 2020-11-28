// @flow

import React, { useContext } from 'react'
import { useQuery } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'

import AppSettingsContext from '../../../context/AppSettingsContext'
import ButtonAddSecondaryMenu from '../../../ui/ButtonAddSecondaryMenu'
import BadgeBoolean from "../../../ui/BadgeBoolean"

import { GET_SCHEDULE_EVENT_ACTIVITIES_QUERY } from './queries'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Table,
} from "tabler-react";
// import HasPermissionWrapper from "../../../../HasPermissionWrapper"
import ScheduleEventEditListBase from "../edit/ScheduleEventEditListBase"
// import ScheduleEventTicketListBase from "./ScheduleEventTicketListBase"
import ScheduleEventActivityDelete from "./ScheduleEventActivityDelete"
import moment from 'moment';


function scheduleItems({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  console.log(appSettings)
  
  const eventId = match.params.event_id
  const activeLink = "activities"

  const sidebarContent = <Link to={`/schedule/events/edit/${eventId}/activities/add`}>
    <Button color="primary btn-block mb-6">
      <Icon prefix="fe" name="plus-circle" /> {t('schedule.events.activities.add')}
    </Button>
  </Link>

  const { loading, error, data, fetchMore } = useQuery(GET_SCHEDULE_EVENT_ACTIVITIES_QUERY, {
    variables: {
      schedule_event: eventId
    }
  })
  
  if (loading) return (
    <ScheduleEventEditListBase activeLink={activeLink} sidebarContent={sidebarContent}>
      {t("general.loading_with_dots")}
    </ScheduleEventEditListBase>
  )
  if (error) return (
    <ScheduleEventEditListBase activeLink={activeLink} sidebarContent={sidebarContent}>
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </ScheduleEventEditListBase>
  )

  console.log('query data')
  console.log(data)

  const scheduleItems = data.scheduleItems
  const pageInfo = data.scheduleItems.pageInfo

  // Empty list
  if (!scheduleItems.edges.length) { return (
    <ScheduleEventEditListBase activeLink={activeLink} sidebarContent={sidebarContent}>
      <p>{t('schedule.events.tickets.empty_list')}</p>
    </ScheduleEventEditListBase>
  )}

  const onLoadMore = () => {
    fetchMore({
      variables: {
        after: scheduleItems.pageInfo.endCursor
      },
      updateQuery: (previousResult, { fetchMoreResult }) => {
        const newEdges = fetchMoreResult.scheduleItems.edges
        const pageInfo = fetchMoreResult.scheduleItems.pageInfo

        return newEdges.length
          ? {
              // Put the new invoices at the end of the list and update `pageInfo`
              // so we have the new `endCursor` and `hasNextPage` values
              scheduleItems: {
                __typename: previousResult.scheduleItems.__typename,
                edges: [ ...previousResult.scheduleItems.edges, ...newEdges ],
                pageInfo
              }
            }
          : previousResult
      }
    })
  }

  return (
    <ScheduleEventEditListBase activeLink={activeLink} pageInfo={pageInfo} onLoadMore={onLoadMore} sidebarContent={sidebarContent}>
      <Table>
        <Table.Header>
          <Table.Row key={v4()}>
            <Table.ColHeader>{t('general.time')}</Table.ColHeader>
            <Table.ColHeader>{t('general.name')}</Table.ColHeader>
            <Table.ColHeader>{t('general.location')}</Table.ColHeader>
            <Table.ColHeader>{t('general.teacher')}</Table.ColHeader>
            <Table.ColHeader>{t('general.filled')}</Table.ColHeader>
            <Table.ColHeader>{t('general.public')}</Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
            {scheduleItems.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col>
                  {moment(node.dateStart).format(dateFormat)} <br />
                  {/* Start & end time */}
                  {moment(node.dateStart + ' ' + node.timeStart).format(timeFormat)} {' - '}
                  {moment(node.dateStart + ' ' + node.timeEnd).format(timeFormat)} { ' ' }
                </Table.Col>
                <Table.Col>
                  {node.name} <br />
                  <div dangerouslySetInnerHTML={{__html: node.description}} className="text-muted"/>
                </Table.Col>
                <Table.Col>
                  {node.organizationLocationRoom.organizationLocation.name} <br />
                  <span className="text-muted">{node.organizationLocationRoom.name}</span>
                </Table.Col>
                <Table.Col>
                  {node.account.fullName} 
                  {(node.account2) ? <span className="text-muted"><br />{node.account2.fullName}</span> : ""}
                </Table.Col>
                <Table.Col>
                  {node.countAttendance}/{node.spaces}
                </Table.Col>
                <Table.Col>
                  <BadgeBoolean value={node.displayPublic} />
                </Table.Col>
                <Table.Col className="text-right">
                  <Link to={`/schedule/events/edit/${eventId}/activities/edit/${node.id}`}>
                    <Button className='btn-sm' 
                            color="secondary">
                      {t('general.edit')}
                    </Button>
                  </Link>
                </Table.Col>
                <Table.Col className="text-right">
                  <ScheduleEventActivityDelete id={node.id} />
                </Table.Col>
              </Table.Row>
            ))}
        </Table.Body>
      </Table>
    </ScheduleEventEditListBase>
  )
}

export default withTranslation()(withRouter(scheduleItems))
