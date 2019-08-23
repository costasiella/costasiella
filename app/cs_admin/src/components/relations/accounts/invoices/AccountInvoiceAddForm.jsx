// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from "uuid"
import { Link } from 'react-router-dom'

import {
  Button,
  Card,
  Form,
  Grid,
} from "tabler-react";


const AccountInvoiceAddForm = ({ t, history, inputData, isSubmitting, setFieldValue, setFieldTouched, errors, values, return_url }) => (
  <FoForm>
    <Card.Body>
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
        <Link to={return_url}>
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


export default withTranslation()(withRouter(AccountInvoiceAddForm))