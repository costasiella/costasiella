// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_ALT_PRICES_QUERY } from "./queries"
import { ACCOUNT_SUBSCRIPTION_ALT_PRICE_SCHEMA } from './yupSchema'
import { dateToLocalISO } from '../../../../../../tools/date_tools'

import AccountSubscriptionEditAltPriceBase from "./AccountSubscriptionEditAltPriceBase"
import AccountSubscriptionEditAltPriceForm from "./AccountSubscriptionEditAltPriceForm"


const ADD_ACCOUNT_SUBSCRIPTION_ALT_PRICE = gql`
  mutation CreateAccountSubscriptionAltPrice($input:CreateAccountSubscriptionAltPriceInput!) {
    createAccountSubscriptionAltPrice(input: $input) {
      accountSubscriptionAltPrice {
        id
      }
    }
  }
`


function AccountSubscriptionEditAltPriceAdd({ t, history, match }) {
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/alt_prices/`


  const [addSubscriptionAltPrice] = useMutation(ADD_ACCOUNT_SUBSCRIPTION_ALT_PRICE, {
    onCompleted: () => history.push(returnUrl),
  })

  return (
    <AccountSubscriptionEditAltPriceBase>
      <Formik
        initialValues={{ 
          subscriptionYear: new Date().getFullYear(),
          subscriptionMonth: new Date().getMonth() + 1,
          amount: 0,
          description: "",
          note: ""
        }}
        validationSchema={ACCOUNT_SUBSCRIPTION_ALT_PRICE_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          addSubscriptionAltPrice({ variables: {
            input: {
              accountSubscription: subscriptionId,
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
              toast.success((t('relations.account.subscriptions.alt_prices.toast_add_success')), {
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
            formTitle="create"
          />
        )}
      </Formik>
    </AccountSubscriptionEditAltPriceBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditAltPriceAdd))