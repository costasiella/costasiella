// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'


import {
  Button,
  Card,
  Form,
} from "tabler-react"


const SettingsFinanceCurrencyForm = ({ t, history, isSubmitting, errors, values, return_url }) => (
  <FoForm>
      <Card.Body>
          <Form.Group label={t('settings.finance.currency')}>
            <Field type="text" 
              name="finance_currency" 
              className={(errors.finance_currency) ? "form-control is-invalid" : "form-control"} 
              autoComplete="off" />
            <ErrorMessage name="finance_currency" component="span" className="invalid-feedback" />
          </Form.Group>
          <Form.Group label={t('settings.finance.currency_symbol')}>
            <Field type="text" 
              name="finance_currency_symbol" 
              className={(errors.finance_currency_symbol) ? "form-control is-invalid" : "form-control"} 
              autoComplete="off" />
            <ErrorMessage name="finance_currency_symbol" component="span" className="invalid-feedback" />
          </Form.Group>
      </Card.Body>
      <Card.Footer>
          <Button 
            color="primary"
            type="submit" 
            disabled={isSubmitting}
          >
            {t('general.submit')}
          </Button>
          {/* <Link to={return_url}>
            <Button 
              type="button" 
              color="link">
                {t('general.cancel')}
            </Button>
          </Link> */}
      </Card.Footer>
  </FoForm>
)

export default withTranslation()(withRouter(SettingsFinanceCurrencyForm))