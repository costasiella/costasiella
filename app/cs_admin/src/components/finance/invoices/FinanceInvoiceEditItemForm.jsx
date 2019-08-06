// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'


import {
  Dimmer,
  Form,
} from "tabler-react"


let itemFormTypingTimer


const FinanceInvoiceEditSummaryForm = ({ t, isSubmitting, errors, handleChange, submitForm }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group>
        <Field type="text" 
                name="item" 
                className={(errors.item) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" 
                onChange={(e) => {
                  clearTimeout(itemFormTypingTimer)
                  handleChange(e)
                  itemFormTypingTimer = setTimeout(() => {
                    submitForm()
                  }, 1500)
                }}
                onKeyDown={() => clearTimeout(itemFormTypingTimer)}
                
        />
        <ErrorMessage name="item" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FinanceInvoiceEditSummaryForm))