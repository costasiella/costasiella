// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_PAUSES_QUERY, GET_ACCOUNT_SUBSCRIPTION_PAUSE_QUERY } from "./queries"
import { ACCOUNT_SUBSCRIPTION_PAUSE_SCHEMA } from './yupSchema'
import { dateToLocalISO } from '../../../../../../tools/date_tools'

import AccountSubscriptionEditPauseBase from "./AccountSubscriptionEditPauseBase"
import AccountSubscriptionEditPauseForm from "./AccountSubscriptionEditPauseForm"


const UPDATE_ACCOUNT_SUBSCRIPTION_PAUSE = gql`
  mutation UpdateAccountSubscriptionPause($input:UpdateAccountSubscriptionPauseInput!) {
    updateAccountSubscriptionPause(input: $input) {
      accountSubscriptionPause {
        id
      }
    }
  }
`


function AccountSubscriptionEditPauseEdit({ t, history, match }) {
  const id = match.params.id
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/pauses/`

  const { loading, error, data, } = useQuery(GET_ACCOUNT_SUBSCRIPTION_PAUSE_QUERY, {
    variables: {
      id: id
    }
  })

  const [updateSubscriptionPause] = useMutation(UPDATE_ACCOUNT_SUBSCRIPTION_PAUSE, {
    onCompleted: () => history.push(returnUrl),
  })

  if (loading) return (
    <AccountSubscriptionEditPauseBase>
        <p>{t('general.loading_with_dots')}</p>
    </AccountSubscriptionEditPauseBase>
  )
  // Error
  if (error) {
    return (
      <AccountSubscriptionEditPauseBase>
          { console.log(error) }
          <p>{t('general.error_sad_smiley')}</p>
      </AccountSubscriptionEditPauseBase>
    )
  }

  console.log('query data')
  console.log(data)
  const inputData = data
  const accountSubscriptionPause = data.accountSubscriptionPause



  return (
    <AccountSubscriptionEditPauseBase>
      <Formik
        initialValues={{ 
          dateStart: new Date(accountSubscriptionPause.dateStart),
          dateEnd: new Date(accountSubscriptionPause.dateEnd),
          description: accountSubscriptionPause.description
        }}
        validationSchema={ACCOUNT_SUBSCRIPTION_PAUSE_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          updateSubscriptionPause({ variables: {
            input: {
              id: id,
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
              toast.success((t('relations.account.subscriptions.pauses.toast_edit_success')), {
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
            formTitle="update"
          />
        )}
      </Formik>
    </AccountSubscriptionEditPauseBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditPauseEdit))