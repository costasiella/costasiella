// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from "uuid"

import {
  Button,
  Card,
  Form,
  Grid,
} from "tabler-react"


const FinanceInvoiceGroupDefaultForm = ({ t, history, inputData, isSubmitting, setFieldTouched, setFieldValue, errors, values, submitForm }) => (
  <FoForm>
    <Form.Group label={t('finance.invoice_groups_defaults.default_group')}>
      <Field component="select" 
            name="financeInvoiceGroup" 
            className={(errors.financeInvoiceGroup) ? "form-control is-invalid" : "form-control"} 
            // value={values.financeInvoiceGroup}
            onChange={() => {
              // setFieldValue('financeInvoiceGroup', values.financeInvoiceGroup)
              // setFieldTouched('financeInvoiceGroup', true)
              setTimeout(() => {submitForm()}, 200)
            }}
            autoComplete="off">
        {inputData.financeInvoiceGroups.edges.map(({ node }) =>
          <option value={node.id} key={v4()}>{node.name}</option>
        )}
      </Field>
      <ErrorMessage name="financeInvoiceGroup" component="span" className="invalid-feedback" />
    </Form.Group>  
  </FoForm>
)

export default withTranslation()(withRouter(FinanceInvoiceGroupDefaultForm))