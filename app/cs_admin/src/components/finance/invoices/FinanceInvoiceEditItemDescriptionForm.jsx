// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from 'uuid'

import {
  Dimmer,
  Form,
  Table
} from "tabler-react"


let itemDescriptionFormTypingTimer
const itemSubmitTimeout = 1500

const FinanceInvoiceEditItemDescriptionForm = ({ t, isSubmitting, errors, handleChange, submitForm }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group>
        <Field type="text" 
                name="description" 
                className={(errors.description) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" 
                component="textarea"
                onChange={(e) => {
                  clearTimeout(itemDescriptionFormTypingTimer)
                  handleChange(e)
                  itemDescriptionFormTypingTimer = setTimeout(() => {
                    submitForm()
                  }, itemSubmitTimeout)
                }}
                onKeyDown={() => clearTimeout(itemDescriptionFormTypingTimer)}
        />
        <ErrorMessage name="description" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FinanceInvoiceEditItemDescriptionForm))