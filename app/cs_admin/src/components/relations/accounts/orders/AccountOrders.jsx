// @flow

import React, { useContext } from 'react'
import { useQuery } from "react-apollo"
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'
import moment from 'moment'

import AppSettingsContext from '../../../context/AppSettingsContext'
import FinanceOrderStatus from "../../../finance/orders/FinanceOrderStatus"

import {
  Button,
  Table
} from "tabler-react";
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import BadgeBookingStatus from "../../../ui/BadgeBookingStatus"

import ContentCard from "../../../general/ContentCard"
import AccountOrdersBase from "./AccountOrdersBase"
import AccountOrderDelete from "./AccountOrderDelete"

import { GET_ACCOUNT_ORDERS_QUERY } from "./queries"


function AccountOrders({ t, match, history }) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  // const timeFormat = appSettings.timeFormatMoment
  const account_id = match.params.account_id
  const { loading, error, data, fetchMore } = useQuery(GET_ACCOUNT_ORDERS_QUERY, {
    variables: {'account': account_id},
  })

  // Loading
  if (loading) return (
    <AccountOrdersBase>
      <p>{t('general.loading_with_dots')}</p>
    </AccountOrdersBase>
  )
  // Error
  if (error) {
    console.log(error)
    return (
      <AccountOrdersBase>
        <p>{t('general.error_sad_smiley')}</p>
      </AccountOrdersBase>
    )
  }

  console.log("AccountClasses data:")
  console.log(data)
  const account = data.account
  const financeOrders = data.financeOrders
  
  // Empty list
  if (!financeOrders.edges.length) {
    return (
      <AccountOrdersBase account={account}>
        <p>{t('relations.account.orders.empty_list')}</p>
      </AccountOrdersBase>
    )
  }

  // Return populated list
  return (
    <AccountOrdersBase account={account}>
      <ContentCard 
        cardTitle={t('relations.account.orders.title')}
        pageInfo={financeOrders.pageInfo}
        onLoadMore={() => {
          fetchMore({
            variables: {
              after: financeOrders.pageInfo.endCursor
            },
            updateQuery: (previousResult, { fetchMoreResult }) => {
              const newEdges = fetchMoreResult.financeOrders.edges
              const pageInfo = fetchMoreResult.financeOrders.pageInfo

              return newEdges.length
                ? {
                    // Put the new financeOrders at the end of the list and update `pageInfo`
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
              {financeOrders.edges.map(({ node }) => (        
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
                    <Link to={"/finance/orders/edit/" + node.id}>
                      <Button className='btn-sm' 
                              color="secondary">
                        {t('general.edit')}
                      </Button>
                    </Link>
                  </Table.Col>
                  <Table.Col key={v4()}>
                    <AccountOrderDelete node={node} account={account} />
                  </Table.Col>
                </Table.Row>
              ))}
          </Table.Body>
        </Table>
      </ContentCard>
    </AccountOrdersBase>
  )
}
      
        
export default withTranslation()(withRouter(AccountOrders))