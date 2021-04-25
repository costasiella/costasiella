// @flow

import React from 'react'
import { useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { GET_TASK_RESULT_QUERY } from "../../../queries"
import { AUTOMATION_ACCOUNT_SUBSCRIPTION_CREDIT_SCHEMA } from './yupSchema'
import AutomationAccountSubscriptionCreditForm from './AutomationAccountSubscriptionCreditForm'


import {
  Card,
} from "tabler-react"
// import SiteWrapper from "../../SiteWrapper"
// import HasPermissionWrapper from "../../HasPermissionWrapper"

import AutomationAccountSubscriptionInvoicesBase from './AutomationAccountSubscriptionInvoicesBase'


const ADD_TASK = gql`
  mutation CreateAccountSubscriptionInvoicesForMonth($input:CreateAccountSubscriptionInvoicesForMonthInput!) {
    createAccountSubscriptionInvoicesForMonth(input: $input) {
      ok
    }
  }
`


function AutomationAccountSubscriptionCreditAdd({ t, history }) {
  const [addTask] = useMutation(ADD_TASK)
  const returnUrl = "/automation/account/subscriptions/invoices"

  return (
    <AutomationAccountSubscriptionInvoicesBase returnUrl={returnUrl}>
      <Card>
        <Card.Header>
          <Card.Title>{t('automation.account.subscriptions.invoices.title_add')}</Card.Title>
        </Card.Header>
        <Formik
          initialValues={{ 
            subscriptionYear: new Date().getFullYear(), 
            subscriptionMonth: new Date().getMonth() + 1 }}
          validationSchema={AUTOMATION_ACCOUNT_SUBSCRIPTION_CREDIT_SCHEMA}
          onSubmit={(values, { setSubmitting }) => {
              addTask({ variables: {
                input: {
                  month: values.subscriptionMonth,
                  year: values.subscriptionYear
                }
              }, refetchQueries: [
                  {query: GET_TASK_RESULT_QUERY, 
                    variables: {
                      taskName: "costasiella.tasks.account.subscription.invoices.tasks.account_subscription_invoices_add_for_month"
                  }}
              ]})
              .then(({ data }) => {
                  console.log('got data', data)
                  history.push(returnUrl)
                  toast.success((t('automation.account.subscriptions.invoices.toast_add_success')), {
                      position: toast.POSITION.BOTTOM_RIGHT
                    })
                }).catch((error) => {
                  toast.error((t('general.toast_server_error')) + ': ' +  error, {
                      position: toast.POSITION.BOTTOM_RIGHT
                    })
                  console.log('there was an error sending the query', error)
                  setSubmitting(false)
                })
          }}
          >
          {({ isSubmitting, errors }) => (
              <AutomationAccountSubscriptionCreditForm 
                isSubmitting={isSubmitting}
                errors={errors}
                returnUrl={returnUrl}
              />
          )}
        </Formik>
      </Card>
    </AutomationAccountSubscriptionInvoicesBase>
  )
}

export default withTranslation()(withRouter(AutomationAccountSubscriptionCreditAdd))