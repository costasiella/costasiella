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

import CSDatePicker from "../../ui/CSDatePicker"


const FinancePaymentCollectionBatchForm = (
  { t, history, isSubmitting, setFieldTouched, setFieldValue, errors, values, returnUrl, create=false, category=false, invoices=true }
  ) => (
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
          {(create) ? 
            <Grid.Col>
              <Form.Group label={t('finance.payment_batches.execution_date')}>
                <CSDatePicker 
                  selected={values.executionDate}
                  onChange={(executionDate) => {
                    setFieldValue("executionDate", executionDate)
                    setFieldTouched("executionDate", true)
                  }}
                  onBlur={() => setFieldTouched("executionDate", true)}
                  placeholderText={t('')}
                />
                <ErrorMessage name="executionDate" component="span" className="invalid-feedback" />
              </Form.Group>
            </Grid.Col>
            : "" 
          }
        </Grid.Row>
        {(create && category) ?
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
            <Form.Group label={t('general.note')}>
              <Field type="textarea"
                     component="textarea" 
                     name="note" 
                     className={(errors.note) ? "form-control is-invalid" : "form-control"} 
                     autoComplete="off" />
              <ErrorMessage name="note" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        {(create) ? 
          <Grid.Row>
            <Grid.Col>
              <Form.Group>
                <Form.Label className="custom-switch">
                  <Field 
                  className="custom-switch-input"
                  type="checkbox" 
                  name="includeZeroAmounts" 
                  checked={values.includeZeroAmounts} />
                  <span className="custom-switch-indicator" ></span>
                  <span className="custom-switch-description">{t('finance.payment_batches.include_zero_amounts')}</span>
                </Form.Label>
                <ErrorMessage name="includeZeroAmounts" component="div" />   
              </Form.Group>  
            </Grid.Col>
          </Grid.Row>
          : "" 
        }
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

export default withTranslation()(withRouter(FinancePaymentCollectionBatchForm))