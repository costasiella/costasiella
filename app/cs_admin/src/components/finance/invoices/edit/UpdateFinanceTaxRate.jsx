// @flow

import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { get_list_query_variables } from "../tools"
import { UPDATE_INVOICE_ITEM, GET_INVOICES_QUERY, GET_INVOICE_QUERY } from "../queries"
import FormFinanceTaxRate from "./FormFinanceTaxRate"


function get_initial_tax_rate(node) {
    let initialValues = {}

    if (node.financeTaxRate) {
      initialValues.financeTaxRate = node.financeTaxRate.id
    }

    return initialValues
}


function UpdateFinanceTaxRate({t, match, initialValues, inputData}) {
  const [updateInvoiceItem, { data }] = useMutation(UPDATE_INVOICE_ITEM)

    return (
      <Formik
        initialValues={get_initial_tax_rate(initialValues)}
        // validationSchema={INVOICE_GROUP_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log('submit values:')
          console.log(values)

          updateInvoiceItem({ variables: {
            input: {
              id: initialValues.id,
              financeTaxRate: values.financeTaxRate, 
            }
          }, refetchQueries: [
            {query: GET_INVOICES_QUERY, variables: get_list_query_variables()},
            {query: GET_INVOICE_QUERY, variables: {id: match.params.id}}
          ]})
          .then(({ data }) => {
              console.log('got data', data)
              toast.success((t('finance.invoice.toast_edit_item_financeTaxRate_success')), {
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
        {({ isSubmitting, errors, values, submitForm, handleChange }) => (
          <FormFinanceTaxRate
            inputData={inputData}
            isSubmitting={isSubmitting}
            errors={errors}
            values={values}
            submitForm={submitForm}
            handleChange={handleChange}
          >
          </FormFinanceTaxRate>   
        )}
      </Formik>
    )
}


export default withTranslation()(withRouter(UpdateFinanceTaxRate))