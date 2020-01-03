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

import { handleTextInputBlur } from './tools'


const FormFinanceTaxRate = ({ t, isSubmitting, errors, submitForm, inputData, handleChange }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group>
        <Field component="select" 
              name="financeTaxRate" 
              className={(errors.financeTaxRate) ? "form-control is-invalid" : "form-control"} 
              autoComplete="off"
              onBlur={(e) => { 
                handleTextInputBlur(e, handleChange, submitForm)
              }}
        >
          {console.log("query data in form finance tax rate:")}
          {console.log(inputData)}
          <option value="" key={v4()}></option>
          {inputData.financeTaxRates.edges.map(({ node }) =>
            <option value={node.id} key={v4()}>{node.name} ({node.percentage}% {node.rateType})</option>
          )}
        </Field>
        <ErrorMessage name="financeTaxRate" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FormFinanceTaxRate))