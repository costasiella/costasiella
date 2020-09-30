// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_QUERY } from "../../queries"
import { GET_ACCOUNT_SUBSCRIPTION_CREDITS_QUERY } from "./queries"
import { CREATE_ACCOUNT_INVOICE } from "../invoices/queries"
import { ACCOUNT_SUBSCRIPTION_CREDIT_SCHEMA } from './yupSchema'

import AccountSubscriptionEditCreditBase from "./AccountSubscriptionEditCreditBase"
import AccountSubscriptionEditInvoiceAddForm from "./AccountSubscriptionEditInvoiceAddForm"


function AccountSubscriptionEditFinanceInvoiceAdd({ t, history, match }) {
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/invoices/`

  const [ addFinanceInvoice ] = useMutation(CREATE_ACCOUNT_INVOICE, {
    onCompleted: () => history.push(returnUrl),
  })

  return (
    <AccountSubscriptionEditCreditBase>
      <Formik
        initialValues={{ 
          subscriptionYear: new Date().getFullYear(), 
          subscriptionMonth: new Date().getMonth() + 1,
        }}
        validationSchema={ACCOUNT_SUBSCRIPTION_CREDIT_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          addFinanceInvoice({ variables: {
            input: {
              accountSubscription: subscriptionId,
              financeInvoiceGroup: values.financeInvoiceGroup,
              subscriptionYear: values.subscriptionYear,
              subscriptionMonth: values.subscriptionMonth,
              summary: values.summary,
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
          <AccountSubscriptionEditInvoiceAddForm
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


export default withTranslation()(withRouter(AccountSubscriptionEditFinanceInvoiceAdd))