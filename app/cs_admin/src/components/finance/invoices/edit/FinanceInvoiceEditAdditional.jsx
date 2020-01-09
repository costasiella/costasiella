// @flow

import React from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'


import {
  Card,
  Tab,
  TabbedCard
} from "tabler-react"


import { get_list_query_variables } from "../tools"
import { UPDATE_INVOICE, GET_INVOICES_QUERY } from "../queries"
import FinanceInvoiceEditTermsForm from "./FinanceInvoiceEditTermsForm"
import FinanceInvoiceEditFooterForm from "./FinanceInvoiceEditFooterForm"
import FinanceInvoiceEditNoteForm from "./FinanceInvoiceEditNoteForm"
import FinanceInvoiceEditPayments from "./FinanceInvoiceEditPayments"


const FinanceInvoiceEditAdditional = ({ t, history, match, initialData }) => (
  <TabbedCard initialTab={t('general.terms_and_conditions')}>
    <Tab title={t('general.terms_and_conditions')}>
      <Mutation mutation={UPDATE_INVOICE}> 
        {(updateInvoice, { data }) => (
          <Formik
            initialValues={{ 
              terms: initialData.financeInvoice.terms, 
            }}
            // validationSchema={INVOICE_GROUP_SCHEMA}
            onSubmit={(values, { setSubmitting }) => {
              console.log('submit values:')
              console.log(values)

              updateInvoice({ variables: {
                input: {
                  id: match.params.id,
                  terms: values.terms, 
                }
              }, refetchQueries: [
                  // {query: GET_INVOICES_QUERY, variables: get_list_query_variables()}
              ]})
              .then(({ data }) => {
                  console.log('got data', data)
                  toast.success((t('finance.invoice.toast_edit_terms_success')), {
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
            {({ isSubmitting, errors, values, touched, handleChange, submitForm, setFieldTouched, setFieldValue }) => (
              <FinanceInvoiceEditTermsForm
                isSubmitting={isSubmitting}
                errors={errors}
                values={values}
                handleChange={handleChange}
                submitForm={submitForm}
                setFieldTouched={setFieldTouched}
                setFieldValue={setFieldValue}
              >
              </FinanceInvoiceEditTermsForm>
            )}
          </Formik>
        )}
      </Mutation>
    </Tab>
    <Tab title={t('general.footer')}>
      <Mutation mutation={UPDATE_INVOICE}> 
        {(updateInvoice, { data }) => (
          <Formik
            initialValues={{ 
              footer: initialData.financeInvoice.footer, 
            }}
            // validationSchema={INVOICE_GROUP_SCHEMA}
            onSubmit={(values, { setSubmitting }) => {
              console.log('submit values:')
              console.log(values)

              updateInvoice({ variables: {
                input: {
                  id: match.params.id,
                  footer: values.footer, 
                }
              }, refetchQueries: [
                  // {query: GET_INVOICES_QUERY, variables: get_list_query_variables()}
              ]})
              .then(({ data }) => {
                  console.log('got data', data)
                  toast.success((t('finance.invoice.toast_edit_footer_success')), {
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
            {({ isSubmitting, errors, values, touched, handleChange, submitForm, setFieldTouched, setFieldValue }) => (
              <FinanceInvoiceEditFooterForm
                isSubmitting={isSubmitting}
                errors={errors}
                values={values}
                handleChange={handleChange}
                submitForm={submitForm}
                setFieldTouched={setFieldTouched}
                setFieldValue={setFieldValue}
              >
              </FinanceInvoiceEditFooterForm>
            )}
          </Formik>
        )}
      </Mutation>
    </Tab>
    <Tab title={t('general.note')}>
    <Mutation mutation={UPDATE_INVOICE}> 
        {(updateInvoice, { data }) => (
          <Formik
            initialValues={{ 
              note: initialData.financeInvoice.note, 
            }}
            // validationSchema={INVOICE_GROUP_SCHEMA}
            onSubmit={(values, { setSubmitting }) => {
              console.log('submit values:')
              console.log(values)

              updateInvoice({ variables: {
                input: {
                  id: match.params.id,
                  note: values.note, 
                }
              }, refetchQueries: [
                  // {query: GET_INVOICES_QUERY, variables: get_list_query_variables()}
              ]})
              .then(({ data }) => {
                  console.log('got data', data)
                  toast.success((t('finance.invoice.toast_edit_note_success')), {
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
            {({ isSubmitting, errors, values, touched, handleChange, submitForm, setFieldTouched, setFieldValue }) => (
              <FinanceInvoiceEditNoteForm
                isSubmitting={isSubmitting}
                errors={errors}
                values={values}
                handleChange={handleChange}
                submitForm={submitForm}
                setFieldTouched={setFieldTouched}
                setFieldValue={setFieldValue}
              >
              </FinanceInvoiceEditNoteForm>
            )}
          </Formik>
        )}
      </Mutation>
    </Tab>
    <Tab title={t('general.payments')}>
      <FinanceInvoiceEditPayments inputData={initialData} />
    </Tab>
  </TabbedCard>
  // <Card statusColor="blue">
  //   <Card.Header>
  //     <Card.Title>{t('general.summary')}</Card.Title>
  //   </Card.Header>
  //   <Card.Body>

  //   </Card.Body>
  // </Card>
)

export default withTranslation()(withRouter(FinanceInvoiceEditAdditional))