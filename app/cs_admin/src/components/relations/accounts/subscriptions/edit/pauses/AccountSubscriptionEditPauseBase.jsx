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
import { GET_INVOICE_QUERY } from "../queries"

import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
  Table
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
// import ScheduleClassPriceBack from "./ScheduleClassPriceBack"
import AccountSubscriptionEditBase from "../AccountSubscriptionEditBase"


function AccountSubscriptionEditPauseBase({ t, history, match, children, formType="create" }) {
  const activeTab = "pauses"
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/pauses/`

  console.log('query data')
  console.log(data)
  const inputData = data
  const invoice_number = inputData.financeInvoice.invoiceNumber

  let title
  if ( form_type == "create" ) {
    title = t('relations.account.subscriptions.pauses.add')
  } else {
    title = t('relations.account.subscriptions.pauses.edit')
  }

  title = title + " #" + invoice_number

  return (
    <AccountSubscriptionEditBase active_tab={activeTab}>
      <div className="pull-right"></div>
      <h5>{title}</h5>
      {children}
    </AccountSubscriptionEditBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditPauseBase))