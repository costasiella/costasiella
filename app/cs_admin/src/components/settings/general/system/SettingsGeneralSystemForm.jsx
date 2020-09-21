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


const SettingsGeneralSystemForm = ({ t, history, isSubmitting, errors, values, return_url }) => (
  <FoForm>
      <Card.Body>
          <Form.Group label={t('settings.general.system.system_hostname')}>
            <Field type="text" 
              name="system_hostname" 
              className={(errors.system_hostname) ? "form-control is-invalid" : "form-control"} 
              autoComplete="off" />
            <ErrorMessage name="system_hostname" component="span" className="invalid-feedback" />
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

export default withTranslation()(withRouter(SettingsGeneralSystemForm))