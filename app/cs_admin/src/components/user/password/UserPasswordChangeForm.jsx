// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { v4 } from 'uuid'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'


import {
  Button,
  Card,
  Dimmer,
  Form,
  Grid
} from "tabler-react"


// import CSDatePicker from "../../ui/CSDatePicker"
// import ISO_COUNTRY_CODES from "../../../tools/iso_country_codes"


const UserPasswordChangeForm = ({ t, history, isSubmitting, errors, values, return_url, setFieldTouched, setFieldValue }) => (
  <FoForm className="card" autoComplete="off">
    <Card.Body className="p-6">
      <Card.Title>
        {t('user.change_password.title')}
      </Card.Title>
      <Form.Group label={t('user.change_password.password_current')}>
        <Field type="password" 
                name="passwordCurrent" 
                className={(errors.passwordCurrent) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" />
        <ErrorMessage name="passwordCurrent" component="span" className="invalid-feedback" />
      </Form.Group>
      <Form.Group label={t('user.change_password.password_new')}>
        <Field type="password" 
                name="passwordNew" 
                className={(errors.passwordNew) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" />
        <ErrorMessage name="passwordNew" component="span" className="invalid-feedback" />
      </Form.Group>
      <Form.Group label={t('user.change_password.password_new_repeat')}>
        <Field type="password" 
                name="passwordNew2" 
                className={(errors.passwordNew2) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" />
        <ErrorMessage name="passwordNew2" component="span" className="invalid-feedback" />
      </Form.Group>
      <Form.Footer>
        <Button 
          block
          loading={isSubmitting}
          color="primary"
          type="submit" 
          disabled={isSubmitting}
        >
          {t('user.change_password.title')}
        </Button>
      </Form.Footer>
    </Card.Body>
  </FoForm>
)

export default withTranslation()(withRouter(UserPasswordChangeForm))

