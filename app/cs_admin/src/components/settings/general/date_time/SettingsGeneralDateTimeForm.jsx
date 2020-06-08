// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from 'uuid'


import {
  Button,
  Card,
  Form,
} from "tabler-react"


const SettingsGeneralDateTimeForm = ({ t, history, isSubmitting, errors, values, return_url }) => (
  <FoForm>
      <Card.Body>
          <Form.Group label={t('settings.general.date_format')}>
            <Field component="select" 
                    name="dateFormat" 
                    className={(errors.dateFormat) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
                <option value="YYYY-MM-DD" key={v4()}>{t('settings.general.date_formats.YYYY-MM-DD')}</option>
                <option value="MM-DD-YYYY" key={v4()}>{t('settings.general.date_formats.MM-DD-YYYY')}</option>
                <option value="DD-MM-YYYY" key={v4()}>{t('settings.general.date_formats.DD-MM-YYYY')}</option>
            </Field>
            <ErrorMessage name="dateFormat" component="span" className="invalid-feedback" />
          </Form.Group>
          <Form.Group label={t('settings.general.time_format')}>
            <Field component="select" 
                    name="timeFormat" 
                    className={(errors.timeFormat) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
                <option value="24" key={v4()}>{t('settings.general.time_formats.24hr')}</option>
                <option value="12" key={v4()}>{t('settings.general.time_formats.12hr')}</option>
            </Field>
            <ErrorMessage name="timeFormat" component="span" className="invalid-feedback" />
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

export default withTranslation()(withRouter(SettingsGeneralDateTimeForm))