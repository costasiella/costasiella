// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'

import {
  Dimmer,
  Form,
} from "tabler-react"


let priceFormTypingTimer
const itemSubmitTimeout = 1500

const FormPrice = ({ t, isSubmitting, errors, handleChange, submitForm }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group>
        <Field type="text" 
                name="price" 
                className={(errors.price) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" 
                onChange={(e) => {
                  clearTimeout(priceFormTypingTimer)
                  handleChange(e)
                  priceFormTypingTimer = setTimeout(() => {
                    submitForm()
                  }, itemSubmitTimeout)
                }}
                onKeyDown={() => clearTimeout(priceFormTypingTimer)}
        />
        <ErrorMessage name="price" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FormPrice))