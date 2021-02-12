// @flow

import React, { Component } from 'react'
import gql from "graphql-tag"
import { Query, Mutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'
import moment from 'moment'


import {
  Card, 
  Form
} from "tabler-react"


import { dateToLocalISO } from '../../../../tools/date_tools'
import { get_list_query_variables } from "../tools"
import { UPDATE_INVOICE, GET_INVOICES_QUERY } from "../queries"
import FinanceInvoiceEditOptionsForm from "./FinanceInvoiceEditOptionsForm"


class FinanceInvoiceEditOptions extends Component {
  constructor(props) {
    super(props)
    console.log("finance invoice edit options props:")
    console.log(props)
  }

  render() {
    const t = this.props.t
    const match = this.props.match
    const initialData = this.props.initialData

    let initialPaymentMethod = ""
    if (initialData.financeInvoice.financePaymentMethod) {
      initialPaymentMethod = initialData.financeInvoice.financePaymentMethod.id
    }


    return (
      <Card statusColor="blue">
        <Card.Header>
          <Card.Title>{t('general.options')}</Card.Title>
        </Card.Header>
        <Card.Body>
          <Mutation mutation={UPDATE_INVOICE}> 
            {(updateInvoice, { data }) => (
              <Formik
                initialValues={{ 
                  invoiceNumber: initialData.financeInvoice.invoiceNumber, 
                  dateSent: initialData.financeInvoice.dateSent,
                  dateDue: initialData.financeInvoice.dateDue,
                  status: initialData.financeInvoice.status,
                  financePaymentMethod: initialPaymentMethod
                }}
                // validationSchema={INVOICE_GROUP_SCHEMA}
                onSubmit={(values, { setSubmitting }) => {
                  console.log('submit values:')
                  console.log(values)
    
                  updateInvoice({ variables: {
                    input: {
                      id: match.params.id,
                      invoiceNumber: values.invoiceNumber, 
                      dateSent: dateToLocalISO(values.dateSent),
                      dateDue: dateToLocalISO(values.dateDue),
                      status: values.status,
                      financePaymentMethod: values.financePaymentMethod,
                    }
                  }, refetchQueries: [
                      {query: GET_INVOICES_QUERY, variables: get_list_query_variables()}
                  ]})
                  .then(({ data }) => {
                      console.log('got data', data)
                      toast.success((t('finance.invoice.toast_edit_options_success')), {
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
                  <FinanceInvoiceEditOptionsForm
                    inputData={initialData}
                    isSubmitting={isSubmitting}
                    errors={errors}
                    values={values}
                    handleChange={handleChange}
                    submitForm={submitForm}
                    setFieldValue={setFieldValue}
                    setFieldTouched={setFieldTouched}
                  >
                  </FinanceInvoiceEditOptionsForm>
                )}
              </Formik>
            )}
          </Mutation>
          {/* <Form.Label>
            {t('general.last_updated_at')}
          </Form.Label>
            {moment(initialData.financeInvoice.updatedAt).format('LL')} */}
        </Card.Body>
      </Card>
    )
  }
}

export default withTranslation()(withRouter(FinanceInvoiceEditOptions))