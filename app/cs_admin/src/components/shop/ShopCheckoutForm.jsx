// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'

import {
  Button,
  Form,
  Icon
} from "tabler-react"


const ShopClasspassForm = ({ t, isSubmitting, errors }) => (
    <FoForm>
      <Form.Group label={t('shop.order.message')}>
        <Field type="text" 
               component="textarea"
               name="message" 
               className={(errors.message) ? "form-control is-invalid" : "form-control"} 
               autoComplete="off" />
        <ErrorMessage name="message" component="span" className="invalid-feedback" />
      </Form.Group>
      <Button 
        block
        color="primary"
        className="pull-right" 
        type="submit" 
        disabled={isSubmitting}
      >
        {t('shop.place_order')} <Icon name="chevron-right" />
      </Button>
    </FoForm>
)

export default withTranslation()(withRouter(ShopClasspassForm))