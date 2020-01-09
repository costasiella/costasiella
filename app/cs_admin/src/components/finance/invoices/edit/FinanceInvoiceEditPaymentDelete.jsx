import React, { useContext } from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

// import { get_list_query_variables } from "../tools"
import { DELETE_INVOICE_PAYMENT, GET_INVOICES_QUERY, GET_INVOICE_QUERY } from "../queries"
import confirm_delete from "../../../../tools/confirm_delete"

import {
  Icon
} from "tabler-react"

import moment from 'moment'
import AppSettingsContext from '../../../context/AppSettingsContext'

import { get_list_query_variables } from "../tools"


function FinanceInvoiceEditPaymentDelete({t, match, node}) {
  const appSettings = useContext(AppSettingsContext)
  const dateFormat = appSettings.dateFormat
  const [deleteInvoicePayment, { data }] = useMutation(DELETE_INVOICE_PAYMENT)

    return (
      <button className="icon btn btn-link btn-sm" 
        title={t('general.delete')} 
        href=""
        onClick={() => {
          confirm_delete({
            t: t,
            msgConfirm: t("finance.invoices.payment_delete_confirm_msg"),
            msgDescription: <p>{ moment(node.date).format(dateFormat) } - {node.amountDisplay}</p>,
            msgSuccess: t('finance.invoices.payment_deleted'),
            deleteFunction: deleteInvoicePayment,
            functionVariables: { 
              variables: {
                input: {
                  id: node.id
                }
              }, 
              refetchQueries: [
                {query: GET_INVOICES_QUERY, variables: get_list_query_variables() },
                {query: GET_INVOICE_QUERY, variables: {id: match.params.id} },
              ]
            }
          })
      }}>
        <span className="text-red"><Icon prefix="fe" name="trash-2" /></span>
      </button>
    )
}


export default withTranslation()(withRouter(FinanceInvoiceEditPaymentDelete))
