import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

// import { get_list_query_variables } from "../tools"
import { DELETE_INVOICE_PAYMENT, GET_INVOICES_QUERY, GET_INVOICE_QUERY } from "../queries"
import confirm_delete from "../../../../tools/confirm_delete"

import {
  Icon
} from "tabler-react"



function FinanceInvoiceEditPaymentDelete({t, match, node}) {
  const [deleteInvoicePayment, { data }] = useMutation(DELETE_INVOICE_PAYMENT)

    return (
      <button className="icon btn btn-link btn-sm" 
        title={t('general.delete')} 
        href=""
        onClick={() => {
          confirm_delete({
            t: t,
            msgConfirm: t("finance.invoices.payment_delete_confirm_msg"),
            msgDescription: <p>{node.date} <br /> {node.amountDisplay}</p>,
            msgSuccess: t('finance.invoices.payment_deleted'),
            deleteFunction: deleteInvoicePayment,
            functionVariables: { 
              variables: {
                input: {
                  id: node.id
                }
              }, 
              refetchQueries: [
                // {query: GET_INVOICES_QUERY, variables: get_list_query_variables() },
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
