import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { GET_ACCOUNT_SUBSCRIPTION_QUERY } from "../../queries"
import { DELETE_ACCOUNT_SUBSCRIPTION_CREDIT, GET_ACCOUNT_SUBSCRIPTION_CREDITS_QUERY } from "./queries"
import confirm_delete from "../../../../../../tools/confirm_delete"

import {
  Icon
} from "tabler-react"


function AccountSubscriptionEditCreditDelete({t, match, history, id}) {
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const [deleteAccountSubscriptionCredit] = useMutation(DELETE_ACCOUNT_SUBSCRIPTION_CREDIT)
  const query_vars = {
    accountSubscription: subscriptionId
  }

  return (
    <button className="icon btn btn-link btn-sm mb-3 pull-right" 
      title={t('general.delete')} 
      onClick={() => {
        confirm_delete({
          t: t,
          msgConfirm: t("relations.account.subscriptions.credits.delete_confirm_msg"),
          msgDescription: <p></p>,
          msgSuccess: t('relations.account.subscriptions.credits.delete_success'),
          deleteFunction: deleteAccountSubscriptionCredit,
          functionVariables: { 
            variables: {
              input: {
                id: id
              },
            }, 
            refetchQueries: [
              { query: GET_ACCOUNT_SUBSCRIPTION_CREDITS_QUERY, variables: query_vars },
              { query: GET_ACCOUNT_SUBSCRIPTION_QUERY, variables: {
                accountId: accountId,
                id: subscriptionId
              }}
            ]
          }
        })
    }}>
      <Icon prefix="fe" name="trash-2" />
    </button>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditCreditDelete))