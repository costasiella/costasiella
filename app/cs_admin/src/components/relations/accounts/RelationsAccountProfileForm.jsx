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


const RelationsAccountProfileForm = ({ t, history, isSubmitting, errors, values, return_url, setFieldTouched, setFieldValue }) => (
  <FoForm>
      <Card.Body>
        <Grid.Row>
          <Grid.Col>
            <Form.Group>
              <Form.Label className="custom-switch">
                  <Field 
                  className="custom-switch-input"
                  type="checkbox" 
                  name="customer" 
                  checked={values.customer} />
                  <span className="custom-switch-indicator" ></span>
                  <span className="custom-switch-description">{t('general.customer')}</span>
              </Form.Label>
              <ErrorMessage name="customer" component="div" />   
            </Form.Group>  
          </Grid.Col>
          <Grid.Col>
            <Form.Group>
              <Form.Label className="custom-switch">
                  <Field 
                  className="custom-switch-input"
                  type="checkbox" 
                  name="teacher" 
                  checked={values.teacher} />
                  <span className="custom-switch-indicator" ></span>
                  <span className="custom-switch-description">{t('general.teacher')}</span>
              </Form.Label>
              <ErrorMessage name="teacher" component="div" />   
            </Form.Group>  
          </Grid.Col>
          <Grid.Col>
            <Form.Group>
              <Form.Label className="custom-switch">
                  <Field 
                  className="custom-switch-input"
                  type="checkbox" 
                  name="employee" 
                  checked={values.employee} />
                  <span className="custom-switch-indicator" ></span>
                  <span className="custom-switch-description">{t('general.employee')}</span>
              </Form.Label>
              <ErrorMessage name="employee" component="div" />   
            </Form.Group>  
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.first_name')}>
              <Field type="text" 
                      name="firstName" 
                      className={(errors.firstName) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="firstName" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.last_name')}>
              <Field type="text" 
                      name="lastName" 
                      className={(errors.lastName) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="lastName" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
         <Grid.Col>
            <Form.Group label={t('general.date_of_birth')}>
              <CSDatePicker 
                selected={values.dateOfBirth}
                onChange={(date) => setFieldValue("dateOfBirth", date)}
                onBlur={() => setFieldTouched("dateOfBirth", true)}
              />
              <ErrorMessage name="dateOfBirth" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.gender')}>
              <Field component="select" 
                    name="gender" 
                    className={(errors.organizationMembership) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
                <option value=""></option>
                <option value="F">{t("genders.female")}</option>
                <option value="M">{t("genders.male")}</option>
                <option value="X">{t("genders.other")}</option>
              </Field>
              <ErrorMessage name="gender" component="span" className="invalid-feedback" />
            </Form.Group> 
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.email')}>
              <Field type="text" 
                      name="email" 
                      className={(errors.email) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="email" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('relations.accounts.emergency')}>
              <Field type="text" 
                     name="emergency" 
                     className={(errors.emergency) ? "form-control is-invalid" : "form-control"} 
                     autoComplete="off" />
              <ErrorMessage name="emergency" component="span" className="invalid-feedback" />
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
            <Form.Group label={t('general.mobile')}>
              <Field type="text" 
                     name="mobile" 
                     className={(errors.mobile) ? "form-control is-invalid" : "form-control"} 
                     autoComplete="off" />
              <ErrorMessage name="mobile" component="span" className="invalid-feedback" />
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

export default withTranslation()(withRouter(RelationsAccountProfileForm))

