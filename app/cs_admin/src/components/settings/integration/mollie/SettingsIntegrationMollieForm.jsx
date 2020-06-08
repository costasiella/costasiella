// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'


import {
  Button,
  Card,
  Form,
} from "tabler-react"


const SettingsIntegrationMollieForm = ({ t, history, isSubmitting, errors, values, return_url }) => (
  <FoForm>
      <Card.Body>
          <Form.Group label={t('settings.integration.mollie.api_key')}>
            <Field type="text" 
              name="mollie_api_key" 
              className={(errors.mollie_api_key) ? "form-control is-invalid" : "form-control"} 
              autoComplete="off" />
            <ErrorMessage name="mollie_api_key" component="span" className="invalid-feedback" />
          </Form.Group>
      </Card.Body>
      <Card.Footer>
          <Button 
            color="primary"
            type="submit" 
            disabled={isSubmitting}
          >
            {t('general.submit')}
          </Button>
          {/* <Link to={return_url}>
            <Button 
              type="button" 
              color="link">
                {t('general.cancel')}
            </Button>
          </Link> */}
      </Card.Footer>
  </FoForm>
)

export default withTranslation()(withRouter(SettingsIntegrationMollieForm))