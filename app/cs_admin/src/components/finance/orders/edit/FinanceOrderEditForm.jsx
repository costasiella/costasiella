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


const FinanceOrderEditForm = ({ t, history, inputData, isSubmitting, setFieldValue, setFieldTouched, errors, values, return_url }) => (
  <FoForm>
    <Card>
      <Card.Body> 
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.status')}>
              <Field component="select" 
                     name="status" 
                     className={(errors.status) ? "form-control is-invalid" : "form-control"} 
                     autoComplete="off">
                <option value={"RECEIVED"} key={v4()}>{t("finance.orders.statuses.RECEIVED")}</option>
                <option value={"AWAITING_PAYMENT"} key={v4()}>{t("finance.orders.statuses.AWAITING_PAYMENT")}</option>
                <option value={"PAID"} key={v4()}>{t("finance.orders.statuses.PAID")}</option>
                <option value={"DELIVERED"} key={v4()}>{t("finance.orders.statuses.DELIVERED")}</option>
                <option value={"CANCELLED"} key={v4()}>{t("finance.orders.statuses.CANCELLED")}</option>
                <option value={"NOT_FOUND"} key={v4()}>{t("finance.orders.statuses.NOT_FOUND")}</option>
              </Field>
              <ErrorMessage name="status" component="span" className="invalid-feedback" />
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
          <Link to={return_url} >
            <Button
              type="button" 
              color="link" 
            >
              {t('general.cancel')}
            </Button>
          </Link>
      </Card.Footer>
    </Card>
  </FoForm>
)


export default withTranslation()(withRouter(FinanceOrderEditForm))