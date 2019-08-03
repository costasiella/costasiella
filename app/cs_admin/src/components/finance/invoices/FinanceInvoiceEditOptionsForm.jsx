// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from 'uuid'

import {
  Dimmer,
  Form,
} from "tabler-react"


let optionsFormTypingTimer


const FinanceInvoiceEditOptionsForm = ({ t, isSubmitting, errors, handleChange, submitForm, setFieldValue, setFieldTouched, inputData }) => (
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
      <Form.Group label={t('general.status')}>
        <Field component="select" 
              name="status" 
              className={(errors.status) ? "form-control is-invalid" : "form-control"} 
              autoComplete="off"
              onChange={(e) => {
                setFieldValue('status', e.target.value)
                setFieldTouched('status', true)
                setTimeout(() => {submitForm()}, 200)
              }}
        >
          <option value="DRAFT">{t('finance.invoices.status.DRAFT')}</option>
          <option value="SENT">{t('finance.invoices.status.SENT')}</option>
          <option value="PAID">{t('finance.invoices.status.PAID')}</option>
          <option value="CANCELLED">{t('finance.invoices.status.CANCELLED')}</option>
        </Field>
        <ErrorMessage name="status" component="span" className="invalid-feedback" />
      </Form.Group>
      <Form.Group label={t('general.payment_method')}>
        <Field component="select" 
              name="financePaymentMethod" 
              className={(errors.financePaymentMethod) ? "form-control is-invalid" : "form-control"} 
              onChange={(e) => {
                setFieldValue('financePaymentMethod', e.target.value)
                setFieldTouched('financePaymentMethod', true)
                setTimeout(() => {submitForm()}, 200)
              }}
              autoComplete="off">
          <option value="" key={v4()}></option>
          {inputData.financePaymentMethods.edges.map(({ node }) =>
            <option value={node.id} key={v4()}>{node.name}</option>
          )}
        </Field>
        <ErrorMessage name="financePaymentMethod" component="span" className="invalid-feedback" />
      </Form.Group>  
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FinanceInvoiceEditOptionsForm))