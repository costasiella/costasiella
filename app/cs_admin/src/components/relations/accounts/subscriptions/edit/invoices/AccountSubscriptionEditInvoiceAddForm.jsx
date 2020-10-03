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
  Grid,
  Form,
} from "tabler-react"

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../../../../plugin_config/tinymce"
import CSDatePicker from "../../../../../ui/CSDatePicker"

function AccountSubscriptionEditInvoiceAddForm ({ 
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

  const title = t('relations.account.subscriptions.invoices.add')

  return (
    <FoForm>
      <Card.Body>
        <h5>{title}</h5>
        <Form.Group label={t('general.finance_invoice_group')}>
          <Field component="select" 
                name="financeInvoiceGroup" 
                className={(errors.financeInvoiceGroup) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off">
            <option value="" key={v4()}>{t('general.please_select')}</option>
            {inputData.financeInvoiceGroups.edges.map(({ node }) =>
              <option value={node.id} key={v4()}>{node.name}</option>
            )}
          </Field>
          <ErrorMessage name="financeInvoiceGroup" component="span" className="invalid-feedback" />
        </Form.Group>
        <Form.Group label={t('general.summary')}>
          <Field type="text" 
                  name="summary" 
                  className={(errors.summary) ? "form-control is-invalid" : "form-control"} 
                  autoComplete="off" />
          <ErrorMessage name="summary" component="span" className="invalid-feedback" />
        </Form.Group>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.subscription_year')}>
              <Field type="number" 
                      name="subscriptionYear" 
                      className={(errors.subscriptionYear) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="subscriptionYear" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.subscription_month')}>
              <Field type="number" 
                      name="subscriptionMonth" 
                      className={(errors.subscriptionMonth) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="subscriptionMonth" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
      </Card.Body>
      <Card.Footer>
          <Button 
            className="pull-right"
            color="primary"
            disabled={isSubmitting}
            type="submit"
          >
            {t('general.submit')}
          </Button>
          <Link to={returnUrl}>
            <Button
              type="button" 
              color="link" 
            >
                {t('general.cancel')}
            </Button>
          </Link>
      </Card.Footer>
    </FoForm>
  )
}

export default withTranslation()(withRouter(AccountSubscriptionEditInvoiceAddForm))