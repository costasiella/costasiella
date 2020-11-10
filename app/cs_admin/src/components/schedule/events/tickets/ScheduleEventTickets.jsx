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

import { GET_SCHEDULE_EVENT_TICKETS_QUERY } from './queries'

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
import ScheduleEventTicketListBase from "./ScheduleEventTicketListBase"
import ScheduleEventTicketDelete from "./ScheduleEventTicketDelete"
import moment from 'moment';


function ScheduleEventTickets({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  console.log(appSettings)
  
  const eventId = match.params.event_id
  const activeTab = "tickets"

  const buttonAdd = <ButtonAddSecondaryMenu 
                      linkTo={`/schedule/events/edit/${eventId}/tickets/add`} />

  const { loading, error, data, fetchMore } = useQuery(GET_SCHEDULE_EVENT_TICKETS_QUERY, {
    variables: {
      schedule_event: eventId
    }
  })
  
  if (loading) return (
    <ScheduleEventTicketListBase activeTab={activeTab}>
      {t("general.loading_with_dots")}
    </ScheduleEventTicketListBase>
  )
  if (error) return (
    <ScheduleEventTicketListBase activeTab={activeTab}>
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </ScheduleEventTicketListBase>
  )

  console.log('query data')
  console.log(data)

  const scheduleEventTickets = data.scheduleEventTickets
  const pageInfo = data.scheduleEventTickets.pageInfo

  // Empty list
  if (!scheduleEventTickets.edges.length) { return (
    <ScheduleEventTicketListBase activeTab={activeTab}>
      <div className="pull-right">{buttonAdd}</div>
      <h5>{t('schedule.events.tickets.title_list')}</h5>
      <p>{t('schedule.events.tickets.empty_list')}</p>
    </ScheduleEventTicketListBase>
  )}

  const onLoadMore = () => {
    fetchMore({
      variables: {
        after: scheduleEventTickets.pageInfo.endCursor
      },
      updateQuery: (previousResult, { fetchMoreResult }) => {
        const newEdges = fetchMoreResult.scheduleEventTickets.edges
        const pageInfo = fetchMoreResult.scheduleEventTickets.pageInfo

        return newEdges.length
          ? {
              // Put the new invoices at the end of the list and update `pageInfo`
              // so we have the new `endCursor` and `hasNextPage` values
              scheduleEventTickets: {
                __typename: previousResult.scheduleEventTickets.__typename,
                edges: [ ...previousResult.scheduleEventTickets.edges, ...newEdges ],
                pageInfo
              }
            }
          : previousResult
      }
    })
  }

  return (
    <ScheduleEventTicketListBase activeTab={activeTab} pageInfo={pageInfo} onLoadMore={onLoadMore}>
      <div className="pull-right">{buttonAdd}</div>
      <h5>{t('schedule.events.tickets.title_list')}</h5>
      <Table>
        <Table.Header>
          <Table.Row key={v4()}>
            <Table.ColHeader>{t('general.name')}</Table.ColHeader>
            <Table.ColHeader>{t('general.price')}</Table.ColHeader>
            <Table.ColHeader>{t('general.public')}</Table.ColHeader>
            <Table.ColHeader>{t('general.glaccount')}</Table.ColHeader>
            <Table.ColHeader>{t('general.costcenter')}</Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
            <Table.ColHeader></Table.ColHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
            {scheduleEventTickets.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                {/* <Table.Col>
                  {moment(node.dateStart).format(dateFormat)}
                </Table.Col>
                <Table.Col>
                  {moment(node.dateEnd).format(dateFormat)}
                </Table.Col> */}
                <Table.Col>
                  {node.name} <br />
                  <div dangerouslySetInnerHTML={{__html: node.description}} className="text-muted"/>
                </Table.Col>
                <Table.Col>
                  {node.priceDisplay}
                </Table.Col>
                <Table.Col>
                  <BadgeBoolean value={node.displayPublic} />
                </Table.Col>
                <Table.Col>
                  {(node.financeGlaccount) ? node.financeGlaccount.name : ""}
                </Table.Col>
                <Table.Col>
                  {(node.financeCostcenter) ? node.financeCostcenter.name : ""}
                </Table.Col>
                <Table.Col className="text-right">
                  <Link to={`/schedule/events/edit/${eventId}/tickets/edit/${node.id}`}>
                    <Button className='btn-sm' 
                            color="secondary">
                      {t('general.edit')}
                    </Button>
                  </Link>
                </Table.Col>
                <Table.Col className="text-right">
                  {/* Check for fullEvent / deletable before showing delete button */}
                  {(node.deletable) ? <ScheduleEventTicketDelete id={node.id} /> : ""}
                </Table.Col>
              </Table.Row>
            ))}
        </Table.Body>
      </Table>
    </ScheduleEventTicketListBase>
  )
}

export default withTranslation()(withRouter(ScheduleEventTickets))
