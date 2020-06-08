// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { useQuery } from '@apollo/react-hooks'
import { v4 } from 'uuid'

import {
  Card,
  Icon,
  Table,
} from "tabler-react";

import { GET_ORDER_QUERY } from "../queries"


function ShopCheckoutOrderSummary({ t, id }) {
  const { loading, error, data } = useQuery(GET_ORDER_QUERY, {
    variables: { id: id }
  })

  if (loading) return (
      t("general.loading_with_dots")
  )
  if (error) return (
      t("shop.checkout.order_summary.error_loading")
  )

  console.log(data)
  const order = data.financeOrder
  console.log(order)
  const orderItems = order.items.edges
  console.log(orderItems)


  return (
    <Card title={t("shop.checkout.payment.order_summary")}>
      <div className="table-responsive">
        <Table cards={true}>
          <Table.Header>
            <Table.Row>
              <Table.ColHeader>{t('general.item')}</Table.ColHeader>
              <Table.ColHeader>{t('general.price')}</Table.ColHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {orderItems.map(({ node }) => (
              <Table.Row key={v4()}>
                <Table.Col>
                  {node.productName} <br /> 
                  <span className="text-muted">
                    {node.description}
                  </span>
                </Table.Col>
                <Table.Col>{node.totalDisplay}</Table.Col>
              </Table.Row>      
            ))}
            <Table.Row className="bold">
              <Table.Col>
                {t("general.total")}
              </Table.Col>
              <Table.Col>
                  {order.totalDisplay}
              </Table.Col>
            </Table.Row>
          </Table.Body>
        </Table>
      </div>
      <Card.Body>
        {(order.message) ?
          <span className="text-muted">
            <Icon name="message-square" /> {t("shop.checkout.order_summary.message")} <br /><br /> 
            {/* Order message */}
            {order.message}
          </span> 
          : ""
        }
      </Card.Body>
    </Card>
  )
}


export default withTranslation()(withRouter(ShopCheckoutOrderSummary))
