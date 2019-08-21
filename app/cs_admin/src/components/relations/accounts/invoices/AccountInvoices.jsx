// @flow

import React from 'react'
import { Mutation } from 'react-apollo'
import { useQuery } from '@apollo/react-hooks'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import moment from 'moment'

import {
  Page,
  Grid,
  Icon,
  Dimmer,
  Button,
  Card,
  Container,
  Table,
  Text
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import { toast } from 'react-toastify'

import BadgeBoolean from "../../../ui/BadgeBoolean"
import RelationsAccountsBack from "../RelationsAccountsBack"
import confirm_delete from "../../../../tools/confirm_delete"

import ContentCard from "../../../general/ContentCard"
import ProfileMenu from "../ProfileMenu"
import ProfileCardSmall from "../../../ui/ProfileCardSmall"

import { GET_ACCOUNT_INVOICES_QUERY } from "./queries"
import { DELETE_FINANCE_INVOICE } from "../../../finance/invoices/queries"
import FinanceInvoiceStatus from "../../../finance/invoices/FinanceInvoiceStatus"


function AccountInvoices({ t, match, history }) {
  const account_id = match.params.account_id
  const { loading, error, data, fetchMore } = useQuery(GET_ACCOUNT_INVOICES_QUERY, {
    variables: {'account': account_id},
    pollInterval: 2000
  })

  // Loading
  if (loading) return <p>{t('general.loading_with_dots')}</p>
  // Error
  if (error) {
    console.log(error)
    return <p>{t('general.error_sad_smiley')}</p>
  }

  let financeInvoices = data.financeInvoices
  const account = data.account
  
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={account.firstName + " " + account.lastName} >
            <RelationsAccountsBack />
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={9}>
              <ContentCard 
                cardTitle={t('relations.account.invoices.title')}
                pageInfo={financeInvoices.pageInfo}
                onLoadMore={() => {
                  fetchMore({
                    variables: {
                      after: financeInvoices.pageInfo.endCursor
                    },
                    updateQuery: (previousResult, { fetchMoreResult }) => {
                      const newEdges = fetchMoreResult.financeInvoices.edges
                      const pageInfo = fetchMoreResult.financeInvoices.pageInfo

                      return newEdges.length
                        ? {
                            // Put the new financeInvoices at the end of the list and update `pageInfo`
                            // so we have the new `endCursor` and `hasNextPage` values
                            financeInvoices: {
                              __typename: previousResult.financeInvoices.__typename,
                              edges: [ ...previousResult.financeInvoices.edges, ...newEdges ],
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
                      <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                      <Table.ColHeader>{t('finance.invoices.invoice_number')} & {t('finance.invoices.summary')}</Table.ColHeader>
                      <Table.ColHeader>{t('finance.invoices.date')} & {t('finance.invoices.due')}</Table.ColHeader>
                      <Table.ColHeader>{t('general.total')}</Table.ColHeader>
                      <Table.ColHeader>{t('general.balance')}</Table.ColHeader>
                      <Table.ColHeader></Table.ColHeader>
                      <Table.ColHeader></Table.ColHeader>
                    </Table.Row>
                  </Table.Header>
                  <Table.Body>
                      {financeInvoices.edges.map(({ node }) => (
                        <Table.Row key={v4()}>
                          <Table.Col key={v4()}>
                            <FinanceInvoiceStatus status={node.status} />
                          </Table.Col>
                          <Table.Col key={v4()}>
                            {node.invoiceNumber} <br />
                            <Text.Small color="gray">{node.summary.trunc(35)}</Text.Small>
                          </Table.Col>
                          <Table.Col key={v4()}>
                            {moment(node.dateSent).format('LL')} <br />
                            {moment(node.dateDue).format('LL')}
                          </Table.Col>
                          <Table.Col key={v4()}>
                            {node.totalDisplay}
                          </Table.Col>
                          <Table.Col key={v4()}>
                            {node.balanceDisplay}
                          </Table.Col>
                          <Table.Col className="text-right" key={v4()}>
                            <Button className='btn-sm' 
                                    onClick={() => history.push("/finance/invoices/edit/" + node.id)}
                                    color="secondary">
                              {t('general.edit')}
                            </Button>
                          </Table.Col>
                          <Mutation mutation={DELETE_FINANCE_INVOICE} key={v4()}>
                            {(deleteFinanceInvoice, { data }) => (
                              <Table.Col className="text-right" key={v4()}>
                                <button className="icon btn btn-link btn-sm" 
                                  title={t('general.delete')} 
                                  href=""
                                  onClick={() => {
                                    confirm_delete({
                                      t: t,
                                      msgConfirm: t("finance.invoices.delete_confirm_msg"),
                                      msgDescription: <p>{node.invoiceNumber}</p>,
                                      msgSuccess: t('finance.invoices.deleted'),
                                      deleteFunction: deleteFinanceInvoice,
                                      functionVariables: { 
                                        variables: {
                                          input: {
                                            id: node.id
                                          }
                                        }, 
                                        refetchQueries: [
                                          {query: GET_ACCOUNT_INVOICES_QUERY, variables: {'account': account_id}},
                                        ]
                                      }
                                    })
                                }}>
                                  <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
                                </button>
                              </Table.Col>
                            )}
                          </Mutation>
                        </Table.Row>
                      ))}
                  </Table.Body>
                </Table>
              </ContentCard>
            </Grid.Col>
            <Grid.Col md={3}>
              <ProfileCardSmall user={account}/>
                <HasPermissionWrapper permission="add"
                                      resource="financeinvoice">
                  <Link to={"/relations/accounts/" + match.params.account_id + "/invoices/add"}>
                    <Button color="primary btn-block mb-6">
                            {/* //  onClick={() => history.push("/organization/invoices/add")}> */}
                      <Icon prefix="fe" name="plus-circle" /> {t('relations.account.invoices.add')}
                    </Button>
                  </Link>
                </HasPermissionWrapper>
              <ProfileMenu 
                active_link='invoices' 
                account_id={match.params.account_id}
              />
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(AccountInvoices))


// const AccountSubscriptions = ({ t, history, match, archived=false }) => (
//   <SiteWrapper>
//     <div className="my-3 my-md-5">
//       <Query query={GET_ACCOUNT_SUBSCRIPTIONS_QUERY} variables={{ accountId: match.params.account_id }}> 
//         {({ loading, error, data, refetch, fetchMore }) => {
//           // Loading
//           if (loading) return <p>{t('general.loading_with_dots')}</p>
//           // Error
//           if (error) {
//             console.log(error)
//             return <p>{t('general.error_sad_smiley')}</p>
//           }

//           const account = data.account
//           const financeInvoices = data.financeInvoices

//           return (
//             <Container>
//               <Page.Header title={account.firstName + " " + account.lastName} >
//                 <RelationsAccountsBack />
//               </Page.Header>
//               <Grid.Row>
//                 <Grid.Col md={9}>
//                   <ContentCard 
//                     cardTitle={t('relations.account.invoices.title')}
//                     pageInfo={financeInvoices.pageInfo}
//                     onLoadMore={() => {
//                       fetchMore({
//                         variables: {
//                           after: financeInvoices.pageInfo.endCursor
//                         },
//                         updateQuery: (previousResult, { fetchMoreResult }) => {
//                           const newEdges = fetchMoreResult.financeInvoices.edges
//                           const pageInfo = fetchMoreResult.financeInvoices.pageInfo

//                           return newEdges.length
//                             ? {
//                                 // Put the new financeInvoices at the end of the list and update `pageInfo`
//                                 // so we have the new `endCursor` and `hasNextPage` values
//                                 financeInvoices: {
//                                   __typename: previousResult.financeInvoices.__typename,
//                                   edges: [ ...previousResult.financeInvoices.edges, ...newEdges ],
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
//                           <Table.ColHeader>{t('general.payment_method')}</Table.ColHeader>
//                           <Table.ColHeader></Table.ColHeader> 
//                         </Table.Row>
//                       </Table.Header>
//                       <Table.Body>
//                           {financeInvoices.edges.map(({ node }) => (
//                             <Table.Row key={v4()}>
//                               <Table.Col key={v4()}>
//                                 {node.organizationSubscription.name}
//                               </Table.Col>
//                               <Table.Col key={v4()}>
//                                 {node.dateStart}
//                               </Table.Col>
//                               <Table.Col key={v4()}>
//                                 {node.dateEnd}
//                               </Table.Col>
//                               <Table.Col key={v4()}>
//                                 {(node.financePaymentMethod) ? node.financePaymentMethod.name : ""}
//                               </Table.Col>
//                               <Table.Col className="text-right" key={v4()}>
//                                 <Link to={"/relations/accounts/" + match.params.account_id + "/invoices/edit/" + node.id}>
//                                   <Button className='btn-sm' 
//                                           color="secondary">
//                                     {t('general.edit')}
//                                   </Button>
//                                 </Link>
//                               </Table.Col>
//                               <Mutation mutation={DELETE_ACCOUNT_SUBSCRIPTION} key={v4()}>
//                                 {(deleteAccountSubscription, { data }) => (
//                                   <Table.Col className="text-right" key={v4()}>
//                                     <button className="icon btn btn-link btn-sm" 
//                                       title={t('general.delete')} 
//                                       href=""
//                                       onClick={() => {
//                                         confirm_delete({
//                                           t: t,
//                                           msgConfirm: t("relations.account.invoices.delete_confirm_msg"),
//                                           msgDescription: <p>{node.organizationSubscription.name} {node.dateStart}</p>,
//                                           msgSuccess: t('relations.account.invoices.deleted'),
//                                           deleteFunction: deleteAccountSubscription,
//                                           functionVariables: { variables: {
//                                             input: {
//                                               id: node.id
//                                             }
//                                           }, refetchQueries: [
//                                             {query: GET_ACCOUNT_SUBSCRIPTIONS_QUERY, variables: { archived: archived, accountId: match.params.account_id }} 
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
//                                         resource="accountsubscription">
//                     <Link to={"/relations/accounts/" + match.params.account_id + "/invoices/add"}>
//                       <Button color="primary btn-block mb-6">
//                               {/* //  onClick={() => history.push("/organization/invoices/add")}> */}
//                         <Icon prefix="fe" name="plus-circle" /> {t('relations.account.invoices.add')}
//                       </Button>
//                     </Link>
//                   </HasPermissionWrapper>
//                   <ProfileMenu 
//                     active_link='invoices' 
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
      
        
// export default withTranslation()(withRouter(AccountSubscriptions))