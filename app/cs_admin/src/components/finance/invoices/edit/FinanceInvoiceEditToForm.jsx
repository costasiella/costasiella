// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'


import {
  Dimmer,
  Form,
  Grid,
} from "tabler-react"


let toFormTypingTimer
const formSubmitTimeout = 750

function handleOnChange({ e, submitForm, handleChange}) {
  clearTimeout(toFormTypingTimer)
  handleChange(e)
  toFormTypingTimer = setTimeout(() => {
    submitForm()
  }, 750)
}

function handleOnKeyDown() {
  clearTimeout(toFormTypingTimer)
}


const FinanceInvoiceEditToForm = ({ t, isSubmitting, errors, handleChange, submitForm }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group label={t("finance.invoices.relation_company")}>
        <Field type="text" 
                name="relationCompany" 
                className={(errors.relationCompany) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" 
                onChange={(e) => {
                  handleOnChange({ 
                    e:e, 
                    submitForm:submitForm, 
                    handleChange:handleChange
                  })
                }}
                onKeyDown={() => handleOnKeyDown()}
                
        />
        <ErrorMessage name="relationCompany" component="span" className="invalid-feedback" />
      </Form.Group>
      <Grid.Row>
        <Grid.Col md={6}>
          <Form.Group label={t("finance.invoices.relation_company_registration")}>
            <Field type="text" 
                    name="relationCompanyRegistration" 
                    className={(errors.relationCompanyRegistration) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" 
                    onChange={(e) => {
                      handleOnChange({ 
                        e:e, 
                        submitForm:submitForm, 
                        handleChange:handleChange
                      })
                    }}
                    onKeyDown={() => handleOnKeyDown()}
                    
            />
            <ErrorMessage name="relationCompanyRegistration" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
        <Grid.Col md={6}>
          <Form.Group label={t("finance.invoices.relation_company_tax_registration")}>
            <Field type="text" 
                    name="relationCompanyTaxRegistration" 
                    className={(errors.relationCompanyTaxRegistration) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" 
                    onChange={(e) => {
                      handleOnChange({ 
                        e:e, 
                        submitForm:submitForm, 
                        handleChange:handleChange
                      })
                    }}
                    onKeyDown={() => handleOnKeyDown()}
                    
            />
            <ErrorMessage name="relationCompanyTaxRegistration" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
      </Grid.Row>
      <Form.Group label={t("finance.invoices.relation_contact_name")}>
        <Field type="text" 
                name="relationContactName" 
                className={(errors.relationContactName) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" 
                onChange={(e) => {
                  handleOnChange({ 
                    e:e, 
                    submitForm:submitForm, 
                    handleChange:handleChange
                  })
                }}
                onKeyDown={() => handleOnKeyDown()}
                
        />
        <ErrorMessage name="relationContactName" component="span" className="invalid-feedback" />
      </Form.Group>
      <Grid.Row>
        <Grid.Col md={6}>
          <Form.Group label={t("finance.invoices.relation_address")}>
            <Field type="text" 
                    name="relationAddress" 
                    className={(errors.relationAddress) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" 
                    onChange={(e) => {
                      handleOnChange({ 
                        e:e, 
                        submitForm:submitForm, 
                        handleChange:handleChange
                      })
                    }}
                    onKeyDown={() => handleOnKeyDown()}
                    
            />
            <ErrorMessage name="relationAddress" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
        <Grid.Col md={6}>
          <Form.Group label={t("finance.invoices.relation_postcode")}>
            <Field type="text" 
                    name="relationPostcode" 
                    className={(errors.relationPostcode) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" 
                    onChange={(e) => {
                      handleOnChange({ 
                        e:e, 
                        submitForm:submitForm, 
                        handleChange:handleChange
                      })
                    }}
                    onKeyDown={() => handleOnKeyDown()}
                    
            />
            <ErrorMessage name="relationPostcode" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
      </Grid.Row>
      <Grid.Row>
        <Grid.Col md={6}>
          <Form.Group label={t("finance.invoices.relation_city")}>
            <Field type="text" 
                    name="relationCity" 
                    className={(errors.relationCity) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" 
                    onChange={(e) => {
                      handleOnChange({ 
                        e:e, 
                        submitForm:submitForm, 
                        handleChange:handleChange
                      })
                    }}
                    onKeyDown={() => handleOnKeyDown()}
                    
            />
            <ErrorMessage name="relationCity" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
        <Grid.Col md={6}>
          <Form.Group label={t("finance.invoices.relation_country")}>
            <Field type="text" 
                    name="relationCountry" 
                    className={(errors.relationCountry) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" 
                    onChange={(e) => {
                      handleOnChange({ 
                        e:e, 
                        submitForm:submitForm, 
                        handleChange:handleChange
                      })
                    }}
                    onKeyDown={() => handleOnKeyDown()}
                    
            />
            <ErrorMessage name="relationCountry" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
      </Grid.Row>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FinanceInvoiceEditToForm))