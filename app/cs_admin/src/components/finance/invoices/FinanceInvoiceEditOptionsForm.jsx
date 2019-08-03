// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'


import {
  Dimmer,
  Form,
} from "tabler-react"


let optionsFormTypingTimer


const FinanceInvoiceEditOptionsForm = ({ t, isSubmitting, errors, handleChange, submitForm }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group label={t('finance.invoices.invoice_number')}>
        <Field type="text" 
                name="invoiceNumber" 
                className={(errors.invoiceNumber) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" 
                onChange={(e) => {
                  clearTimeout(optionsFormTypingTimer)
                  handleChange(e)
                  optionsFormTypingTimer = setTimeout(() => {
                    submitForm()
                  }, 2000)
                }}
                onKeyDown={() => clearTimeout(optionsFormTypingTimer)}
                
        />
        <ErrorMessage name="invoiceNumber" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FinanceInvoiceEditOptionsForm))