// @flow

import React, { useContext } from 'react'
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { v4 } from "uuid"
import { Link } from 'react-router-dom'
import moment from 'moment'

import AppSettingsContext from '../../../context/AppSettingsContext'
import FinanceOrderStatus from "../../../finance/orders/FinanceOrderStatus"

import {
  Button,
  Card,
  Grid,
  Icon,
  Table
} from "tabler-react"
import { QUERY_ACCOUNT_ORDERS, UPDATE_ORDER } from "./queries"
import GET_USER_PROFILE from "../../../../queries/system/get_user_profile"

import ShopAccountOrdersBase from "./ShopAccountOrdersBase"
import { cancelOrder } from "./ShopAccountOrderCancel"
import LoadMoreOnBottomScroll from "../../../general/LoadMoreOnBottomScroll"

import { get_order_card_status_color } from "./tools"

function ShopAccountOrders({t, match, history}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  const dateTimeFormat = dateFormat + ' ' + timeFormat

  // Chain queries. First query user data and then query orders for that user once we have the account Id.
  const { loading: loadingUser, error: errorUser, data: dataUser } = useQuery(GET_USER_PROFILE)
  const { loading, error, data, fetchMore } = useQuery(QUERY_ACCOUNT_ORDERS, {
    skip: loadingUser || errorUser || !dataUser,
    variables: {
      account: dataUser && dataUser.user ? dataUser.user.accountId : null
    }
  })
  const [ updateOrder ] = useMutation(UPDATE_ORDER)

  if (loading || loadingUser || !data) return (
    <ShopAccountOrdersBase>
      {t("general.loading_with_dots")}
    </ShopAccountOrdersBase>
  )
  if (error || errorUser) return (
    <ShopAccountOrdersBase>
      {t("shop.account.classpasses.error_loading_data")}
    </ShopAccountOrdersBase>
  )

  console.log("User data: ###")
  console.log(data)
  const user = dataUser.user
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
                <span className="pull-right">
                  <FinanceOrderStatus status={node.status} />
                </span>
                <span className="text-muted">
                  {moment(node.createdAt).format(dateTimeFormat)}
                </span>
                <Card statusColor={get_order_card_status_color(node.status)}>
                  <Card.Header>
                    <Card.Title>{t("general.order") + " #" + node.orderNumber}</Card.Title>
                    <Card.Options>
                      {(node.status == "RECEIVED" || node.status == "AWAITING_PAYMENT") ?
                        <Button
                          outline
                          color="warning"
                          size="sm"
                          onClick={() => cancelOrder({
                            t: t,
                            msgConfirm: t('shop.account.orders.msg_cancel_confirm'),
                            msgDescription: <p>{t('general.order') + " #" + node.orderNumber}</p>, 
                            msgSuccess: t('shop.account.orders.order.cancelled'), 
                            cancelFunction: updateOrder, 
                            functionVariables: {
                              variables: {
                                input: {
                                  id: node.id,
                                  status: 'CANCELLED'
                                }
                              }
                            }
                          })}
                        >
                          {t('general.cancel')}
                        </Button>
                      : ""}
                      {(node.status == "AWAITING_PAYMENT") ?
                        <Link to={"/shop/checkout/payment/" + node.id}>
                          <Button
                            className="ml-4"
                            color="success"
                            size="sm"
                          >
                            {t('shop.account.orders.to_payment')} <Icon name="chevron-right" />
                          </Button>
                        </Link>
                      : ""}
                    </Card.Options>
                  </Card.Header>
                  <Table cards>
                    <Table.Header>
                      <Table.Row>
                        <Table.ColHeader>{t("general.product")}</Table.ColHeader>
                        <Table.ColHeader>{t("general.description")}</Table.ColHeader>
                        <Table.ColHeader>{t("general.total")}</Table.ColHeader>
                      </Table.Row>
                    </Table.Header>
                    <Table.Body>
                      {node.items.edges.map(({ node }) => (
                        <Table.Row>
                          <Table.Col>{node.productName}</Table.Col>
                          <Table.Col>{node.description}</Table.Col>
                          <Table.Col>{node.totalDisplay}</Table.Col>
                        </Table.Row>    
                      ))}
                      <Table.Row>
                        <Table.Col></Table.Col>
                        <Table.Col></Table.Col>
                        <Table.Col><span className="bold">{node.totalDisplay}</span></Table.Col>
                      </Table.Row>
                    </Table.Body>
                  </Table>
                </Card>
              </div>
            ))}
          </LoadMoreOnBottomScroll>
        </Grid.Col>
      </Grid.Row>
    </ShopAccountOrdersBase>
  )
}


export default withTranslation()(withRouter(ShopAccountOrders))