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

import cs_django_links from "../../tools/cs_django_links"


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
      <small className="text-muted">
        {t("shop.order.by_placing_this_order")} <br />
        <ul>
          <li>{t("shop.order.agree_terms")} {" "}
            <a target="_blank" href={cs_django_links.EXPORT_TERMS_AND_CONDITIONS}>{t("general.terms_and_conditions")}</a>
          </li>
          <li>{t("shop.order.agree_privacy")} {" "}
            <a target="_blank" href={cs_django_links.EXPORT_PRIVACY_POLICY}>{t("general.privacy_policy")}</a>
          </li>
        </ul>
      </small>
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