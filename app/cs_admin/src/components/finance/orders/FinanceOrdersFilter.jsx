// @flow

import React from 'react'
import { v4 } from "uuid"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import CSLS from "../../../tools/cs_local_storage"
import { get_list_query_variables } from './tools'


function getDefaultValue(value) {
  let defaultValue = localStorage.getItem(value)
  console.log(defaultValue)

  if (defaultValue) {
    return defaultValue
  } else {
    console.log('return empty default')
    return ""
  }
}


function updateLocalStorageAndRefetch(key, value, refetch) {
  localStorage.setItem(key, value)
  refetch(get_list_query_variables())

}

const selectClass = "form-control mb-2"


const FinanceOrdersFilter = ({ t, history, data, refetch }) => (
  <div>
    {/* Status */}
    <select 
      className={selectClass}
      value={getDefaultValue(CSLS.FINANCE_ORDERS_FILTER_STATUS)}
      onChange={ (event) => {
        updateLocalStorageAndRefetch(
          CSLS.FINANCE_ORDERS_FILTER_STATUS,
          event.target.value,
          refetch
        )
      }}
    >
      <option value="" key={v4()}>{t('finance.orders.statuses.all')}</option>
      <option value="RECEIVED" key={v4()}>{t('finance.orders.statuses.RECEIVED')}</option>
      <option value="AWAITING_PAYMENT" key={v4()}>{t('finance.orders.statuses.AWAITING_PAYMENT')}</option>
      <option value="PAID" key={v4()}>{t('finance.orders.statuses.PAID')}</option>
      <option value="DELIVERED" key={v4()}>{t('finance.orders.statuses.DELIVERED')}</option>
      <option value="CANCELLED" key={v4()}>{t('finance.orders.statuses.CANCELLED')}</option>
    </select>
  </div>
);

export default withTranslation()(withRouter(FinanceOrdersFilter))