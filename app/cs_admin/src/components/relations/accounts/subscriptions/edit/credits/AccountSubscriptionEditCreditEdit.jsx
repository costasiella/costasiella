// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_QUERY } from "../../queries"
import { GET_ACCOUNT_SUBSCRIPTION_CREDITS_QUERY, GET_ACCOUNT_SUBSCRIPTION_CREDIT_QUERY } from "./queries"
import { ACCOUNT_SUBSCRIPTION_CREDIT_SCHEMA } from './yupSchema'
import { dateToLocalISO } from '../../../../../../tools/date_tools'

import AccountSubscriptionEditCreditBase from "./AccountSubscriptionEditCreditBase"
import AccountSubscriptionEditCreditForm from "./AccountSubscriptionEditCreditForm"


const UPDATE_ACCOUNT_SUBSCRIPTION_CREDIT = gql`
  mutation UpdateAccountSubscriptionCredit($input:UpdateAccountSubscriptionCreditInput!) {
    updateAccountSubscriptionCredit(input: $input) {
      accountSubscriptionCredit {
        id
      }
    }
  }
`


function AccountSubscriptionEditCreditEdit({ t, history, match }) {
  const id = match.params.id
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/credits/`

  const { loading, error, data, } = useQuery(GET_ACCOUNT_SUBSCRIPTION_CREDIT_QUERY, {
    variables: {
      id: id
    }
  })

  const [updateSubscriptionCredit] = useMutation(UPDATE_ACCOUNT_SUBSCRIPTION_CREDIT, {
    onCompleted: () => history.push(returnUrl),
  })

  if (loading) return (
    <AccountSubscriptionEditCreditBase>
        <p>{t('general.loading_with_dots')}</p>
    </AccountSubscriptionEditCreditBase>
  )
  // Error
  if (error) {
    return (
      <AccountSubscriptionEditCreditBase>
          { console.log(error) }
          <p>{t('general.error_sad_smiley')}</p>
      </AccountSubscriptionEditCreditBase>
    )
  }

  console.log('query data')
  console.log(data)
  const accountSubscriptionCredit = data.accountSubscriptionCredit


  return (
    <AccountSubscriptionEditCreditBase>
      <Formik
        initialValues={{ 
          mutationType: accountSubscriptionCredit.mutationType,
          mutationAmount: accountSubscriptionCredit.mutationAmount,
          description: accountSubscriptionCredit.description
        }}
        validationSchema={ACCOUNT_SUBSCRIPTION_CREDIT_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          updateSubscriptionCredit({ variables: {
            input: {
              id: id,
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
              toast.success((t('relations.account.subscriptions.credits.toast_edit_success')), {
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
            formTitle="update"
          />
        )}
      </Formik>
    </AccountSubscriptionEditCreditBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditCreditEdit))