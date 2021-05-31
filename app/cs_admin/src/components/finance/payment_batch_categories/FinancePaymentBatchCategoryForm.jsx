// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { Link } from 'react-router-dom'
import { v4 } from 'uuid'


import {
  Button,
  Card,
  Form,
  Grid,
} from "tabler-react"


const FinancePaymentBatchCategoryForm = ({ t, history, isSubmitting, errors, values, returnUrl, create=false }) => (
  <FoForm>
      <Card.Body>
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
        {(create) ?
          <Grid.Row>
            <Grid.Col>
              <Form.Group label={t('finance.payment_batch_categories.batch_category_type')}>
                <Field component="select" 
                        name="batchCategoryType" 
                        className={(errors.batchCategoryType) ? "form-control is-invalid" : "form-control"} 
                        autoComplete="off">
                  <option value="COLLECTION" key={v4()}>{t('general.collection')}</option>
                  <option value="PAYMENT" key={v4()}>{t('general.payment')}</option>
                </Field>
                <ErrorMessage name="batchCategoryType" component="span" className="invalid-feedback" />
              </Form.Group>
            </Grid.Col>
          </Grid.Row> 
          : ""
        }
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
            {t('general.submit')}
          </Button>
          <Link to={returnUrl}>
            <Button 
              type="button" 
              color="link">
                {t('general.cancel')}
            </Button>
          </Link>
      </Card.Footer>
  </FoForm>
)

export default withTranslation()(withRouter(FinancePaymentBatchCategoryForm))