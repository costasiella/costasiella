// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo"
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import {
  Card,
} from "tabler-react"

import { get_list_query_variables } from "../tools"

import { GET_INVOICE_QUERY, GET_INVOICES_QUERY } from "../queries"
import { GET_INVOICE_PAYMENT_QUERY } from './queries'
import { FINANCE_INVOICE_PAYMENT_SCHEMA } from './yupSchema'
// import ScheduleClassPriceForm from './ScheduleClassPriceForm'
import { dateToLocalISO } from '../../../../tools/date_tools'

import SiteWrapper from "../../../SiteWrapper"

import FinanceInvoicePaymentBase from "./FinanceInvoicePaymentBase"
import FinanceInvoicePaymentForm from "./FinanceInvoicePaymentForm"


const UPDATE_FINANCE_INVOICE_PAYMENT = gql`
  mutation UpdateFinanceInvoicePayment($input:UpdateFinanceInvoicePaymentInput!) {
    updateFinanceInvoicePayment(input:$input) {
      financeInvoicePayment {
        id
      } 
    }
  }
`


function FinanceInvoicePaymentEdit({ t, history, match }) {
  const invoiceId = match.params.invoice_id
  const id = match.params.id
  console.log(invoiceId)
  console.log(id)

  const return_url = "/finance/invoices/edit/" + invoiceId
  const { loading: invoiceQueryLoading, error: invoiceQueryError, data: invoiceData, } = useQuery(GET_INVOICE_QUERY, {
    variables: {
      id: invoiceId
    }
  })
  const { loading: paymentQueryLoading, error: paymentQueryError, data: paymentData, } = useQuery(GET_INVOICE_PAYMENT_QUERY, {
    variables: {
      id: id
    }
  })
  const [updateInvoicePayment, { mutationData, mutationLoading, mutationError, onCompleted }] = useMutation(UPDATE_FINANCE_INVOICE_PAYMENT, {
    onCompleted: () => history.push(return_url),
  })

  if (invoiceQueryLoading || paymentQueryLoading) return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <p>{t('general.loading_with_dots')}</p>
      </div>
    </SiteWrapper>
  )
  // Error
  if (invoiceQueryError) {
    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          { console.log(invoiceQueryError) }
          <p>{t('general.error_sad_smiley')}</p>
        </div>
      </SiteWrapper>
    )
  }
  // Error
  if (paymentQueryError) {
    return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          { console.log(paymentQueryError) }
          <p>{t('general.error_sad_smiley')}</p>
        </div>
      </SiteWrapper>
    )
  }

  console.log('query data')
  console.log(invoiceData)
  console.log(paymentData)
  const inputData = invoiceData
  const initialValues = paymentData.financeInvoicePayment

  let initialPaymentMethod
  if (initialValues.financePaymentMethod) {
    initialPaymentMethod = initialValues.financePaymentMethod.id
  }

  return (
    <FinanceInvoicePaymentBase form_type={"update"}>
      <Formik
        initialValues={{ 
          date: initialValues.date,
          amount: initialValues.amount,
          financePaymentMethod: initialPaymentMethod,
          note: initialValues.note
        }}
        // validationSchema={FINANCE_INVOICE_PAYMENT_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
            updateInvoicePayment({ variables: {
              input: {
                id: id,
                date: dateToLocalISO(values.date),
                amount: values.amount,
                financePaymentMethod: values.financePaymentMethod,
                note: values.note
              }
            }, refetchQueries: [
                {query: GET_INVOICES_QUERY, variables: get_list_query_variables() },
                {query: GET_INVOICE_QUERY, variables: { id: invoiceId }},
            ]})
            .then(({ data }) => {
                console.log('got data', data);
                toast.success((t('finance.invoice.payments.toast_edit_success')), {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
              }).catch((error) => {
                toast.error((t('general.toast_server_error')) + ': ' +  error, {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                console.log('there was an error sending the query', error)
                setSubmitting(false)
              })
          }
        }
        >
        {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
          <FinanceInvoicePaymentForm
            inputData={inputData}
            isSubmitting={isSubmitting}
            setFieldTouched={setFieldTouched}
            setFieldValue={setFieldValue}
            errors={errors}
            values={values}
            return_url={return_url}
          />
        )}
      </Formik>
    </FinanceInvoicePaymentBase>
  )
}


export default withTranslation()(withRouter(FinanceInvoicePaymentEdit))