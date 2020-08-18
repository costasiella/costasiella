import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import { DELETE_ACCOUNT_SUBSCRIPTION_PAUSE, GET_ACCOUNT_SUBSCRIPTION_PAUSES_QUERY } from "./queries"
import confirm_delete from "../../../../../../tools/confirm_delete"

import {
  Icon
} from "tabler-react"


function AccountSubscriptionEditPauseDelete({t, match, history, id}) {
  const subscriptionId = match.params.subscription_id
  const [deleteAccountSubscriptionPause, { data }] = useMutation(DELETE_ACCOUNT_SUBSCRIPTION_PAUSE)
  const query_vars = {
    accountSubscription: subscriptionId
  }

  return (
    <button className="icon btn btn-link btn-sm mb-3 pull-right" 
      title={t('general.delete')} 
      onClick={() => {
        confirm_delete({
          t: t,
          msgConfirm: t("relations.account.subscriptions.pauses.delete_confirm_msg"),
          msgDescription: <p></p>,
          msgSuccess: t('relations.account.subscriptions.pauses.delete_success'),
          deleteFunction: deleteAccountSubscriptionPause,
          functionVariables: { 
            variables: {
              input: {
                id: id
              },
            }, 
            refetchQueries: [
              { query: GET_ACCOUNT_SUBSCRIPTION_PAUSES_QUERY, variables: query_vars },
            ]
          }
        })
    }}>
      <Icon prefix="fe" name="trash-2" />
    </button>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditPauseDelete))