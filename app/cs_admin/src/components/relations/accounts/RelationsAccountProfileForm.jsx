// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'


import {
  Button,
  Card,
  Form,
  Grid
} from "tabler-react"


import CSDatePicker from "../../ui/CSDatePicker"

const RelationsAccountProfileForm = ({ t, history, isSubmitting, errors, values, return_url, setFieldTouched, setFieldValue }) => (
  <FoForm>
      <Card.Body>
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
                <option value="F">{t("genders.female")}</option>
                <option value="M">{t("genders.male")}</option>
                <option value="X">{t("genders.other")}</option>
              </Field>
              <ErrorMessage name="gender" component="span" className="invalid-feedback" />
            </Form.Group> 
          </Grid.Col>
        </Grid.Row>
        <Form.Group label={t('general.email')}>
          <Field type="text" 
                  name="email" 
                  className={(errors.email) ? "form-control is-invalid" : "form-control"} 
                  autoComplete="off" />
          <ErrorMessage name="email" component="span" className="invalid-feedback" />
        </Form.Group>
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