// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { ADD_PAYMENT_BATCH, GET_PAYMENT_BATCHES_QUERY, GET_INPUT_VALUES } from './queries'
import { PAYMENT_BATCH_INVOICES_SCHEMA, PAYMENT_BATCH_CATEGORY_SCHEMA } from './yupSchema'
import { get_list_query_variables } from "./tools"


import {
  Dimmer,
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react"
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
import { dateToLocalISO } from '../../../tools/date_tools'

import FinanceMenu from '../FinanceMenu'
import FinancePaymentBatchesBase from './FinancePaymentBatchesBase'
import FinancePaymentCollectionBatchForm from './FinancePaymentCollectionBatchForm'


function FinancePaymentCollectionBatchAdd({ t, history, match }) {
  const batchType = match.params.batch_type
  const returnUrl = `/finance/paymentbatches/${batchType}`
  const categoryType = match.params.category_type
  const cardTitle = t('finance.payment_batch.title_add')


  let invoices = false
  let category = false
  switch (categoryType) {
    case "invoices":
      invoices = true
      break
    case "category":
      category = true
      break
    default:
      break
  }

  let batchCategoryType
  switch (batchType) {
    case "collection":
      batchCategoryType = "COLLECTION"
      break
    case "payment":
      batchCategoryType = "PAYMENT"
      break
    default:
      break
  }

  const { loading, error, data } = useQuery(GET_INPUT_VALUES, { variables: {
    batchCategoryType: batchCategoryType
  }})
  const [addFinancePaymentBatch] = useMutation(ADD_PAYMENT_BATCH)

  // Loading
  if (loading) return (
    <FinancePaymentBatchesBase showAdd={true}>
      <Card cardTitle={cardTitle}>
        <Dimmer active={true}
                loader={true}>
        </Dimmer>
      </Card>
    </FinancePaymentBatchesBase>
  )
  // Error
  if (error) return (
    <FinancePaymentBatchesBase showAdd={true}>
      <Card cardTitle={cardTitle}>
        <p>{t('finance.payment_batches.error_loading_input_values')}</p>
      </Card>
      </FinancePaymentBatchesBase>
  )

  const inputData = data

  let initialValues = { name: '', description: '', executionDate: new Date() }
  let yupSchema
  if (categoryType == "category") {
    initialValues.year = new Date().getFullYear()
    initialValues.month = new Date().getMonth() + 1
    yupSchema = PAYMENT_BATCH_CATEGORY_SCHEMA
  } else {
    yupSchema = PAYMENT_BATCH_INVOICES_SCHEMA
  }

  return (
    <FinancePaymentBatchesBase showBack={true}>
      <Card>
        <Card.Header>
          <Card.Title>{cardTitle}</Card.Title>
        </Card.Header>
        <Formik
          initialValues={initialValues}
          validationSchema={yupSchema}
          onSubmit={(values, { setSubmitting }) => {
            let input = {
                batchType: batchType.toUpperCase(),
                name: values.name, 
                executionDate: dateToLocalISO(values.executionDate),
                description: values.description,
                note: values.note,
                includeZeroAmounts: values.includeZeroAmounts
            }

            if (categoryType == "category") {
              input.year = values.year
              input.month = values.month
              input.financePaymentBatchCategory = values.financePaymentBatchCategory
            }

            addFinancePaymentBatch({ 
              variables: { input: input }, 
              refetchQueries: [
                {query: GET_PAYMENT_BATCHES_QUERY, variables: get_list_query_variables(batchType)}
            ]})
            .then(({ data }) => {
                console.log('got data', data);
                const id = data.createFinancePaymentBatch.financePaymentBatch.id
                history.push(`/finance/paymentbatches/${batchType}/view/${id}`)
                toast.success((t('finance.payment_batches.toast_add_success')), {
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
          {({ isSubmitting, errors, values, setFieldValue, setFieldTouched }) => (
              <FinancePaymentCollectionBatchForm
                inputData={inputData}
                create={true}
                invoices={invoices}
                category={category}
                isSubmitting={isSubmitting}
                setFieldTouched={setFieldTouched}
                setFieldValue={setFieldValue}
                values={values}
                errors={errors}
                returnUrl={returnUrl}
              />
          )}
        </Formik>
      </Card>
    </FinancePaymentBatchesBase>
  )
}

export default withTranslation()(withRouter(FinancePaymentCollectionBatchAdd))