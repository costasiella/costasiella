import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"
import { v4 } from "uuid"

import {
    Button,
    Card,
    Form,
    Grid,
    Icon
  } from "tabler-react"
import { Form as FoForm, Field, ErrorMessage } from 'formik'

import CSDatePicker from "../../../../ui/CSDatePicker"


function AutomationAccountSubscriptionInvoicesForm({ t, history, isSubmitting, errors, returnUrl}) {
  return (
    <FoForm>
      <Card.Body>
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
            <Form.Group label={t('automation.account.subscriptions.invoices.invoice_date')}>
              <Field component="select" 
                    name="invoiceDate" 
                    className={(errors.invoiceDate) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
                <option value="today" key={v4()}>{t('automation.account.subscriptions.invoices.today')}</option>
                <option value="first_of_month" key={v4()}>{t('automation.account.subscriptions.invoices.invoice_date_first_day_month')}</option>                
              </Field>
              <ErrorMessage name="invoiceDate" component="span" className="invalid-feedback" />
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
      </Card.Body>
      <Card.Footer>
        <Button 
         color="primary"
          className="pull-right" 
          type="submit" 
          disabled={isSubmitting}
          >
          {t('general.new_task')} <Icon name="chevron-right" />
        </Button>
        <Link to={returnUrl}>
          <Button color="link">
            {t('general.cancel')}
          </Button>
        </Link>
      </Card.Footer>
    </FoForm>
  )
}
  
export default withTranslation()(withRouter(AutomationAccountSubscriptionInvoicesForm))