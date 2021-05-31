// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from "uuid"
import { Link } from "react-router-dom"

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../../plugin_config/tinymce"
import CSDatePicker from "../../../ui/CSDatePicker"


import {
  Button,
  Card,
  Form,
  Grid,
} from "tabler-react";


const AccountFinancePaymentBatchCategoryItemsForm = ({ t, history, inputData, isSubmitting, errors, returnUrl }) => (
  <FoForm>
    <Card.Body> 
      <Grid.Row>
        <Grid.Col>
          <Form.Group label={t('general.year')} >
            <Field type="text" 
                  name="year" 
                  className={(errors.year) ? "form-control is-invalid" : "form-control"} 
                  autoComplete="off" />
            <ErrorMessage name="year" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
        <Grid.Col>
          <Form.Group label={t('general.month')} >
            <Field type="text" 
                  name="month" 
                  className={(errors.month) ? "form-control is-invalid" : "form-control"} 
                  autoComplete="off" />
            <ErrorMessage name="month" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
      </Grid.Row>
      <Grid.Row>
        <Grid.Col>
          <Form.Group label={t('general.amount')} >
            <Field type="text" 
                  name="amount" 
                  className={(errors.amount) ? "form-control is-invalid" : "form-control"} 
                  autoComplete="off" />
            <ErrorMessage name="amount" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
        <Grid.Col>
          <Form.Group label={t('general.category')}>
            <Field component="select" 
                  name="financePaymentBatchCategory" 
                  className={(errors.financePaymentBatchCategory) ? "form-control is-invalid" : "form-control"} 
                  autoComplete="off">
              <option value="" key={v4()}>{t('general.please_select')}</option>
              {inputData.financePaymentBatchCategories.edges.map(({ node }) =>
                <option value={node.id} key={v4()}>{node.name}</option>
              )}
            </Field>
            <ErrorMessage name="financePaymentBatchCategory" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
      </Grid.Row> 
      <Grid.Row>
        <Grid.Col>
          <Form.Group label={t('general.description')} >
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


export default withTranslation()(withRouter(AccountFinancePaymentBatchCategoryItemsForm))