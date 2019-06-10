// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { Link } from 'react-router-dom'


import {
  Button,
  Card,
  Form,
} from "tabler-react"


const FinancePaymentMethodForm = ({ t, history, isSubmitting, errors, values, return_url }) => (
  <FoForm>
      <Card.Body>
          <Form.Group label={t('general.name')}>
            <Field type="text" 
                    name="name" 
                    className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
            <ErrorMessage name="name" component="span" className="invalid-feedback" />
          </Form.Group>
          <Form.Group label={t('finance.code')}>
            <Field type="text" 
                    name="code" 
                    className={(errors.code) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
            <ErrorMessage name="code" component="span" className="invalid-feedback" />
          </Form.Group>
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
            <Button 
              type="button" 
              color="link">
                {t('general.cancel')}
            </Button>
          </Link>
      </Card.Footer>
  </FoForm>
)

export default withTranslation()(withRouter(FinancePaymentMethodForm))