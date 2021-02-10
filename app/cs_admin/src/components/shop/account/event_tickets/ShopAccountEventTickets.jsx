// @flow

import React, { useContext} from 'react'
import { useQuery } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { v4 } from "uuid"
import moment from 'moment'

import AppSettingsContext from '../../../context/AppSettingsContext'
import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"

import {
  Badge,
  Card,
  Grid,
  Table
} from "tabler-react";
import { GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY } from "../../../relations/accounts/schedule_event_tickets/queries"

import ShopAccountProfileBase from "../ShopAccountProfileBase"
import ContentCard from "../../../general/ContentCard"


function ShopAccountEventTickets({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const { loading: loadingUser, error: errorUser, data: dataUser } = useQuery(GET_USER_PROFILE)
  const { loading, error, data, fetchMore } = useQuery(GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY, {
    skip: loadingUser || errorUser || !dataUser,
    variables: {
      account: dataUser && dataUser.user ? dataUser.user.accountId : null
    }
  })  

  if (loading || loadingUser || !data) return (
    <ShopAccountProfileBase>
      {t("general.loading_with_dots")}
    </ShopAccountProfileBase>
  )
  if (error || errorUser) return (
    <ShopAccountProfileBase>
      {t("shop.account.event_tickets.error_loading_data")}
    </ShopAccountProfileBase>
  )

  console.log("User data: ###")
  console.log(dataUser)
  const user = dataUser.user
  const eventTickets = data.accountScheduleEventTickets

  // Empty list
  if (!eventTickets.edges.length) {
    return (
      <ShopAccountProfileBase accountName={user.fullName}>
        <Grid.Row>
          <Grid.Col md={12}>
            <Card cardTitle={t('shop.account.event_tickets.title')} >
              <Card.Body>
                {t('shop.account.event_tickets.empty_list')}
              </Card.Body>
            </Card>
          </Grid.Col>
        </Grid.Row>
      </ShopAccountProfileBase>
    )  
  }

  // Populated list
  return (
    <ShopAccountProfileBase accountName={user.fullName}>
      <Grid.Row>
        <Grid.Col md={12}>
          <ContentCard cardTitle={t('shop.account.event_tickets.title')}
            // headerContent={headerOptions}
            pageInfo={eventTickets.pageInfo}
            onLoadMore={() => {
              fetchMore({
                variables: {
                  after: eventTickets.pageInfo.endCursor
                },
                updateQuery: (previousResult, { fetchMoreResult }) => {
                  const newEdges = fetchMoreResult.accountScheduleEventTickets.edges
                  const pageInfo = fetchMoreResult.accountScheduleEventTickets.pageInfo

                  return newEdges.length
                    ? {
                        // Put the new tickets at the end of the list and update `pageInfo`
                        // so we have the new `endCursor` and `hasNextPage` values
                        eventTickets: {
                          __typename: previousResult.accountScheduleEventTickets.__typename,
                          edges: [ ...previousResult.accountScheduleEventTickets.edges, ...newEdges ],
                          pageInfo
                        }
                      }
                    : previousResult
                }
              })
            }} >
            <Table>
              <Table.Header>
                <Table.Row key={v4()}>
                  <Table.ColHeader>{t('general.ticket')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.start')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.location')}</Table.ColHeader>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {eventTickets.edges.map(({ node }) => (
                  <Table.Row key={v4()}>
                    <Table.Col>
                      {node.scheduleEventTicket.scheduleEvent.name} <br />
                      <Badge>{node.scheduleEventTicket.name}</Badge> {" "}
                      {(node.cancelled) ? <Badge color="warning">{t("general.cancelled")}</Badge> : ""}
                    </Table.Col>
                    <Table.Col>
                      {moment(node.scheduleEventTicket.scheduleEvent.dateStart).format(dateFormat)}
                    </Table.Col>
                    <Table.Col>
                      {node.scheduleEventTicket.scheduleEvent.organizationLocation.name}
                    </Table.Col>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          </ContentCard>
        </Grid.Col>
      </Grid.Row>
    </ShopAccountProfileBase>
  )
}


export default withTranslation()(withRouter(ShopAccountEventTickets))