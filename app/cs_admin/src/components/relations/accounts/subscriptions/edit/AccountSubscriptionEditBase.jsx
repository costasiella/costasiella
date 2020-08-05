// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, Mutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_QUERY } from '../queries'
import AccountSubscriptionForm from '../AccountSubscriptionForm'

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";
import SiteWrapper from "../../../../SiteWrapper"
import HasPermissionWrapper from "../../../../HasPermissionWrapper"
import { dateToLocalISO } from '../../../../../tools/date_tools'
import AccountSubscriptionEditTabs from "./AccountSubscriptionEditTabs"
import AccountSubscriptionEditBaseBase from "./AccountSubscriptionEditBaseBase"

import ProfileMenu from "../../ProfileMenu"


function AccountSubscriptionEditBase({t, history, match, children, active_tab}) {
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const { loading, error, data } = useQuery(GET_ACCOUNT_SUBSCRIPTION_QUERY, {
    variables: {
      accountId: accountId,
      id: subscriptionId
    }
  })
  
  if (loading) return (
    <AccountSubscriptionEditBaseBase active_tab={active_tab}>
      {t("general.loading_with_dots")}
    </AccountSubscriptionEditBaseBase>
  )
  if (error) return (
    <AccountSubscriptionEditBaseBase active_tab={active_tab}>
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </AccountSubscriptionEditBaseBase>
  )

  console.log(data)
  const account = data.account
  const subscription = data.accountSubscription

  return (
    <AccountSubscriptionEditBaseBase active_tab={active_tab} account={account} subscription={subscription}>
      {children}
    </AccountSubscriptionEditBaseBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditBase))
