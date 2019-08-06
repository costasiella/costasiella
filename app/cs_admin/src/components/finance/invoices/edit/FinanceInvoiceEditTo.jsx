// @flow

import React from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import {
  Card
} from "tabler-react"


import { get_list_query_variables } from "../tools"
import { UPDATE_INVOICE, GET_INVOICES_QUERY } from "../queries"
import FinanceInvoiceEditToForm from "./FinanceInvoiceEditToForm"


const FinanceInvoiceEditTo = ({ t, history, match, initialData }) => (
  <Card statusColor="blue">
    <Card.Header>
      <Card.Title>{t('general.to')}</Card.Title>
    </Card.Header>
    <Card.Body>
      <Mutation mutation={UPDATE_INVOICE}> 
        {(updateInvoice, { data }) => (
          <Formik
            initialValues={{ 
              relationCompany: initialData.financeInvoice.relationCompany, 
              relationCompanyRegistration: initialData.financeInvoice.relationCompanyRegistration, 
              relationCompanyTaxRegistration: initialData.financeInvoice.relationCompanyTaxRegistration, 
              relationContactName: initialData.financeInvoice.relationContactName, 
              relationAddress: initialData.financeInvoice.relationAddress, 
              relationPostcode: initialData.financeInvoice.relationPostcode, 
              relationCity: initialData.financeInvoice.relationCity, 
              relationCountry: initialData.financeInvoice.relationCountry, 
            }}
            // validationSchema={INVOICE_GROUP_SCHEMA}
            onSubmit={(values, { setSubmitting }) => {
              console.log('submit values:')
              console.log(values)

              updateInvoice({ variables: {
                input: {
                  id: match.params.id,
                  relationCompany: values.relationCompany,
                  relationCompanyRegistration: values.relationCompanyRegistration,
                  relationCompanyTaxRegistration: values.relationCompanyTaxRegistration,
                  relationContactName: values.relationContactName,
                  relationAddress: values.relationAddress,
                  relationPostcode: values.relationPostcode,
                  relationCity: values.relationCity,
                  relationCountry: values.relationCountry
                }
              }, refetchQueries: [
                  {query: GET_INVOICES_QUERY, variables: get_list_query_variables()}
              ]})
              .then(({ data }) => {
                  console.log('got data', data)
                  toast.success((t('finance.invoice.toast_edit_to_success')), {
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
            {({ isSubmitting, errors, values, touched, handleChange, submitForm }) => (
              <FinanceInvoiceEditToForm
                isSubmitting={isSubmitting}
                errors={errors}
                values={values}
                handleChange={handleChange}
                submitForm={submitForm}
              >
              </FinanceInvoiceEditToForm>
            )}
          </Formik>
        )}
      </Mutation>
    </Card.Body>
  </Card>
)

export default withTranslation()(withRouter(FinanceInvoiceEditTo))