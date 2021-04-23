// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { v4 } from 'uuid'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'


import {
  Button,
  Card,
  Form,
  Grid
} from "tabler-react"


import CSDatePicker from "../../ui/CSDatePicker"
import ISO_COUNTRY_CODES from "../../../tools/iso_country_codes"


function RelationsB2BEditForm({ t, history, isSubmitting, errors, values, return_url, setFieldTouched, setFieldValue }) {
  return (
    <FoForm>
      <Card.Body>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.name')}>
              <Field type="text" 
                      name="name" 
                      className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="name" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.email_contact')}>
              <Field type="text" 
                      name="emailContact" 
                      className={(errors.emailContact) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="emailContact" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.email_billing')}>
              <Field type="text" 
                      name="emailBilling" 
                      className={(errors.emailBilling) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="emailBilling" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.phone')}>
              <Field type="text" 
                      name="phone" 
                      className={(errors.phone) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="phone" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
          <Form.Group label={t('general.phone2')}>
              <Field type="text" 
                      name="phone2" 
                      className={(errors.phone2) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="phone2" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.address')}>
              <Field type="text" 
                      name="address" 
                      className={(errors.address) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="address" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.postcode')}>
              <Field type="text" 
                      name="postcode" 
                      className={(errors.postcode) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="postcode" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.city')}>
              <Field type="text" 
                      name="city" 
                      className={(errors.city) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="city" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.country')}>
              <Field component="select" 
                    name="country" 
                    className={(errors.country) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
                <option value=""></option>
                { ISO_COUNTRY_CODES.map(
                    country => <option value={country.Code} key={v4()}>{country.Name}</option>
                )}
              </Field>
              <ErrorMessage name="country" component="span" className="invalid-feedback" />
            </Form.Group> 
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('finance.invoices.relation_company_registration')}>
              <Field type="text" 
                      name="registration" 
                      className={(errors.registration) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="registration" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
          <Form.Group label={t('finance.invoices.relation_company_tax_registration')}>
              <Field type="text" 
                      name="taxRegistration" 
                      className={(errors.taxRegistration) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="taxRegistration" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
      </Card.Body>
      <Card.Footer>
          <Button 
            color="primary"
            // className="pull-right" 
            type="submit" 
            disabled={isSubmitting}
          >
            {t('general.submit')}
          </Button>
          
          {/* <Button color="link" onClick={() => history.push(return_url)}>
              {t('general.cancel')}
          </Button> */}
      </Card.Footer>
    </FoForm>
  )
}

export default withTranslation()(withRouter(RelationsB2BEditForm))

