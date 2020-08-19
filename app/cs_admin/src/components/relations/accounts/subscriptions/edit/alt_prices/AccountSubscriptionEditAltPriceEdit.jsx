// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_ALT_PRICES_QUERY, GET_ACCOUNT_SUBSCRIPTION_ALT_PRICE_QUERY } from "./queries"
import { ACCOUNT_SUBSCRIPTION_ALT_PRICE_SCHEMA } from './yupSchema'

import AccountSubscriptionEditAltPriceBase from "./AccountSubscriptionEditAltPriceBase"
import AccountSubscriptionEditAltPriceForm from "./AccountSubscriptionEditAltPriceForm"


const UPDATE_ACCOUNT_SUBSCRIPTION_ALT_PRICE = gql`
  mutation UpdateAccountSubscriptionAltPrice($input:UpdateAccountSubscriptionAltPriceInput!) {
    updateAccountSubscriptionAltPrice(input: $input) {
      accountSubscriptionAltPrice {
        id
      }
    }
  }
`


function AccountSubscriptionEditAltPriceEdit({ t, history, match }) {
  const id = match.params.id
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/alt_prices/`

  const { loading, error, data, } = useQuery(GET_ACCOUNT_SUBSCRIPTION_ALT_PRICE_QUERY, {
    variables: {
      id: id
    }
  })

  const [updateSubscriptionAltPrice] = useMutation(UPDATE_ACCOUNT_SUBSCRIPTION_ALT_PRICE, {
    onCompleted: () => history.push(returnUrl),
  })

  if (loading) return (
    <AccountSubscriptionEditAltPriceBase>
        <p>{t('general.loading_with_dots')}</p>
    </AccountSubscriptionEditAltPriceBase>
  )
  // Error
  if (error) {
    return (
      <AccountSubscriptionEditAltPriceBase>
          { console.log(error) }
          <p>{t('general.error_sad_smiley')}</p>
      </AccountSubscriptionEditAltPriceBase>
    )
  }

  console.log('query data')
  console.log(data)
  const inputData = data
  const accountSubscriptionAltPrice = data.accountSubscriptionAltPrice



  return (
    <AccountSubscriptionEditAltPriceBase>
      <Formik
        initialValues={{ 
          subscriptionYear: accountSubscriptionAltPrice.subscriptionYear,
          subscriptionMonth: accountSubscriptionAltPrice.subscriptionMonth,
          amount: accountSubscriptionAltPrice.amount,
          description: accountSubscriptionAltPrice.description,
          note: accountSubscriptionAltPrice.note
        }}
        validationSchema={ACCOUNT_SUBSCRIPTION_ALT_PRICE_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          updateSubscriptionAltPrice({ variables: {
            input: {
              id: id,
              subscriptionYear: values.subscriptionYear,
              subscriptionMonth: values.subscriptionMonth,
              amount: values.amount,
              description: values.description,
              note: values.note,
            }
          }, refetchQueries: [
              {query: GET_ACCOUNT_SUBSCRIPTION_ALT_PRICES_QUERY, variables: {
                accountSubscription: subscriptionId
              }},
          ]})
          .then(({ data }) => {
              console.log('got data', data);
              toast.success((t('relations.account.subscriptions.alt_prices.toast_edit_success')), {
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
          <AccountSubscriptionEditAltPriceForm
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
    </AccountSubscriptionEditAltPriceBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditAltPriceEdit))