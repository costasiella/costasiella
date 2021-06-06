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

import { GET_SCHEDULE_EVENT_EARLYBIRDS_QUERY } from './queries'

import {
  Avatar,
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
import ScheduleEventEarlybirdDelete from "./ScheduleEventEarlybirdDelete"
import moment from 'moment';


function ScheduleEventEarlybirds({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  console.log(appSettings)
  
  const eventId = match.params.event_id
  const activeLink = "earlybirds"

  const sidebarContent = <Link to={`/schedule/events/edit/${eventId}/earlybirds/add`}>
    <Button color="primary btn-block mb-6">
      <Icon prefix="fe" name="plus-circle" /> {t('schedule.events.earlybirds.add')}
    </Button>
  </Link>

  const { loading, error, data, fetchMore } = useQuery(GET_SCHEDULE_EVENT_EARLYBIRDS_QUERY, {
    variables: {
      scheduleEvent: eventId
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

  const scheduleEventEarlybirds = data.scheduleEventEarlybirds
  const pageInfo = data.scheduleEventEarlybirds.pageInfo

  // Empty list
  if (!scheduleEventEarlybirds.edges.length) { return (
    <ScheduleEventEditListBase activeLink={activeLink} sidebarContent={sidebarContent}>
      <p>{t('schedule.events.earlybirds.empty_list')}</p>
    </ScheduleEventEditListBase>
  )}

  const onLoadMore = () => {
    fetchMore({
      variables: {
        after: scheduleEventEarlybirds.pageInfo.endCursor
      },
      updateQuery: (previousResult, { fetchMoreResult }) => {
        const newEdges = fetchMoreResult.scheduleEventEarlybirds.edges
        const pageInfo = fetchMoreResult.scheduleEventEarlybirds.pageInfo

        return newEdges.length
          ? {
              // Put the new invoices at the end of the list and update `pageInfo`
              // so we have the new `endCursor` and `hasNextPage` values
              scheduleEventEarlybirds: {
                __typename: previousResult.scheduleEventEarlybirds.__typename,
                edges: [ ...previousResult.scheduleEventEarlybirds.edges, ...newEdges ],
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
            <Table.ColHeader>{t('general.date_start')}</Table.ColHeader>
            <Table.ColHeader>{t('general.date_end')}</Table.ColHeader>
            <Table.ColHeader>{t('schedule.events.earlybirds.discountPercentage')}</Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
            {scheduleEventEarlybirds.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col>
                  {moment(node.dateStart).format(dateFormat)}
                </Table.Col>
                <Table.Col>
                  {moment(node.dateEnd).format(dateFormat)}
                </Table.Col>
                <Table.Col>
                  {node.discountPercentage} %
                </Table.Col>
                <Table.Col className="text-right">
                  <Link to={`/schedule/events/edit/${eventId}/earlybirds/edit/${node.id}`}>
                    <Button className='btn-sm' 
                            color="secondary">
                      {t('general.edit')}
                    </Button>
                  </Link>
                </Table.Col>
                <Table.Col className="text-right">
                  <ScheduleEventEarlybirdDelete id={node.id} />
                </Table.Col>
              </Table.Row>
            ))}
        </Table.Body>
      </Table>
    </ScheduleEventEditListBase>
  )
}

export default withTranslation()(withRouter(ScheduleEventEarlybirds))
