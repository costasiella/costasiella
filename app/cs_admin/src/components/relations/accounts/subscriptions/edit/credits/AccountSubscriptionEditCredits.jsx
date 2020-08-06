// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import { Formik } from 'formik'
import { toast } from 'react-toastify'

// import { GET_ACCOUNT_SUBSCRIPTIONS_QUERY, GET_ACCOUNT_SUBSCRIPTION_QUERY } from '../queries'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";
// import HasPermissionWrapper from "../../../../HasPermissionWrapper"
import AccountSubscriptionEditListBase from "../AccountSubscriptionEditListBase"


function AccountSubscriptionEditCredits({t, match, history}) {
  const id = match.params.subscription_id
  const accountId = match.params.account_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions`
  const activeTab = "credits"

  // const { loading, error, data } = useQuery(GET_ACCOUNT_SUBSCRIPTION_QUERY, {
  //   variables: {
  //     archived: false,
  //     accountId: accountId,
  //     id: id
  //   }
  // })
  
  // if (loading) return (
  //   <AccountSubscriptionEditBase active_tab={activeTab}>
  //     {t("general.loading_with_dots")}
  //   </AccountSubscriptionEditBase>
  // )
  // if (error) return (
  //   <AccountSubscriptionEditBase active_tab={activeTab}>
  //     <p>{t('general.error_sad_smiley')}</p>
  //     <p>{error.message}</p>
  //   </AccountSubscriptionEditBase>
  // )

  // console.log('query data')
  // console.log(data)
  // const inputData = data
  // const account = data.account
  // const initialdata = data.accountSubscription

  // let initialPaymentMethod = ""
  // if (initialdata.financePaymentMethod) {
  //   initialPaymentMethod = initialdata.financePaymentMethod.id
  // }

  return (
    <AccountSubscriptionEditListBase active_tab={activeTab}>
      hello world
    </AccountSubscriptionEditListBase>
  )
}

export default withTranslation()(withRouter(AccountSubscriptionEditCredits))
