// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from 'uuid'
import { Link } from 'react-router-dom'


import {
  Button,
  Card,
  Form,
  Grid,
} from "tabler-react"


const OrganizationAppointmentForm = ({ t, history, match, inputData, isSubmitting, errors, values, return_url }) => (
  <FoForm>
      <Card.Body>
         <Form.Group label={t('general.teacher')}>
            <Field component="select" 
                    name="account" 
                    className={(errors.account) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
              <option value="" key={v4()}>{t('general.please_select')}</option>
              {inputData.accountTeacherProfiles.edges.map(({ node }) =>
                <option value={node.account.id} key={v4()}>{node.account.fullName}</option>
              )}
            </Field>
            <ErrorMessage name="account" component="span" className="invalid-feedback" />
          </Form.Group>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.price')}>
              <Field type="text" 
                    name="price" 
                    className={(errors.price) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
              <ErrorMessage name="price" component="span" className="invalid-feedback" />
            </Form.Group>
            <Form.Group label={t('general.taxrate')}>
              <Field component="select" 
                      name="financeTaxRate" 
                      className={(errors.financeTaxRate) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off">
                {console.log("query data in appointment price form:")}
                {console.log(inputData)}
                <option value="" key={v4()}>{t('general.please_select')}</option>
                {inputData.financeTaxRates.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.name} ({node.percentage}% {node.rateType})</option>
                )}
              </Field>
              <ErrorMessage name="financeTaxRate" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
      </Card.Body>
      <Card.Footer>
          <Button 
            color="primary"
            className="pull-right" 
            type="submit" 
            disabled={isSubmitting}
          >
            {t('general.submit')}
          </Button>
          <Link to={return_url}>
            <Button color="link" type="button">
                {t('general.cancel')}
            </Button>
          </Link>
      </Card.Footer>
  </FoForm>
);

export default withTranslation()(withRouter(OrganizationAppointmentForm))