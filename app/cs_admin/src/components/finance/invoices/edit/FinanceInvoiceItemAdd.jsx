// @flow

import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { get_list_query_variables } from "../tools"
import { CREATE_INVOICE_ITEM, GET_INVOICES_QUERY, GET_INVOICE_QUERY } from "../queries"
import { toast } from 'react-toastify'

import {
  Icon
} from "tabler-react"



function FinanceInvoiceItemAdd({t, match}) {
  const [addInvoiceItem, { data }] = useMutation(CREATE_INVOICE_ITEM)

    return (
      <button className="btn btn-primary btn-sm" 
        title={t('general.delete')} 
        href=""
        onClick={() => {
          addInvoiceItem({ variables: {
            input: {
              financeInvoice: match.params.id              
            }
          }, refetchQueries: [
              {query: GET_INVOICE_QUERY, variables: {id: match.params.id}}
          ]})
          .then(({ data }) => {
              console.log('got data', data)
              toast.success((t('finance.invoice.toast_add_item_success')), {
                  position: toast.POSITION.BOTTOM_RIGHT
                })
              // setSubmitting(false)
            }).catch((error) => {
              toast.error((t('general.toast_server_error')) + ': ' +  error, {
                  position: toast.POSITION.BOTTOM_RIGHT
                })
              console.log('there was an error sending the query', error)
              // setSubmitting(false)
            })
      }}>
        <Icon prefix="fe" name="plus" /> { ' ' }
        {t('finance.invoice.item_add')}
      </button>
    )
}


export default withTranslation()(withRouter(FinanceInvoiceItemAdd))
