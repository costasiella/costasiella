// @flow

import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import { get_list_query_variables } from "../tools"
import { UPDATE_INVOICE_ITEM } from "../queries"
import FormProductName from "./FormProductName"


function UpdateProductName({t, initialValues}) {
  const [updateInvoiceItem, { data }] = useMutation(UPDATE_INVOICE_ITEM)

    return (
      <Formik
        initialValues={{
          productName: initialValues.productName
        }}
        // validationSchema={INVOICE_GROUP_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log('submit values:')
          console.log(values)

          updateInvoiceItem({ variables: {
            input: {
              id: initialValues.id,
              productName: values.productName, 
            }
          }, refetchQueries: [
              // {query: GET_INVOICES_QUERY, variables: get_list_query_variables()}
          ]})
          .then(({ data }) => {
              console.log('got data', data)
              toast.success((t('finance.invoice.toast_edit_item_product_name_success')), {
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
        {({ isSubmitting, errors, values, touched, handleChange, submitForm, setFieldValue, setFieldTouched }) => (
          <FormProductName
            isSubmitting={isSubmitting}
            errors={errors}
            values={values}
            handleChange={handleChange}
            submitForm={submitForm}
            key={"invoice_item_product_name" + initialValues.id} // don't use uuid here, during re-render it causes the inputs to lose focus while typing due to a different key
          >
          </FormProductName>   
        )}
      </Formik>
    )
}


export default withTranslation()(withRouter(UpdateProductName))