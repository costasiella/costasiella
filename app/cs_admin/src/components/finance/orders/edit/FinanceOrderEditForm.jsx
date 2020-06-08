// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from "uuid"

import {
  Button,
  Card,
  Form,
  Grid,
  Icon
} from "tabler-react";


const FinanceOrderEditForm = ({ t, isSubmitting, errors, values, returnUrl }) => (
  <FoForm>
    <Card title={t('general.status')}>
      <Card.Body> 
        <Grid.Row>
          <Grid.Col md={10}>
            <Form.Group>
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
            <span className="text-muted">
              <Icon name="info" /> {' '}
              {t("finance.orders.set_status_to_delivered_to_deliver_manually")}
            </span>
          </Grid.Col>
          <Grid.Col md={2}>
          <Button 
                className="pull-right"
                color="primary"
                disabled={isSubmitting}
                type="submit"
              >
                {t('general.submit')}
              </Button>
          </Grid.Col>
        </Grid.Row> 
      </Card.Body>
    </Card>
  </FoForm>
)


export default withTranslation()(withRouter(FinanceOrderEditForm))