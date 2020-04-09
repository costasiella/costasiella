// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import {
  Page,
  Grid,
  Icon,
  Dimmer,
  Badge,
  Button,
  Card,
  Container,
  Table, 
  Text
} from "tabler-react";
import HasPermissionWrapper from "../../HasPermissionWrapper"
// import { confirmAlert } from 'react-confirm-alert'; // Import
import { toast } from 'react-toastify'

import { get_list_query_variables } from "./tools"
import ContentCard from "../../general/ContentCard"
import FinanceOrdersBase from './FinanceOrdersBase'
import FinanceOrderStatus from "./FinanceOrderStatus"
import FinanceOrderDelete from "./FinanceOrderDelete"

import { GET_ORDERS_QUERY, DELETE_FINANCE_ORDER } from "./queries"

import confirm_delete from "../../../tools/confirm_delete"
import moment from 'moment'



function FinanceOrders({t, match, history}) {
  const title = t("shop.home.title")
  const { loading, error, data, refetch, fetchMore } = useQuery(GET_ORDERS_QUERY, {
    variables: {get_list_query_variables},
    pollInterval: 2000
  })

  if (loading) return (
    <FinanceOrdersBase title={title}>
      {t("general.loading_with_dots")}
    </FinanceOrdersBase>
  )

  if (error) return (
    <FinanceOrdersBase title={title}>
      {t("finance.orders.error_loading")}
    </FinanceOrdersBase>
  )

  console.log(data)
  const orders = data.financeOrders
  console.log(orders)

  // Empty list
  if (!orders.edges.length) { return (
    <FinanceOrdersBase refetch={refetch}>
      <ContentCard cardTitle={t('finance.orders.title')}>
        <p>
          {t('finance.orders.empty_list')}
        </p>
      </ContentCard>
    </FinanceOrdersBase>
  )}

  return (
    <FinanceOrdersBase title={title} refetch={refetch}>
      <ContentCard 
        cardTitle={t('finance.orders.title')} 
        pageInfo={orders.pageInfo}
        onLoadMore={() => {
          fetchMore({
            variables: {
              after: orders.pageInfo.endCursor
            },
            updateQuery: (previousResult, { fetchMoreResult }) => {
              const newEdges = fetchMoreResult.financeOrders.edges
              const pageInfo = fetchMoreResult.financeOrders.pageInfo

              return newEdges.length
                ? {
                    // Put the new invoices at the end of the list and update `pageInfo`
                    // so we have the new `endCursor` and `hasNextPage` values
                    financeOrders: {
                      __typename: previousResult.financeOrders.__typename,
                      edges: [ ...previousResult.financeOrders.edges, ...newEdges ],
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
              <Table.ColHeader>{t('general.status')}</Table.ColHeader>
              <Table.ColHeader>{t('finance.orders.order_number')}</Table.ColHeader>
              <Table.ColHeader>{t('finance.orders.relation')}</Table.ColHeader>
              <Table.ColHeader>{t('finance.orders.date')}</Table.ColHeader>
              <Table.ColHeader>{t('general.total')}</Table.ColHeader>
              <Table.ColHeader></Table.ColHeader>
              <Table.ColHeader></Table.ColHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
              {orders.edges.map(({ node }) => (        
                <Table.Row key={v4()}>
                  <Table.Col key={v4()}>
                    <FinanceOrderStatus status={node.status} />
                  </Table.Col>
                  <Table.Col key={v4()}>
                    # {node.orderNumber}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    {node.account.fullName}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    {moment(node.createdAt).format('LL')}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    {node.totalDisplay}
                  </Table.Col>
                  <Table.Col key={v4()}>
                    Edit
                  </Table.Col>
                  <Table.Col key={v4()}>
                    <FinanceOrderDelete node={node}/>
                  </Table.Col>
                </Table.Row>
              ))}
          </Table.Body>
        </Table>
      </ContentCard>
    </FinanceOrdersBase>
  )
}



// const FinanceOrders = ({ t, history }) => (
//   <SiteWrapper>
//     <div className="my-3 my-md-5">
//       <Container>
//         <Page.Header title={t("finance.title")}>
//           <div className="page-options d-flex">
//           </div>
//         </Page.Header>
//             <Query query={GET_ORDERS_QUERY} variables={get_list_query_variables()} pollInterval={2000}>
//              {({ loading, error, data: {financeOrders: orders}, refetch, fetchMore }) => {
//                 // Loading
//                 if (loading) return (
//                   <FinanceInvoicesBase refetch={refetch}>
//                     <ContentCard cardTitle={t('finance.invoices.title')}>
//                       <Dimmer active={true}
//                               loader={true}>
//                       </Dimmer>
//                     </ContentCard>
//                   </FinanceInvoicesBase>
//                 )
//                 // Error
//                 if (error) return (
//                   <FinanceInvoicesBase refetch={refetch}>
//                     <ContentCard cardTitle={t('finance.invoices.title')}>
//                       <p>{t('finance.invoices.error_loading')}</p>
//                     </ContentCard>
//                   </FinanceInvoicesBase>
//                 )
                
//                 // Empty list
//                 if (!invoices.edges.length) { return (
//                   <FinanceInvoicesBase refetch={refetch}>
//                     <ContentCard cardTitle={t('finance.invoices.title')}>
//                       <p>
//                         {t('finance.invoices.empty_list')}
//                       </p>
//                     </ContentCard>
//                   </FinanceInvoicesBase>
//                 )} else {   
//                 // Life's good! :)
//                 return (
//                   <FinanceInvoicesBase refetch={refetch}>
//                     <ContentCard cardTitle={t('finance.invoices.title')}
//                                 pageInfo={invoices.pageInfo}
//                                 onLoadMore={() => {
//                                   fetchMore({
//                                     variables: {
//                                       after: invoices.pageInfo.endCursor
//                                     },
//                                     updateQuery: (previousResult, { fetchMoreResult }) => {
//                                       const newEdges = fetchMoreResult.financeInvoices.edges
//                                       const pageInfo = fetchMoreResult.financeInvoices.pageInfo

//                                       return newEdges.length
//                                         ? {
//                                             // Put the new invoices at the end of the list and update `pageInfo`
//                                             // so we have the new `endCursor` and `hasNextPage` values
//                                             financeInvoices: {
//                                               __typename: previousResult.financeInvoices.__typename,
//                                               edges: [ ...previousResult.financeInvoices.edges, ...newEdges ],
//                                               pageInfo
//                                             }
//                                           }
//                                         : previousResult
//                                     }
//                                   })
//                                 }} 
//                       >
//                       <Table>
//                         <Table.Header>
//                           <Table.Row key={v4()}>
//                             <Table.ColHeader>{t('general.status')}</Table.ColHeader>
//                             <Table.ColHeader>{t('finance.invoices.invoice_number')}</Table.ColHeader>
//                             <Table.ColHeader>{t('finance.invoices.relation')} & {t('finance.invoices.summary')}</Table.ColHeader>
//                             <Table.ColHeader>{t('finance.invoices.date')} & {t('finance.invoices.due')}</Table.ColHeader>
//                             {/* <Table.ColHeader>{t('finance.invoices.due')}</Table.ColHeader> */}
//                             <Table.ColHeader>{t('general.total')}</Table.ColHeader>
//                             <Table.ColHeader>{t('general.balance')}</Table.ColHeader>
//                             <Table.ColHeader></Table.ColHeader>
//                             <Table.ColHeader></Table.ColHeader>
//                           </Table.Row>
//                         </Table.Header>
//                         <Table.Body>
//                             {invoices.edges.map(({ node }) => (
//                               <Table.Row key={v4()}>
//                                 <Table.Col key={v4()}>
//                                   <FinanceInvoicesStatus status={node.status} />
//                                 </Table.Col>
//                                 <Table.Col key={v4()}>
//                                   {node.invoiceNumber}
//                                 </Table.Col>
//                                 <Table.Col key={v4()}>
//                                   {(node.account) ? 
//                                     <Link to={"/relations/accounts/" + node.account.id + "/profile"}>
//                                       {(node.relationCompany) ? node.relationCompany: node.relationContactName}
//                                     </Link> :
//                                     (node.relationCompany) ? node.relationCompany: node.relationContactName
//                                   }
//                                    <br />
//                                   <Text.Small color="gray">{node.summary.trunc(20)}</Text.Small>
//                                 </Table.Col>
//                                 <Table.Col key={v4()}>
//                                   {moment(node.dateSent).format('LL')} <br />
//                                   {moment(node.dateDue).format('LL')}
//                                 </Table.Col>
//                                 <Table.Col key={v4()}>
//                                   {node.totalDisplay}
//                                 </Table.Col>
//                                 <Table.Col key={v4()}>
//                                   {node.balanceDisplay}
//                                 </Table.Col>
//                                 <Table.Col className="text-right" key={v4()}>
//                                   <Button className='btn-sm' 
//                                           onClick={() => history.push("/finance/invoices/edit/" + node.id)}
//                                           color="secondary">
//                                     {t('general.edit')}
//                                   </Button>
//                                 </Table.Col>
//                                 <Mutation mutation={DELETE_FINANCE_INVOICE} key={v4()}>
//                                   {(deleteFinanceInvoice, { data }) => (
//                                     <Table.Col className="text-right" key={v4()}>
//                                       <button className="icon btn btn-link btn-sm" 
//                                         title={t('general.delete')} 
//                                         href=""
//                                         onClick={() => {
//                                           confirm_delete({
//                                             t: t,
//                                             msgConfirm: t("finance.invoices.delete_confirm_msg"),
//                                             msgDescription: <p>{node.invoiceNumber}</p>,
//                                             msgSuccess: t('finance.invoices.deleted'),
//                                             deleteFunction: deleteFinanceInvoice,
//                                             functionVariables: { 
//                                               variables: {
//                                                 input: {
//                                                   id: node.id
//                                                 }
//                                               }, 
//                                               refetchQueries: [
//                                                 {query: GET_INVOICES_QUERY, variables: get_list_query_variables() } 
//                                               ]
//                                             }
//                                           })
//                                       }}>
//                                         <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
//                                       </button>
//                                    </Table.Col>
//                                   )}
//                                </Mutation>
//                               </Table.Row>
//                             ))}
//                         </Table.Body>
//                       </Table>
//                     </ContentCard>
//                   </FinanceInvoicesBase>
//                 )}}
//                }
//             </Query>
//       </Container>
//     </div>
//   </SiteWrapper>
// );

export default withTranslation()(withRouter(FinanceOrders))