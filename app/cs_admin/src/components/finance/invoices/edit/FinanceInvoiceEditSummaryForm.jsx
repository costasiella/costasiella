// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'


import {
  Dimmer,
  Form,
} from "tabler-react"


let summaryFormTypingTimer
const formSubmitTimeout = 750


const FinanceInvoiceEditSummaryForm = ({ t, isSubmitting, errors, handleChange, submitForm }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group>
        <Field type="text" 
                name="summary" 
                className={(errors.summary) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" 
                onChange={(e) => {
                  clearTimeout(summaryFormTypingTimer)
                  handleChange(e)
                  summaryFormTypingTimer = setTimeout(() => {
                    submitForm()
                  }, formSubmitTimeout)
                }}
                onKeyDown={() => clearTimeout(summaryFormTypingTimer)}
                
        />
        <ErrorMessage name="summary" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FinanceInvoiceEditSummaryForm))