// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_QUERY } from "../../queries"
import { GET_ACCOUNT_SUBSCRIPTION_CREDITS_QUERY } from "./queries"
import { ACCOUNT_SUBSCRIPTION_CREDIT_SCHEMA } from './yupSchema'
import { dateToLocalISO } from '../../../../../../tools/date_tools'

import AccountSubscriptionEditCreditBase from "./AccountSubscriptionEditCreditBase"
import AccountSubscriptionEditCreditForm from "./AccountSubscriptionEditCreditForm"


const ADD_ACCOUNT_SUBSCRIPTION_CREDIT = gql`
  mutation CreateAccountSubscriptionCredit($input:CreateAccountSubscriptionCreditInput!) {
    createAccountSubscriptionCredit(input: $input) {
      accountSubscriptionCredit {
        id
      }
    }
  }
`


function AccountSubscriptionEditCreditAdd({ t, history, match }) {
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/credits/`

  const [addSubscriptionCredit] = useMutation(ADD_ACCOUNT_SUBSCRIPTION_CREDIT, {
    onCompleted: () => history.push(returnUrl),
  })

  return (
    <AccountSubscriptionEditCreditBase>
      <Formik
        initialValues={{ 
          mutationType: "ADD",
          mutationAmount: 0,
          description: ""
        }}
        validationSchema={ACCOUNT_SUBSCRIPTION_CREDIT_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          addSubscriptionCredit({ variables: {
            input: {
              accountSubscription: subscriptionId,
              mutationType: values.mutationType,
              mutationAmount: values.mutationAmount,
              description: values.description
            }
          }, refetchQueries: [
              {query: GET_ACCOUNT_SUBSCRIPTION_CREDITS_QUERY, variables: {
                accountSubscription: subscriptionId
              }},
              {query: GET_ACCOUNT_SUBSCRIPTION_QUERY, variables: {
                accountId: accountId,
                id: subscriptionId
              }}
          ]})
          .then(({ data }) => {
              console.log('got data', data);
              toast.success((t('relations.account.subscriptions.credits.toast_add_success')), {
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
        {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
          <AccountSubscriptionEditCreditForm
            isSubmitting={isSubmitting}
            setFieldTouched={setFieldTouched}
            setFieldValue={setFieldValue}
            errors={errors}
            values={values}
            returnUrl={returnUrl}
            formTitle="create"
          />
        )}
      </Formik>
    </AccountSubscriptionEditCreditBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditCreditAdd))