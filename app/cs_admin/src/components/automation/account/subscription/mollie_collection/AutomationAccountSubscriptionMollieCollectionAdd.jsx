// @flow

import React from 'react'
import { useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { GET_TASK_RESULT_QUERY } from "../../../queries"
import { AUTOMATION_ACCOUNT_SUBSCRIPTION_MOLLIE_COLLECTION_SCHEMA } from './yupSchema'
import AutomationAccountSubscriptionMollieCollectionForm from './AutomationAccountSubscriptionMollieCollectionForm'


import {
  Card,
} from "tabler-react"
// import SiteWrapper from "../../SiteWrapper"
// import HasPermissionWrapper from "../../HasPermissionWrapper"

import AutomationAccountSubscriptionCreditsBase from './AutomationAccountSubscriptionMollieCollectionBase'


const ADD_TASK = gql`
  mutation CreateAccountSubscriptionInvoicesMollieCollectionForMonth(
    $input:CreateAccountSubscriptionInvoicesMollieCollectionForMonthInput!
  ) {
    createAccountSubscriptionInvoicesMollieCollectionForMonth(input: $input) {
      ok
    }
  }
`


function AutomationAccountSubscriptionMollieCollectionAdd({ t, history }) {
  const [addTask] = useMutation(ADD_TASK)
  const returnUrl = "/automation/account/subscriptions/mollie_collections"

  return (
    <AutomationAccountSubscriptionCreditsBase returnUrl={returnUrl}>
      <Card>
        <Card.Header>
          <Card.Title>{t('automation.account.subscriptions.mollie_collection.title_add')}</Card.Title>
        </Card.Header>
        <Formik
          initialValues={{ 
            subscriptionYear: new Date().getFullYear(), 
            subscriptionMonth: new Date().getMonth() + 1 }}
          validationSchema={AUTOMATION_ACCOUNT_SUBSCRIPTION_MOLLIE_COLLECTION_SCHEMA}
          onSubmit={(values, { setSubmitting }) => {
              addTask({ variables: {
                input: {
                  month: values.subscriptionMonth,
                  year: values.subscriptionYear
                }
              }, refetchQueries: [
                  {query: GET_TASK_RESULT_QUERY, 
                    variables: {
                      taskName: "costasiella.tasks.account.subscription.mollie_collection.tasks.account_subscription_credits_add_for_month"
                  }}
              ]})
              .then(({ data }) => {
                  console.log('got data', data)
                  history.push(returnUrl)
                  toast.success((t('automation.account.subscriptions.mollie_collection.toast_add_success')), {
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
              <AutomationAccountSubscriptionMollieCollectionForm 
                isSubmitting={isSubmitting}
                errors={errors}
                returnUrl={returnUrl}
              />
          )}
        </Formik>
      </Card>
    </AutomationAccountSubscriptionCreditsBase>
  )
}

export default withTranslation()(withRouter(AutomationAccountSubscriptionMollieCollectionAdd))