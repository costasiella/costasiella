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
          <Form.Group>
            <Form.Label className="custom-switch">
              <Field 
                className="custom-switch-input"
                type="checkbox" 
                name="displayPublic" 
                checked={values.displayPublic} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('organization.appointments.public')}</span>
            </Form.Label>
            <ErrorMessage name="displayPublic" component="div" />   
          </Form.Group>    

          <Form.Group label={t('general.name')}>
            <Field type="text" 
                    name="name" 
                    className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
            <ErrorMessage name="name" component="span" className="invalid-feedback" />
          </Form.Group>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.glaccount')}>
              <Field component="select" 
                    name="financeGlaccount" 
                    className={(errors.financeGlaccount) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
                <option value="" key={v4()}></option>
                {inputData.financeGlaccounts.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.name} ({node.code})</option>
                )}
              </Field>
              <ErrorMessage name="financeGlaccount" component="span" className="invalid-feedback" />
            </Form.Group>
            <Form.Group label={t('general.costcenter')}>
              <Field component="select" 
                    name="financeCostcenter" 
                    className={(errors.financeCostcenter) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
                <option value="" key={v4()}></option>
                {inputData.financeCostcenters.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.name} ({node.code})</option>
                )}
              </Field>
              <ErrorMessage name="financeCostcenter" component="span" className="invalid-feedback" />
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