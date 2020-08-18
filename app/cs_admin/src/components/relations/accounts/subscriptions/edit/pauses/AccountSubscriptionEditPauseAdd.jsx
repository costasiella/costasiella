// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ACCOUNT_SUBSCRIPTION_PAUSES_QUERY } from "../queries"
import { FINANCE_INVOICE_PAYMENT_SCHEMA } from './yupSchema'
import { dateToLocalISO } from '../../../../tools/date_tools'

import AccountSubscriptionEditPauseBase from "./AccountSubscriptionEditPauseBase"
import AccountSubscriptionEditPauseForm from "./AccountSubscriptionEditPauseForm"


const ADD_ACCOUNT_SUBSCRIPTION_PAUSE = gql`
  mutation CreateAccountSubscriptionPause($input:CreateAccountSubscriptionPauseInput!) {
    createAccountSubscriptionPause(input: $input) {
      accountSubscriptionPause {
        id
        accountSubscription {
          id
        }
        dateStart
        dateEnd
        description
      }
    }
  }
`


function AccountSubscriptionEditPauseAdd({ t, history, match }) {
  const id = match.params.subscription_id
  const accountId = match.params.account_id
  const subscriptionId = match.params.subscription_id
  const returnUrl = `/relations/accounts/${accountId}/subscriptions/edit/${subscriptionId}/pauses/`
  const activeTab = "pauses"

  // const invoiceId = match.params.invoice_id
  // const return_url = "/finance/invoices/edit/" + invoiceId
  // const { loading: queryLoading, error: queryError, data, } = useQuery(GET_INVOICE_QUERY, {
  //   variables: {
  //     id: invoiceId
  //   }
  // })
  const [addInvoicePayment, { mutationData, mutationLoading, mutationError, onCompleted }] = useMutation(ADD_ACCOUNT_SUBSCRIPTION_PAUSE, {
    onCompleted: () => history.push(returnUrl),
  })

  // if (queryLoading) return (
  //   <AccountSubscriptionEditPauseBase>
  //       <p>{t('general.loading_with_dots')}</p>
  //   </AccountSubscriptionEditPauseBase>
  // )
  // // Error
  // if (queryError) {
  //   return (
  //     <AccountSubscriptionEditPauseBase>
  //         { console.log(queryError) }
  //         <p>{t('general.error_sad_smiley')}</p>
  //     </AccountSubscriptionEditPauseBase>
  //   )
  // }

  // console.log('query data')
  // console.log(data)
  // const inputData = data

  return (
    <AccountSubscriptionEditPauseBase formType={"create"}>
      <Formik
        initialValues={{ 
          dateStart: new Date() ,
          description: ""
        }}
        // validationSchema={FINANCE_INVOICE_PAYMENT_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
            addInvoicePayment({ variables: {
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
            return_url={return_url}
          />
        )}
      </Formik>
    </AccountSubscriptionEditPauseBase>
  )
}


export default withTranslation()(withRouter(AccountSubscriptionEditPauseAdd))