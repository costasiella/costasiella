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


let itemFormTypingTimer
const itemSubmitTimeout = 1500

const FormProductName = ({ t, isSubmitting, errors, handleChange, submitForm }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group>
        <Field type="text" 
                name="productName" 
                className={(errors.productName) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" 
                onChange={(e) => {
                  clearTimeout(itemFormTypingTimer)
                  handleChange(e)
                  itemFormTypingTimer = setTimeout(() => {
                    submitForm()
                  }, itemSubmitTimeout)
                }}
                onKeyDown={() => clearTimeout(itemFormTypingTimer)}
        />
        <ErrorMessage name="productName" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FormProductName))