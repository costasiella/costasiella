// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

// import { GET_ACCOUNT_SUBSCRIPTION_QUERY } from "../../queries"
import { GET_FINANCE_INVOICE_ITEM_QUERY, GET_INPUT_VALUES_QUERY } from "./queries"
import { CREATE_ACCOUNT_INVOICE } from "../../../invoices/queries"
import { ACCOUNT_SUBSCRIPTION_INVOICE_SCHEMA } from './yupSchema'

import AccountSubscriptionEditInvoiceAddBase from "./AccountSubscriptionEditInvoiceAddBase"
import AccountSubscriptionEditInvoiceAddForm from "./AccountSubscriptionEditInvoiceAddForm"


function AccountSubscriptionEditInvoiceAdd({ t, history, match }) {
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/invoices/`

  const { loading: queryLoading, error: queryError, data: queryData } = useQuery(GET_INPUT_VALUES_QUERY)

  const [ addFinanceInvoice ] = useMutation(CREATE_ACCOUNT_INVOICE, {
    onCompleted: () => history.push(returnUrl),
  })

    // Loading
    if (queryLoading) return (
      <AccountSubscriptionEditInvoiceAddBase>
        <p>{t('general.loading_with_dots')}</p>
      </AccountSubscriptionEditInvoiceAddBase>
    )
    // Error
    if (queryError) {
      console.log(queryError)
      return (
        <AccountSubscriptionEditInvoiceAddBase>
          <p>{t('general.error_sad_smiley')}</p>
        </AccountSubscriptionEditInvoiceAddBase>
      )
    }
    
    console.log(queryData)

  return (
    <AccountSubscriptionEditInvoiceAddBase>
      <Formik
        initialValues={{ 
          financeInvoiceGroup: "",
          summary: "",
          subscriptionYear: new Date().getFullYear(), 
          subscriptionMonth: new Date().getMonth() + 1,
        }}
        validationSchema={ACCOUNT_SUBSCRIPTION_INVOICE_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log("submit values")
          console.log(values)

          addFinanceInvoice({ variables: {
            input: {
              account: accountId,
              accountSubscription: subscriptionId,
              financeInvoiceGroup: values.financeInvoiceGroup,
              subscriptionYear: values.subscriptionYear,
              subscriptionMonth: values.subscriptionMonth,
              summary: values.summary,
            }
          }, refetchQueries: [
              {query: GET_FINANCE_INVOICE_ITEM_QUERY, variables: {
                accountSubscription: subscriptionId
              }},
              // {query: GET_ACCOUNT_SUBSCRIPTION_QUERY, variables: {
              //   accountId: accountId,
              //   id: subscriptionId
              // }}
          ]})
          .then(({ data }) => {
              console.log('got data', data)
              const financeInvoiceId = data.createFinanceInvoice.financeInvoice.id
              history.push(`/finance/invoices/edit/${financeInvoiceId}`)
              toast.success((t('relations.account.subscriptions.invoices.toast_add_success')), {
                position: toast.POSITION.BOTTOM_RIGHT
              })
              toast.success((t('relations.account.subscriptions.invoices.toast_you_are_now_editing')), {
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
            inputData={queryData}
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
    </AccountSubscriptionEditInvoiceAddBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditInvoiceAdd))