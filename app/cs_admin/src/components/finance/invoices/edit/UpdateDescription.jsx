// @flow

import React from 'react'
import { useMutation } from '@apollo/react-hooks';
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { get_list_query_variables } from "../tools"
import { UPDATE_INVOICE_ITEM } from "../queries"
import FormDescription from "./FormDescription"


function UpdateDescription({t, initialValues}) {
  const [updateInvoiceItem, { data }] = useMutation(UPDATE_INVOICE_ITEM)

    return (
      <Formik
        initialValues={{
          description: initialValues.description
        }}
        // validationSchema={INVOICE_GROUP_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log('submit values:')
          console.log(values)

          updateInvoiceItem({ variables: {
            input: {
              id: initialValues.id,
              description: values.description, 
            }
          }, refetchQueries: [
              // {query: GET_INVOICE_QUERY, variables: {id: match.params.id}}
          ]})
          .then(({ data }) => {
              console.log('got data', data)
              toast.success((t('finance.invoice.toast_edit_item_description_success')), {
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
        {({ isSubmitting, errors, values, handleChange, submitForm }) => (
          <FormDescription
            isSubmitting={isSubmitting}
            errors={errors}
            values={values}
            handleChange={handleChange}
            submitForm={submitForm}
          >
          </FormDescription>   
        )}
      </Formik>
    )
}


export default withTranslation()(withRouter(UpdateDescription))