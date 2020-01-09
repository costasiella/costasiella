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
import CSDatePicker from "../../../ui/CSDatePicker"

const FinanceInvoicePaymentForm = ({ t, history, match, isSubmitting, errors, values, inputData, return_url, setFieldTouched, setFieldValue }) => (
  <FoForm>
    <Card statusColor="blue">
      <Card.Header>
        <Card.Title>{t('general.details')}</Card.Title>
      </Card.Header>
      <Card.Body>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.date')}>
              <CSDatePicker 
                selected={values.date}
                onChange={(date) => setFieldValue("date", date)}
                onBlur={() => setFieldTouched("date", true)}
              />
              <ErrorMessage name="date" component="span" className="invalid-feedback" />
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
            <Form.Group label={t('general.payment_method')}>
              <Field component="select" 
                      name="financePaymentMethod" 
                      className={(errors.financePaymentMethod) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off">
                {console.log("query data in finance payment form:")}
                {console.log(inputData)}
                <option value="" key={v4()}>{t('')}</option>
                {inputData.financePaymentMethods.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.name}</option>
                )}
              </Field>
              <ErrorMessage name="financePaymentMethod" component="span" className="invalid-feedback" />
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
          <Button color="link" onClick={() => history.push(return_url)} role="button">
              {t('general.cancel')}
          </Button>
      </Card.Footer>
    </Card>
  </FoForm>
);

export default withTranslation()(withRouter(FinanceInvoicePaymentForm))