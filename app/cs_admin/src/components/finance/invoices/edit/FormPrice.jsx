// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'

import {
  Dimmer,
  Form,
} from "tabler-react"


import { handleTextInputBlur } from './tools'

const FormPrice = ({ t, isSubmitting, errors, handleChange, submitForm }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group>
        <Field type="text" 
                name="price" 
                className={(errors.price) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" 
                onBlur={(e) => { 
                  handleTextInputBlur(e, handleChange, submitForm)
                }}
        />
        <ErrorMessage name="price" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FormPrice))