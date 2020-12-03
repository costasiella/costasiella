// @flow

import React, { useState } from 'react'
import { useQuery, useMutation, useLazyQuery } from '@apollo/react-hooks'
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import { v4 } from 'uuid'

import {
  Card,
  Table,
} from "tabler-react";

import { GET_ACCOUNTS_QUERY } from "../../../../../queries/accounts/account_search_queries"
import { GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY } from "./queries"
// import { SCHEDULE_EVENT_TICKET_SCHEDLE_ITEM_SCHEMA } from "./yupSchema"
import { get_accounts_query_variables } from "./tools"

import InputSearch from "../../../../general/InputSearch"
import ScheduleEventTicketBack from "../ScheduleEventTicketBack"
import ScheduleEventTicketEditBase from "../ScheduleEventTicketEditBase"
// import ScheduleEventTicketEditActivityForm from "./ScheduleEventTicketEditActivityForm"

import CSLS from "../../../../../tools/cs_local_storage"


const UPDATE_SCHEDULE_EVENT_TICKET_SCHEDULE_ITEM = gql`
  mutation UpdateScheduleEventTicketScheduleItem($input:UpdateScheduleEventTicketScheduleItemInput!) {
    updateScheduleEventTicketScheduleItem(input: $input) {
      scheduleEventTicketScheduleItem {
        id
      }
    }
  }
`


function ScheduleEventTicketEditCustomers({ t, history, match }) {
  const [showSearch, setShowSearch] = useState(false)
  const id = match.params.id
  const eventId = match.params.event_id
  const returnUrl = `/schedule/events/edit/${eventId}/tickets/`
  const activeTab = "customers"
  const activeLink = 'tickets'
  const sidebarContent = <ScheduleEventTicketBack />

  const { loading, error, data } = useQuery(GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY, {
    variables: {
      schedule_event_ticket: id
    }
  })

  // const [updateScheduleEventTicketScheduleItem] = useMutation(UPDATE_SCHEDULE_EVENT_TICKET_SCHEDULE_ITEM)


  const [ getAccounts, 
    { refetch: refetchAccounts, 
      fetchMore: fetchMoreAccounts,
      loading: queryAccountsLoading, 
      error: queryAccountsError, 
      data: queryAccountsData 
    }] = useLazyQuery( GET_ACCOUNTS_QUERY )

  console.log('queryAccountsData')
  console.log(queryAccountsData)

  if (loading) return (
    <ScheduleEventTicketEditBase 
      sidebarContent={sidebarContent} 
      activeTab={activeTab} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
    >
      {t("general.loading_with_dots")}
    </ScheduleEventTicketEditBase>
  )
  if (error) return (
    <ScheduleEventTicketEditBase 
      sidebarContent={sidebarContent} 
      activeTab={activeTab} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
    >
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </ScheduleEventTicketEditBase>
  )

  console.log('query data')
  console.log(data)
  const inputData = data
  const scheduleEventTicketActivities = data.scheduleEventTicketScheduleItems
  console.log(scheduleEventTicketActivities)

  const pageHeaderOptions = <InputSearch 
    initialValueKey={CSLS.SCHEDULE_EVENTS_TICKETS_CUSTOMERS_SEARCH}
    placeholder="Search..."
    onChange={(value) => {
      console.log(value)
      localStorage.setItem(CSLS.SCHEDULE_EVENTS_TICKETS_CUSTOMERS_SEARCH, value)
      if (value) {
        // {console.log('showSearch')}
        // {console.log(showSearch)}
        setShowSearch(true)
        getAccounts({ variables: get_accounts_query_variables()})
      } else {
        setShowSearch(false)
      }
    }}
  />

  const searchResults = "hello world for search results"

  return (
    <ScheduleEventTicketEditBase 
      sidebarContent={sidebarContent} 
      activeTab={activeTab} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
      pageHeaderOptions={pageHeaderOptions}
      SearchResults={searchResults}
    >
      <Card.Body>
        <Table>
          <Table.Header>
            <Table.Row>
              <Table.ColHeader>{t('general.name')}</Table.ColHeader>
              <Table.ColHeader>{t('general.included')}</Table.ColHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {scheduleEventTicketActivities.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col>
                  {node.scheduleItem.name}
                </Table.Col>  
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      </Card.Body>
    </ScheduleEventTicketEditBase>
  )
}


export default withTranslation()(withRouter(ScheduleEventTicketEditCustomers))