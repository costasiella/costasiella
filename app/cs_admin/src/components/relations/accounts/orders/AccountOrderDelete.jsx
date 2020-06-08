import React, { useContext } from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { GET_ACCOUNT_ORDERS_QUERY } from "./queries"
import { DELETE_FINANCE_ORDER } from "../../../finance/orders/queries"
import confirm_delete from "../../../../tools/confirm_delete"

import AppSettingsContext from '../../../context/AppSettingsContext'

import moment from 'moment'

import {
  Icon,
  List
} from "tabler-react"


function AccountClassDelete({t, match, node, account}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const timeFormat = appSettings.timeFormatMoment
  const [deleteOrder, { data }] = useMutation(DELETE_FINANCE_ORDER)

  console.log("AccountOrderDelete")
  console.log(node)
  console.log(account)
  console.log("---")

  return (
    <button className="icon btn btn-link btn-sm pull-right" 
      title={t('general.delete')} 
      href=""
      onClick={() => {
        confirm_delete({
          t: t,
          msgConfirm: t("relations.account.orders.delete_confirm_msg"),
          msgDescription: <p>
            {t('general.order')}# {node.orderNumber}
          </p>,
          msgSuccess: t('relations.account.orders.delete_success'),
          deleteFunction: deleteOrder,
          functionVariables: { 
            variables: {
              input: {
                id: node.id
              }
            }, 
            refetchQueries: [
              { query: GET_ACCOUNT_ORDERS_QUERY, 
                variables: { account: account.id } },
            ]
          }
        })
    }}>
      <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
    </button>
  )
}


export default withTranslation()(withRouter(AccountClassDelete))
