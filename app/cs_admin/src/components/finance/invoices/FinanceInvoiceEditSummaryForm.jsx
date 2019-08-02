// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { Link } from 'react-router-dom'


import {
  Button,
  Card,
  Dimmer,
  Form,
  Grid,
} from "tabler-react"



const FinanceInvoiceEditSummaryForm = ({ t, history, isSubmitting, setFieldTouched, setFieldValue, errors, values, return_url, edit=false }) => (
  <Dimmer loader={true} active={isSubmitting}>
    <FoForm>
        <Form.Group>
          <Field type="text" 
                  name="summary" 
                  className={(errors.summary) ? "form-control is-invalid" : "form-control"} 
                  autoComplete="off" />
          <ErrorMessage name="summary" component="span" className="invalid-feedback" />
        </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FinanceInvoiceEditSummaryForm))