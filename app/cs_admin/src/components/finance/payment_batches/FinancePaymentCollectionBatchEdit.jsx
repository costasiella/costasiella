// @flow

import React from 'react'
import { useQuery, useMutation } from "react-apollo";
import gql from "graphql-tag"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { UPDATE_PAYMENT_BATCH, GET_PAYMENT_BATCH_QUERY, GET_PAYMENT_BATCHES_QUERY } from './queries'
import { PAYMENT_BATCH_EDIT_SCHEMA } from './yupSchema'
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


function FinancePaymentCollectionBatchEdit({ t, history, match }) {
  const batchType = match.params.batch_type
  const batchId = match.params.id
  const returnUrl = `/finance/paymentbatches/${batchType}/view/${batchId}`
  const cardTitle = t('finance.payment_batch.title_edit')


  const { loading, error, data } = useQuery(GET_PAYMENT_BATCH_QUERY, {
    variables: { id: batchId }
  })
  const [updateFinancePaymentBatch] = useMutation(UPDATE_PAYMENT_BATCH)

  // Loading
  if (loading) return (
    <FinancePaymentBatchesBase showAdd={false} returnUrl={returnUrl}>
      <Card title={cardTitle}>
        <Card.Body>
          <Dimmer active={true} loader={true} />
        </Card.Body>
      </Card>
    </FinancePaymentBatchesBase>
  )
  // Error
  if (error) return (
    <FinancePaymentBatchesBase showAdd={true} returnUrl={returnUrl}>
      <Card title={cardTitle}>
        <p>{t('finance.payment_batches.error_loading_input_values')}</p>
      </Card>
      </FinancePaymentBatchesBase>
  )

  const inputValues = data.financePaymentBatch

  return (
    <FinancePaymentBatchesBase showBack={true} returnUrl={returnUrl}>
      <Card>
        <Card.Header>
          <Card.Title>{cardTitle}</Card.Title>
        </Card.Header>
        <Formik
          initialValues={{ name: inputValues.name , note: inputValues.note }}
          validationSchema={PAYMENT_BATCH_EDIT_SCHEMA}
          onSubmit={(values, { setSubmitting }) => {
            let input = {
                id: batchId,
                name: values.name, 
                note: values.note,
            }

            updateFinancePaymentBatch({ 
              variables: { input: input }, 
              refetchQueries: [
                {query: GET_PAYMENT_BATCHES_QUERY, variables: get_list_query_variables(batchType)}
            ]})
            .then(({ data }) => {
                console.log('got data', data);
                toast.success((t('finance.payment_batches.toast_edit_success')), {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                setSubmitting(false)
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
                create={false}
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

export default withTranslation()(withRouter(FinancePaymentCollectionBatchEdit))