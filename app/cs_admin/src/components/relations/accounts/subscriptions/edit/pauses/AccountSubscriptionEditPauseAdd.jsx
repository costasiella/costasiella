// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_PAUSES_QUERY } from "./queries"
import { ACCOUNT_SUBSCRIPTION_PAUSE_SCHEMA } from './yupSchema'
import { dateToLocalISO } from '../../../../../../tools/date_tools'

import AccountSubscriptionEditPauseBase from "./AccountSubscriptionEditPauseBase"
import AccountSubscriptionEditPauseForm from "./AccountSubscriptionEditPauseForm"


const ADD_ACCOUNT_SUBSCRIPTION_PAUSE = gql`
  mutation CreateAccountSubscriptionPause($input:CreateAccountSubscriptionPauseInput!) {
    createAccountSubscriptionPause(input: $input) {
      accountSubscriptionPause {
        id
      }
    }
  }
`


function AccountSubscriptionEditPauseAdd({ t, history, match }) {
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/pauses/`

  const [addSubscriptionPause] = useMutation(ADD_ACCOUNT_SUBSCRIPTION_PAUSE, {
    onCompleted: () => history.push(returnUrl),
  })

  return (
    <AccountSubscriptionEditPauseBase>
      <Formik
        initialValues={{ 
          dateStart: new Date() ,
          description: ""
        }}
        validationSchema={ACCOUNT_SUBSCRIPTION_PAUSE_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          addSubscriptionPause({ variables: {
            input: {
              accountSubscription: subscriptionId,
              dateStart: dateToLocalISO(values.dateStart),
              dateEnd: dateToLocalISO(values.dateEnd),
              description: values.description
            }
          }, refetchQueries: [
              {query: GET_ACCOUNT_SUBSCRIPTION_PAUSES_QUERY, variables: {
                accountSubscription: subscriptionId
              }},
          ]})
          .then(({ data }) => {
              console.log('got data', data);
              toast.success((t('relations.account.subscriptions.pauses.toast_add_success')), {
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
          <AccountSubscriptionEditPauseForm
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
    </AccountSubscriptionEditPauseBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditPauseAdd))