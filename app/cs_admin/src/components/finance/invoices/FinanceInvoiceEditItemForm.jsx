// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'


import {
  Dimmer,
  Form,
  Grid
} from "tabler-react"


let itemFormTypingTimer


const FinanceInvoiceEditItemForm = ({ t, isSubmitting, errors, handleChange, submitForm }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Grid.Row>
        <Grid.Col>
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
                      }, 1500)
                    }}
                    onKeyDown={() => clearTimeout(itemFormTypingTimer)}
                    
            />
            <ErrorMessage name="productName" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
      </Grid.Row>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FinanceInvoiceEditItemForm))