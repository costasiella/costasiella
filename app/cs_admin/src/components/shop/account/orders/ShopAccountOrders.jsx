// @flow

import React, { useContext} from 'react'
import { useQuery } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { v4 } from "uuid"
import moment from 'moment'

import AppSettingsContext from '../../../context/AppSettingsContext'

import {
  Card,
  Grid,
  Table
} from "tabler-react";
import { QUERY_ACCOUNT_ORDERS } from "./queries"

import ShopAccountOrdersBase from "./ShopAccountOrdersBase"
import LoadMoreOnBottomScroll from "../../../general/LoadMoreOnBottomScroll"


function ShopAccountOrders({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  const dateTimeFormat = dateFormat + ' ' + timeFormat
  const { loading, error, data, fetchMore } = useQuery(QUERY_ACCOUNT_ORDERS)
  

  if (loading) return (
    <ShopAccountOrdersBase>
      {t("general.loading_with_dots")}
    </ShopAccountOrdersBase>
  )
  if (error) return (
    <ShopAccountOrdersBase>
      {t("shop.account.classpasses.error_loading_data")}
    </ShopAccountOrdersBase>
  )

  console.log("User data: ###")
  console.log(data)
  const user = data.user
  const orders = data.financeOrders

  // Empty list
  if (!orders.edges.length) {
    return (
      <ShopAccountOrdersBase accountName={user.fullName}>
        <Grid.Row>
          <Grid.Col md={12}>
            <Card cardTitle={t('shop.account.orders.title')} >
              <Card.Body>
                {t('shop.account.orders.empty_list')}
              </Card.Body>
            </Card>
          </Grid.Col>
        </Grid.Row>
      </ShopAccountOrdersBase>
    )  
  }

  // Populated list
  return (
    <ShopAccountOrdersBase accountName={user.fullName}>
      <Grid.Row>
        <Grid.Col md={12}>
          <LoadMoreOnBottomScroll
            // headerContent={headerOptions}
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
                        // Put the new subscriptions at the end of the list and update `pageInfo`
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
            }} >
            <h4>{t("shop.account.orders.title")}</h4>
            {orders.edges.map(({ node }) => (
              <div>
                {moment(node.createdAt).format(dateTimeFormat)}
                {node.status}
              </div>
            ))}

            {/* <Table>
              <Table.Header>
                <Table.Row key={v4()}>
                  <Table.ColHeader>{t('general.name')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.date_start')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.date_end')}</Table.ColHeader>
                  <Table.ColHeader>{t('general.classes_remaining')}</Table.ColHeader>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {classpasses.edges.map(({ node }) => (
                  <Table.Row key={v4()}>
                    <Table.Col>
                      {node.organizationClasspass.name}
                    </Table.Col>
                    <Table.Col>
                      {moment(node.dateStart).format(dateFormat)}
                    </Table.Col>
                    <Table.Col>
                      {moment(node.dateEnd).format(dateFormat)}
                    </Table.Col>
                    <Table.Col>
                      {node.classesRemainingDisplay}
                    </Table.Col>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table> */}
          </LoadMoreOnBottomScroll>
        </Grid.Col>
      </Grid.Row>
    </ShopAccountOrdersBase>
  )
}


export default withTranslation()(withRouter(ShopAccountOrders))