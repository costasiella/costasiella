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

import { handleTextInputChange, handleTextInputBlur } from './tools'


const FormProductName = ({ t, isSubmitting, errors, handleChange, submitForm }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group>
        <Field type="text" 
                name="productName" 
                className={(errors.productName) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" 
                onChange={(e) => {
                  handleTextInputChange(e, handleChange, submitForm)
                }}
                onBlur={(e) => { 
                  handleTextInputBlur(e, handleChange, submitForm)
                }}
        />
        <ErrorMessage name="productName" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FormProductName))