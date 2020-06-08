import React, { useContext } from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

// import { get_list_query_variables } from "../tools"
import { DELETE_FINANCE_ORDER, GET_ORDERS_QUERY } from "./queries"
import confirm_delete from "../../../tools/confirm_delete"

import {
  Icon
} from "tabler-react"

import moment from 'moment'
import AppSettingsContext from '../../context/AppSettingsContext'

import { get_list_query_variables } from "./tools"


function FinanceOrderDelete({t, match, node}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const [deleteOrder, { data }] = useMutation(DELETE_FINANCE_ORDER)

    return (
      <button className="icon btn btn-link btn-sm" 
        title={t('general.delete')} 
        href=""
        onClick={() => {
          confirm_delete({
            t: t,
            msgConfirm: t("finance.orders.delete_confirm_msg"),
            msgDescription: <p>{t("general.order")} # { node.orderNumber }</p>,
            msgSuccess: t('finance.orders.deleted'),
            deleteFunction: deleteOrder,
            functionVariables: { 
              variables: {
                input: {
                  id: node.id
                }
              }, 
              refetchQueries: [
                {query: GET_ORDERS_QUERY, variables: get_list_query_variables() },
              ]
            }
          })
      }}>
        <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
      </button>
    )
}


export default withTranslation()(withRouter(FinanceOrderDelete))
