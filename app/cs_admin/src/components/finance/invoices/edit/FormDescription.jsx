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

import { handleTextInputBlur } from './tools'


const FormDescription = ({ t, isSubmitting, errors, handleChange, submitForm }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group>
        <Field type="text" 
                name="description" 
                className={(errors.description) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" 
                component="textarea"
                onBlur={(e) => { 
                  handleTextInputBlur(e, handleChange, submitForm)
                }}
        />
        <ErrorMessage name="description" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FormDescription))