import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { GET_FINANCE_INVOICE_ITEM_QUERY } from "./queries"
import { DELETE_FINANCE_INVOICE } from "../../../../../finance/invoices/queries"
import confirm_delete from "../../../../../../tools/confirm_delete"

import {
  Icon
} from "tabler-react"


function AccountSubscriptionEditInvoiceDelete({t, match, history, id}) {
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const [deleteAccountSubscriptionInvoice] = useMutation(DELETE_FINANCE_INVOICE)
  const query_vars = {
    accountSubscription: subscriptionId
  }

  return (
    <button className="icon btn btn-link btn-sm mb-3 pull-right" 
      title={t('general.delete')} 
      onClick={() => {
        confirm_delete({
          t: t,
          msgConfirm: t("finance.invoices.delete_confirm_msg"),
          msgDescription: <p></p>,
          msgSuccess: t('finance.invoices.deleted'),
          deleteFunction: deleteAccountSubscriptionInvoice,
          functionVariables: { 
            variables: {
              input: {
                id: id
              },
            }, 
            refetchQueries: [
              { query: GET_FINANCE_INVOICE_ITEM_QUERY, variables: query_vars },
              // { query: GET_FINANCE_INVOICE_ITEM_QUERY, variables: {
              //   accountId: accountId,
              //   id: subscriptionId
              // }}
            ]
          }
        })
    }}>
      <Icon prefix="fe" name="trash-2" />
    </button>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditInvoiceDelete))