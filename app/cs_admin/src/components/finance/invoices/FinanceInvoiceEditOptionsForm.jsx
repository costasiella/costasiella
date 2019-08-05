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

import CSDatePicker from "../../ui/CSDatePicker"


let optionsFormTypingTimer
const formSubmitTimeout = 1500


const FinanceInvoiceEditOptionsForm = ({ t, isSubmitting, values, errors, handleChange, submitForm, setFieldValue, setFieldTouched, inputData }) => (
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
                  }, formSubmitTimeout)
                }}
                onKeyDown={() => clearTimeout(optionsFormTypingTimer)}
                
        />
        <ErrorMessage name="invoiceNumber" component="span" className="invalid-feedback" />
      </Form.Group>
      <Form.Group label={t('finance.invoices.date')}>
        <CSDatePicker 
          className={(errors.dateSent) ? "form-control is-invalid" : "form-control"} 
          selected={values.dateSent}
          onChange={(date) => {
            setFieldValue("dateSent", date)
            setFieldTouched("dateSent", true)
            setTimeout(() => {submitForm()}, formSubmitTimeout)
          }}
          onBlur={() => setFieldTouched("dateSent", true)}
        />
        <ErrorMessage name="dateSent" component="span" className="invalid-feedback" />
      </Form.Group>
      <Form.Group label={t('finance.invoices.due')}>
        <CSDatePicker 
          className={(errors.dateDue) ? "form-control is-invalid" : "form-control"} 
          selected={values.dateDue}
          onChange={(date) => {
            setFieldValue("dateDue", date)
            setFieldTouched("dateDue", true)
            setTimeout(() => {submitForm()}, formSubmitTimeout)
          }}
          onBlur={() => setFieldTouched("dateDue", true)}
        />
        <ErrorMessage name="dateDue" component="span" className="invalid-feedback" />
      </Form.Group>
      <Form.Group label={t('general.status')}>
        <Field component="select" 
              name="status" 
              className={(errors.status) ? "form-control is-invalid" : "form-control"} 
              autoComplete="off"
              onChange={(e) => {
                setFieldValue('status', e.target.value)
                setFieldTouched('status', true)
                setTimeout(() => {submitForm()}, formSubmitTimeout)
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
                setTimeout(() => {submitForm()}, formSubmitTimeout)
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