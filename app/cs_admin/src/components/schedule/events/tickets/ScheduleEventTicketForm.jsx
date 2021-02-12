// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from 'uuid'

import {
  Button,
  Card,
  Grid,
  Form,
} from "tabler-react"

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../../plugin_config/tinymce"
// import CSDatePicker from "../../../../../ui/CSDatePicker"

function ScheduleEventTicketForm ({ 
  t, 
  history, 
  match, 
  isSubmitting, 
  errors, 
  values, 
  inputData, 
  returnUrl, 
  setFieldTouched, 
  setFieldValue, 
  formTitle="create" })   
{

  return (
    <FoForm>
      <Card.Body>
        <Grid.Row>
          <Grid.Col>
            <Form.Group>
              <Form.Label className="custom-switch">
                  <Field 
                    className="custom-switch-input"
                    type="checkbox" 
                    name="displayPublic" 
                    checked={values.displayPublic} />
                  <span className="custom-switch-indicator" ></span>
                  <span className="custom-switch-description">{t('schedule.events.tickets.public')}</span>
              </Form.Label>
              <ErrorMessage name="displayPublic" component="div" />   
            </Form.Group>  
          </Grid.Col>
        </Grid.Row>
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
            <Form.Group label={t('general.price')}>
                <Field type="text" 
                    name="price" 
                    className={(errors.price) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
                <ErrorMessage name="price" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.taxrate')}>
              <Field component="select" 
                      name="financeTaxRate" 
                      className={(errors.financeTaxRate) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off">
                {console.log("query data in subscription price add:")}
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
        <Grid.Row>
          <Grid.Col>
          <Form.Group label={t('general.description')}>
            <Editor
                textareaName="description"
                initialValue={values.description}
                init={tinymceBasicConf}
                onChange={(e) => setFieldValue("description", e.target.getContent())}
                onBlur={() => setFieldTouched("description", true)}
              />
            <ErrorMessage name="description" component="span" className="invalid-feedback" />
          </Form.Group>
          </Grid.Col>
        </Grid.Row>
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
          </Grid.Col>
          <Grid.Col>
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
          <Button color="link" onClick={() => history.push(returnUrl)} role="button">
              {t('general.cancel')}
          </Button>
      </Card.Footer>
    </FoForm>
  )
}

export default withTranslation()(withRouter(ScheduleEventTicketForm))