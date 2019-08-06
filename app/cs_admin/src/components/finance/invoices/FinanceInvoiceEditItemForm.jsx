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

const FinanceInvoiceEditItemForm = ({ t, isSubmitting, errors, values, handleChange, submitForm, setFieldValue, setFieldTouched, node, inputData }) => (
  <FoForm>
  <Table.Row>    

      <Table.Col>
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
      </Table.Col>
      <Table.Col>
        <Form.Group>
          <Field type="text" 
                  component="textarea"
                  name="description" 
                  className={(errors.description) ? "form-control is-invalid" : "form-control"} 
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
          <ErrorMessage name="description" component="span" className="invalid-feedback" />
        </Form.Group>
      </Table.Col>
      <Table.Col>
        <Form.Group>
          <Field type="text" 
                  name="quantity" 
                  className={(errors.quantity) ? "form-control is-invalid" : "form-control"} 
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
          <ErrorMessage name="quantity" component="span" className="invalid-feedback" />
        </Form.Group>
      </Table.Col>
      <Table.Col>
        <Form.Group>
          <Field type="text" 
                  name="price" 
                  className={(errors.price) ? "form-control is-invalid" : "form-control"} 
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
          <ErrorMessage name="price" component="span" className="invalid-feedback" />
        </Form.Group>
      </Table.Col>
      <Table.Col>
        <Form.Group>
          <Field component="select" 
                name="financeTaxRate" 
                className={(errors.financeTaxRate) ? "form-control is-invalid" : "form-control"} 
                onChange={(e) => {
                  setFieldValue('financeTaxRate', e.target.value)
                  setFieldTouched('financeTaxRate', true)
                  setTimeout(() => {submitForm()}, itemSubmitTimeout)
                }}
                autoComplete="off">
            <option value="" key={v4()}></option>
            {inputData.financeTaxRates.edges.map(({ node }) =>
              <option value={node.id} key={v4()}>{node.name}</option>
            )}
          </Field>
          <ErrorMessage name="financePaymentMethod" component="span" className="invalid-feedback" />
        </Form.Group>  
      </Table.Col>
      <Table.Col>
        {node.subtotalDisplay}            
      </Table.Col>
      <Table.Col>
        {node.taxDisplay}            
      </Table.Col>
      <Table.Col>
        {node.totalDisplay}            
      </Table.Col>
  </Table.Row>
  </FoForm>
)

export default withTranslation()(withRouter(FinanceInvoiceEditItemForm))