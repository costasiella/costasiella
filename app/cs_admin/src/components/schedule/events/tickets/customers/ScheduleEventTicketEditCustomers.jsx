// @flow

import React, { useState } from 'react'
import { useQuery, useMutation, useLazyQuery } from '@apollo/react-hooks'
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'

import {
  Badge,
  Button,
  Card,
  Table,
} from "tabler-react";

import { GET_ACCOUNTS_QUERY } from "../../../../../queries/accounts/account_search_queries"
import { GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY, UPDATE_ACCOUNT_SCHEDULE_EVENT_TICKET } from "./queries"
// import { SCHEDULE_EVENT_TICKET_SCHEDLE_ITEM_SCHEMA } from "./yupSchema"
import { get_accounts_query_variables } from "./tools"

import BadgeBoolean from "../../../../ui/BadgeBoolean"
import ContentCard from "../../../../general/ContentCard"
import InputSearch from "../../../../general/InputSearch"
import ScheduleEventTicketBack from "../ScheduleEventTicketBack"
import ScheduleEventTicketEditBase from "../ScheduleEventTicketEditBase"
// import ScheduleEventTicketEditActivityForm from "./ScheduleEventTicketEditActivityForm"

import CSLS from "../../../../../tools/cs_local_storage"


const ADD_ACCOUNT_SCHEDULE_EVENT_TICKET = gql`
mutation CreateAccountScheduleEventTicket($input:CreateAccountScheduleEventTicketInput!) {
  createAccountScheduleEventTicket(input: $input) {
    accountScheduleEventTicket {
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
      scheduleEventTicket: id
    }
  })

  const [addAccountScheduleEventTicket] = useMutation(ADD_ACCOUNT_SCHEDULE_EVENT_TICKET)
  const [updateAccountScheduleEventTicket] = useMutation(UPDATE_ACCOUNT_SCHEDULE_EVENT_TICKET)
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
  const accountScheduleEventTickets = data.accountScheduleEventTickets
  console.log(accountScheduleEventTickets)

  let accountIdsWithTickets = []
  accountScheduleEventTickets.edges.map(({ node }) => (
    accountIdsWithTickets.push(node.account.id)
  ))
  console.log(accountIdsWithTickets)

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

  // const searchResults = <div>hello world for search results</div>

  // Search results
  const searchResults = (showSearch && (queryAccountsData) && (!queryAccountsLoading) && (!queryAccountsError)) ?
    <ContentCard cardTitle={t('general.search_results')}
                pageInfo={queryAccountsData.accounts.pageInfo}
                onLoadMore={() => {
                  fetchMoreAccounts({
                    variables: {
                    after: queryAccountsData.accounts.pageInfo.endCursor
                  },
                  updateQuery: (previousResult, { fetchMoreResult }) => {
                    const newEdges = fetchMoreResult.accounts.edges
                    const pageInfo = fetchMoreResult.accounts.pageInfo 

                    return newEdges.length
                      ? {
                          // Put the new accounts at the end of the list and update `pageInfo`
                          // so we have the new `endCursor` and `hasNextPage` values
                          queryAccountsData: {
                            accounts: {
                              __typename: previousResult.accounts.__typename,
                              edges: [ ...previousResult.accounts.edges, ...newEdges ],
                              pageInfo
                            }
                          }
                        }
                      : previousResult
                  }
                })
              }} >
      { (!queryAccountsData.accounts.edges.length) ? 
        t('schedule.classes.class.attendance.search_result_empty') : 
        <Table>
          <Table.Header>
            <Table.Row key={v4()}>
              <Table.ColHeader>{t('general.name')}</Table.ColHeader>
              <Table.ColHeader>{t('general.email')}</Table.ColHeader>
              <Table.ColHeader></Table.ColHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {queryAccountsData.accounts.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col key={v4()}>
                  {node.fullName}
                </Table.Col>
                <Table.Col key={v4()}>
                  {node.email}
                </Table.Col>
                <Table.Col key={v4()}>
                  {(accountIdsWithTickets.includes(node.id)) ? 
                    <span className="pull-right">{t("schedule.events.tickets.customers.search_results_already_bought")}</span> :
                    <Button 
                      onClick={() =>
                        addAccountScheduleEventTicket({ variables: {
                          input: {
                            account: node.id,
                            scheduleEventTicket: id
                          }                            
                        }, refetchQueries: [
                            {query: GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY, variables: {
                              scheduleEventTicket: id
                            }},
                        ]})
                        .then(({ data }) => {
                            console.log('got data', data);
                            toast.success((t('schedule.events.tickets.customers.toast_add_success')), {
                                position: toast.POSITION.BOTTOM_RIGHT
                              })
                            setShowSearch(false)
                          }).catch((error) => {
                            toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                position: toast.POSITION.BOTTOM_RIGHT
                              })
                            console.log('there was an error sending the query', error)
                            setShowSearch(false)
                          })
                      }
                    >
                      {t("general.add")}
                    </Button>
                    // <Link to={"/schedule/classes/class/book/" + schedule_item_id + "/" + class_date + "/" + node.id}>
                    //   <Button color="secondary pull-right">
                    //     {t('general.checkin')} <Icon name="chevron-right" />
                    //   </Button>
                    // </Link>       
                  }   
                </Table.Col>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      }
    </ContentCard>
    : ""

  // Empty list
  // if (!accountScheduleEventTickets.edges.length) {
  //   <ScheduleEventTicketEditBase 
  //     sidebarContent={sidebarContent} 
  //     activeTab={activeTab} 
  //     activeLink={activeLink} 
  //     returnUrl={returnUrl}
  //     pageHeaderOptions={pageHeaderOptions}
  //     SearchResults={searchResults}
  //   >
  //     <Card.Body>
  //       <Table>
  //         <Table.Header>
  //           <Table.Row>
  //             <Table.ColHeader>{t('general.name')}</Table.ColHeader>
  //             <Table.ColHeader>{t('general.included')}</Table.ColHeader>
  //           </Table.Row>
  //         </Table.Header>
  //         <Table.Body>
  //           {accountScheduleEventTickets.edges.map(({ node }) => (
  //             <Table.Row key={v4()}>
  //               <Table.Col>
  //                 {node.scheduleItem.name}
  //               </Table.Col>  
  //             </Table.Row>
  //           ))}
  //         </Table.Body>
  //       </Table>
  //     </Card.Body>
  //   </ScheduleEventTicketEditBase>
  // }

  // Data
  return (
    <ScheduleEventTicketEditBase 
      sidebarContent={sidebarContent} 
      activeTab={activeTab} 
      activeLink={activeLink} 
      returnUrl={returnUrl}
      pageHeaderOptions={pageHeaderOptions}
      searchResults={searchResults}
    >
      <Card.Body>
        <Table>
          <Table.Header>
            <Table.Row>
              <Table.ColHeader>{t('general.name')}</Table.ColHeader>
              <Table.ColHeader>{t('general.invoice')}</Table.ColHeader>
              <Table.ColHeader>{t('schedule.events.tickets.info_mail_sent')}</Table.ColHeader> 
              <Table.ColHeader></Table.ColHeader> 
              <Table.ColHeader></Table.ColHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {accountScheduleEventTickets.edges.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col>
                  {node.account.fullName} <br />
                  {(node.cancelled) ? <Badge color="warning">{t("general.cancelled")}</Badge> : ""}
                </Table.Col>  
                <Table.Col>

                </Table.Col>
                <Table.Col>
                  <BadgeBoolean value={node.infoMailSent} /> <br />
                  {/* TODO: resend link here */}
                </Table.Col>
                <Table.Col>
                  {(node.cancelled) ?
                    <Button 
                      className="pull-right"
                      color="warning"
                      onClick={() =>
                        updateAccountScheduleEventTicket({ variables: {
                          input: {
                            id: node.id,
                            cancelled: false
                          }
                        }, refetchQueries: [
                            {query: GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY, variables: {
                              scheduleEventTicket: id
                            }},
                        ]})
                        .then(({ data }) => {
                            console.log('got data', data);
                            toast.success((t('schedule.events.tickets.customers.uncancelled')), {
                                position: toast.POSITION.BOTTOM_RIGHT
                              })
                            setShowSearch(false)
                          }).catch((error) => {
                            toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                position: toast.POSITION.BOTTOM_RIGHT
                              })
                            console.log('there was an error sending the query', error)
                            setShowSearch(false)
                          }
                        )
                      }
                    >
                      {t("general.uncancel")}
                    </Button>
                  :
                    <Button 
                      className="pull-right"
                      color="warning"
                      onClick={() =>
                        updateAccountScheduleEventTicket({ variables: {
                          input: {
                            id: node.id,
                            cancelled: true
                          }
                        }, refetchQueries: [
                            {query: GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY, variables: {
                              scheduleEventTicket: id
                            }},
                        ]})
                        .then(({ data }) => {
                            console.log('got data', data);
                            toast.success((t('schedule.events.tickets.customers.cancelled')), {
                                position: toast.POSITION.BOTTOM_RIGHT
                              })
                            setShowSearch(false)
                          }).catch((error) => {
                            toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                position: toast.POSITION.BOTTOM_RIGHT
                              })
                            console.log('there was an error sending the query', error)
                            setShowSearch(false)
                          })
                        }
                      >
                        {t("general.cancel")}
                      </Button>
                  }
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