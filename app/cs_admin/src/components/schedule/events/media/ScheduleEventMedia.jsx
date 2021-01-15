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

import { GET_SCHEDULE_EVENT_MEDIAS_QUERY } from './queries'

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
import ScheduleEventMediaDelete from "./ScheduleEventMediaDelete"
import moment from 'moment';


function ScheduleEventMedia({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  console.log(appSettings)
  
  const eventId = match.params.event_id
  const activeLink = "media"

  const sidebarContent = <Link to={`/schedule/events/edit/${eventId}/media/add`}>
    <Button color="primary btn-block mb-6">
      <Icon prefix="fe" name="plus-circle" /> {t('schedule.events.media.add')}
    </Button>
  </Link>

  const { loading, error, data, fetchMore } = useQuery(GET_SCHEDULE_EVENT_MEDIAS_QUERY, {
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

  const scheduleEventMedias = data.scheduleEventMedias
  const pageInfo = data.scheduleEventMedias.pageInfo

  // Empty list
  if (!scheduleEventMedias.edges.length) { return (
    <ScheduleEventEditListBase activeLink={activeLink} sidebarContent={sidebarContent}>
      <p>{t('schedule.events.media.empty_list')}</p>
    </ScheduleEventEditListBase>
  )}

  const onLoadMore = () => {
    fetchMore({
      variables: {
        after: scheduleEventMedias.pageInfo.endCursor
      },
      updateQuery: (previousResult, { fetchMoreResult }) => {
        const newEdges = fetchMoreResult.scheduleEventMedias.edges
        const pageInfo = fetchMoreResult.scheduleEventMedias.pageInfo

        return newEdges.length
          ? {
              // Put the new invoices at the end of the list and update `pageInfo`
              // so we have the new `endCursor` and `hasNextPage` values
              scheduleEventMedias: {
                __typename: previousResult.scheduleEventMedias.__typename,
                edges: [ ...previousResult.scheduleEventMedias.edges, ...newEdges ],
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
            <Table.ColHeader></Table.ColHeader> 
            <Table.ColHeader>{t('general.description')}</Table.ColHeader>
            <Table.ColHeader>{t('general.sort_order')}</Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
            {scheduleEventMedias.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col>
                  <Avatar size="lg" imageURL={node.urlImageThumbnailSmall} />
                </Table.Col>
                <Table.Col>
                  {node.description}
                </Table.Col>
                <Table.Col>
                  {node.sortOrder}
                </Table.Col>
                <Table.Col className="text-right">
                  <Link to={`/schedule/events/edit/${eventId}/media/edit/${node.id}`}>
                    <Button className='btn-sm' 
                            color="secondary">
                      {t('general.edit')}
                    </Button>
                  </Link>
                </Table.Col>
                <Table.Col className="text-right">
                  <ScheduleEventMediaDelete id={node.id} />
                </Table.Col>
              </Table.Row>
            ))}
        </Table.Body>
      </Table>
    </ScheduleEventEditListBase>
  )
}

export default withTranslation()(withRouter(ScheduleEventMedia))
