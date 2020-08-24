import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"

import {
    Button,
    Card,
    Form,
    Grid,
    Icon
  } from "tabler-react"
  import { Form as FoForm, Field, ErrorMessage } from 'formik'


function AutomationAccountSubscriptionCreditForm({ t, history, isSubmitting, errors, returnUrl}) {
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
  
export default withTranslation()(withRouter(AutomationAccountSubscriptionCreditForm))