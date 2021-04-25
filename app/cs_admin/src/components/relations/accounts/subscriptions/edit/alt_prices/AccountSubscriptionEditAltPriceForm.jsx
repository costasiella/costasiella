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
import { tinymceBasicConf } from "../../../../../../plugin_config/tinymce"
import CSDatePicker from "../../../../../ui/CSDatePicker"

function AccountSubscriptionEditAltPriceForm ({ 
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

  let title
  if ( formTitle == "create" ) {
    title = t('relations.account.subscriptions.alt_prices.add')
  } else {
    title = t('relations.account.subscriptions.alt_prices.edit')
  }

  return (
    <FoForm>
      <Card.Body>
        <h5>{title}</h5>
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
          <Grid.Col>
            <Form.Group label={t('general.amount')}>
                <Field type="text" 
                    name="amount" 
                    className={(errors.amount) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
                <ErrorMessage name="amount" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
          <Form.Group label={t('general.description')}>
            <Field type="text" 
                    name="description" 
                    className={(errors.description) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
            <ErrorMessage name="description" component="span" className="invalid-feedback" />
          </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
          <Form.Group label={t('general.note')}>
            <Editor
                textareaName="note"
                initialValue={values.note}
                init={tinymceBasicConf}
                onChange={(e) => setFieldValue("note", e.target.getContent())}
                onBlur={() => setFieldTouched("note", true)}
              />
            <ErrorMessage name="note" component="span" className="invalid-feedback" />
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

export default withTranslation()(withRouter(AccountSubscriptionEditAltPriceForm))