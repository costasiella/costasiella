// @flow

import React, { useContext } from 'react'
import { useQuery, useMutation } from '@apollo/react-hooks'
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import moment from 'moment'

import {
  Badge,
  Button,
  Table
} from "tabler-react";
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import { toast } from 'react-toastify'

import AppSettingsContext from '../../../context/AppSettingsContext'
import BadgeBoolean from "../../../ui/BadgeBoolean"
import RelationsAccountsBack from "../RelationsAccountsBack"

import ContentCard from "../../../general/ContentCard"
import FinanceInvoicesStatus from "../../../ui/FinanceInvoiceStatus"

import AccountScheduleEventTicketsBase from "./AccountScheduleEventTicketsBase"


import { UPDATE_ACCOUNT_SCHEDULE_EVENT_TICKET } from "../../../schedule/events/tickets/customers/queries"
import { GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY } from "./queries"



function AccountScheduleEventTickets({t, history, match}) {
  // const title = t("relations.account.event_tickets.title")
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment

  const accountId = match.params.account_id
  const { loading, error, data, fetchMore } = useQuery(GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY, { variables: {
    accountId: accountId
  }})
  const [updateAccountScheduleEventTicket] = useMutation(UPDATE_ACCOUNT_SCHEDULE_EVENT_TICKET)


  if (loading) return (
    <AccountScheduleEventTicketsBase>
      {t("general.loading_with_dots")}
    </AccountScheduleEventTicketsBase>
  )
  if (error) return (
    <AccountScheduleEventTicketsBase>
      {t("shop.classpasses.error_loading")}
    </AccountScheduleEventTicketsBase>
  )

  console.log(data)
  const accountScheduleEventTickets = data.accountScheduleEventTickets
  console.log(accountScheduleEventTickets)


  return (
    <AccountScheduleEventTicketsBase>
      <ContentCard 
        cardTitle={t('relations.account.event_tickets.title')}
        pageInfo={accountScheduleEventTickets.pageInfo}
        onLoadMore={() => {
          fetchMore({
            variables: {
              after: accountScheduleEventTickets.pageInfo.endCursor
            },
            updateQuery: (previousResult, { fetchMoreResult }) => {
              const newEdges = fetchMoreResult.accountScheduleEventTickets.edges
              const pageInfo = fetchMoreResult.accountScheduleEventTickets.pageInfo

              return newEdges.length
                ? {
                    // Put the new accountScheduleEventTickets at the end of the list and update `pageInfo`
                    // so we have the new `endCursor` and `hasNextPage` values
                    accountScheduleEventTickets: {
                      __typename: previousResult.accountScheduleEventTickets.__typename,
                      edges: [ ...previousResult.accountScheduleEventTickets.edges, ...newEdges ],
                      pageInfo
                    }
                  }
                : previousResult
            }
          })
        }} 
      >
        <Table>
          <Table.Header>
            <Table.Row key={v4()}>
              <Table.ColHeader>{t('general.ticket')}</Table.ColHeader>
              <Table.ColHeader>{t('general.start')}</Table.ColHeader>
              <Table.ColHeader>{t('general.invoice')}</Table.ColHeader>
              <Table.ColHeader>{t('schedule.events.tickets.info_mail_sent')}</Table.ColHeader>
              <Table.ColHeader></Table.ColHeader> 
            </Table.Row>
          </Table.Header>
          <Table.Body>
              {accountScheduleEventTickets.edges.map(({ node }) => (
                <Table.Row key={v4()}>
                  <Table.Col key={v4()}>
                    {node.scheduleEventTicket.scheduleEvent.name} <br />
                    <Badge>{node.scheduleEventTicket.name}</Badge> {" "}
                    {(node.cancelled) ? <Badge color="warning">{t("general.cancelled")}</Badge> : ""}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    {moment(node.scheduleEventTicket.scheduleEvent.dateStart).format(dateFormat)}
                  </Table.Col>
                  <Table.Col>
                    {(node.invoiceItems.edges.length) ? 
                      <span>
                        <Link to={`/finance/invoices/edit/${node.invoiceItems.edges[0].node.financeInvoice.id}`}>
                          {node.invoiceItems.edges[0].node.financeInvoice.invoiceNumber}
                        </Link> <br />
                        <FinanceInvoicesStatus status={node.invoiceItems.edges[0].node.financeInvoice.status} />
                        
                      </span>
                      : ""
                    }
                    
                  </Table.Col>
                  {/* <Table.Col key={v4()}>
                    {node.dateStart}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    {node.dateEnd}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    {node.classesRemainingDisplay}
                  </Table.Col>
                  <Table.Col className="text-right" key={v4()}>
                    <Link to={"/relations/accounts/" + match.params.account_id + "/classpasses/edit/" + node.id}>
                      <Button className='btn-sm' 
                              color="secondary">
                        {t('general.edit')}
                      </Button>
                    </Link>
                  </Table.Col> */}
                  <Table.Col>
                    <BadgeBoolean value={node.infoMailSent} />
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
                            { 
                              query: GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY, 
                              variables: { accountId: accountId }
                            },
                          ]})
                          .then(({ data }) => {
                              console.log('got data', data);
                              toast.success((t('schedule.events.tickets.customers.uncancelled')), {
                                  position: toast.POSITION.BOTTOM_RIGHT
                                })
                            }).catch((error) => {
                              toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                  position: toast.POSITION.BOTTOM_RIGHT
                                })
                              console.log('there was an error sending the query', error)
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
                              { 
                                query: GET_ACCOUNT_SCHEDULE_EVENT_TICKETS_QUERY, 
                                variables: { accountId: accountId }
                              },
                          ]})
                          .then(({ data }) => {
                              console.log('got data', data);
                              toast.success((t('schedule.events.tickets.customers.cancelled')), {
                                  position: toast.POSITION.BOTTOM_RIGHT
                                })
                            }).catch((error) => {
                              toast.error((t('general.toast_server_error')) + ': ' +  error, {
                                  position: toast.POSITION.BOTTOM_RIGHT
                                })
                              console.log('there was an error sending the query', error)
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
      </ContentCard>
    </AccountScheduleEventTicketsBase>
  )
}



// const AccountClasspasses = ({ t, history, match, archived=false }) => (
//   <SiteWrapper>
//     <div className="my-3 my-md-5">
//       <Query query={GET_ACCOUNT_CLASSPASSES_QUERY} variables={{ archived: archived, accountId: match.params.account_id }} 
//         fetchPolicy="network-only"> 
//         {({ loading, error, data, refetch, fetchMore }) => {
//           // Loading
//           if (loading) return <p>{t('general.loading_with_dots')}</p>
//           // Error
//           if (error) {
//             console.log(error)
//             return <p>{t('general.error_sad_smiley')}</p>
//           }

//           const account = data.account
//           const accountClasspasses = data.accountClasspasses

//           return (
//             <Container>
//               <Page.Header title={account.firstName + " " + account.lastName} >
//                 <RelationsAccountsBack />
//               </Page.Header>
//               <Grid.Row>
//                 <Grid.Col md={9}>
//                   <ContentCard 
//                     cardTitle={t('relations.account.classpasses.title')}
//                     pageInfo={accountClasspasses.pageInfo}
//                     onLoadMore={() => {
//                       fetchMore({
//                         variables: {
//                           after: accountClasspasses.pageInfo.endCursor
//                         },
//                         updateQuery: (previousResult, { fetchMoreResult }) => {
//                           const newEdges = fetchMoreResult.accountClasspasses.edges
//                           const pageInfo = fetchMoreResult.accountClasspasses.pageInfo

//                           return newEdges.length
//                             ? {
//                                 // Put the new accountClasspasses at the end of the list and update `pageInfo`
//                                 // so we have the new `endCursor` and `hasNextPage` values
//                                 accountClasspasses: {
//                                   __typename: previousResult.accountClasspasses.__typename,
//                                   edges: [ ...previousResult.accountClasspasses.edges, ...newEdges ],
//                                   pageInfo
//                                 }
//                               }
//                             : previousResult
//                         }
//                       })
//                     }} 
//                   >
//                     <Table>
//                       <Table.Header>
//                         <Table.Row key={v4()}>
//                           <Table.ColHeader>{t('general.name')}</Table.ColHeader>
//                           <Table.ColHeader>{t('general.date_start')}</Table.ColHeader>
//                           <Table.ColHeader>{t('general.date_end')}</Table.ColHeader>
//                           <Table.ColHeader>{t('general.classes_remaining')}</Table.ColHeader>
//                           <Table.ColHeader></Table.ColHeader> 
//                         </Table.Row>
//                       </Table.Header>
//                       <Table.Body>
//                           {accountClasspasses.edges.map(({ node }) => (
//                             <Table.Row key={v4()}>
//                               <Table.Col key={v4()}>
//                                 {node.organizationClasspass.name}
//                               </Table.Col>
//                               <Table.Col key={v4()}>
//                                 {node.dateStart}
//                               </Table.Col>
//                               <Table.Col key={v4()}>
//                                 {node.dateEnd}
//                               </Table.Col>
//                               <Table.Col key={v4()}>
//                                 {node.classesRemainingDisplay}
//                               </Table.Col>
//                               <Table.Col className="text-right" key={v4()}>
//                                 <Link to={"/relations/accounts/" + match.params.account_id + "/classpasses/edit/" + node.id}>
//                                   <Button className='btn-sm' 
//                                           color="secondary">
//                                     {t('general.edit')}
//                                   </Button>
//                                 </Link>
//                               </Table.Col>
//                               <Mutation mutation={DELETE_ACCOUNT_CLASSPASS} key={v4()}>
//                                 {(deleteAccountClasspass, { data }) => (
//                                   <Table.Col className="text-right" key={v4()}>
//                                     <button className="icon btn btn-link btn-sm" 
//                                       title={t('general.delete')} 
//                                       href=""
//                                       onClick={() => {
//                                         confirm_delete({
//                                           t: t,
//                                           msgConfirm: t("relations.account.classpasses.delete_confirm_msg"),
//                                           msgDescription: <p>{node.organizationClasspass.name} {node.dateStart}</p>,
//                                           msgSuccess: t('relations.account.classpasses.deleted'),
//                                           deleteFunction: deleteAccountClasspass,
//                                           functionVariables: { variables: {
//                                             input: {
//                                               id: node.id
//                                             }
//                                           }, refetchQueries: [
//                                             {query: GET_ACCOUNT_CLASSPASSES_QUERY, variables: { archived: archived, accountId: match.params.account_id }} 
//                                           ]}
//                                         })
//                                     }}>
//                                       <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
//                                     </button>
//                                   </Table.Col>
//                                 )}
//                               </Mutation>
//                             </Table.Row>
//                           ))}
//                       </Table.Body>
//                     </Table>
//                   </ContentCard>
//                 </Grid.Col>
//                 <Grid.Col md={3}>
//                   <ProfileCardSmall user={account}/>
//                   <HasPermissionWrapper permission="add"
//                                         resource="accountclasspass">
//                     <Link to={"/relations/accounts/" + match.params.account_id + "/classpasses/add"}>
//                       <Button color="primary btn-block mb-6">
//                               {/* //  onClick={() => history.push("/organization/classpasses/add")}> */}
//                         <Icon prefix="fe" name="plus-circle" /> {t('relations.account.classpasses.add')}
//                       </Button>
//                     </Link>
//                   </HasPermissionWrapper>
//                   <ProfileMenu 
//                     active_link='classpasses' 
//                     account_id={match.params.account_id}
//                   />
//                 </Grid.Col>
//               </Grid.Row>
//             </Container>
//           )
//         }}
//       </Query>
//     </div>
//   </SiteWrapper>
// )
      
        
export default withTranslation()(withRouter(AccountScheduleEventTickets))