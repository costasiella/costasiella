import React from 'react'
import { Link } from 'react-router-dom'

import {
  Icon,
  List
} from "tabler-react"


export function get_list_query_variables(batchType) {
  let queryVars = {
    batchType: batchType.toUpperCase()
  }

  console.log(queryVars)

  return queryVars
}


export function get_add_options_collection(t, batchType) {
  return (
    <List unstyled>
      <List.Item>
        <Link to={`/finance/paymentbatches/${batchType}/add/invoices`}>
          <b>{t("finance.payment_batch_collections.invoices_batch")} <Icon name="chevron-right" /></b>
        </Link><br />
        <p>{t("finance.payment_batch_collections.invoices_batch_description")}</p>
      </List.Item>
      <List.Item>
        <Link to={`/finance/paymentbatches/${batchType}/add/category`}>
          <b>{t("finance.payment_batch_collections.category_batch")} <Icon name="chevron-right" /></b>
        </Link><br />
        <p>{t("finance.payment_batch_collections.category_batch_description")}</p>
      </List.Item>
    </List>
  )
}


export function get_add_options_payment(t, batchType) {
  return (
    <List unstyled>
      <List.Item>
        <Link to={`/finance/paymentbatches/${batchType}/add/category`}>
          <b>{t("finance.payment_batch_payments.category_batch")} <Icon name="chevron-right" /></b>
        </Link><br />
        <p>{t("finance.payment_batch_payments.category_batch_description")}</p>
      </List.Item>
    </List>
  )
}