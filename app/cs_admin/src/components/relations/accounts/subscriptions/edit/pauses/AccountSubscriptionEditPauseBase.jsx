// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


// import { GET_INVOICE_QUERY, GET_INPUT_VALUES_QUERY } from './queries'
// import { GET_INVOICE_QUERY } from "../queries"

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
// import ScheduleClassPriceBack from "./ScheduleClassPriceBack"
import AccountSubscriptionEditBase from "../AccountSubscriptionEditBase"


function AccountSubscriptionEditPauseBase({ t, history, match, children}) {
  const activeTab = "pauses"
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/pauses/`

  return (
    <AccountSubscriptionEditBase active_tab={activeTab}>
      {children}
    </AccountSubscriptionEditBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditPauseBase))