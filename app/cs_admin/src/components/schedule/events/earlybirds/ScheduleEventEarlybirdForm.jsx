// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from 'uuid'

import {
  Button,
  Card,
  Grid,
  Form,
} from "tabler-react"


import { customFileInputLabelStyle } from "../../../../tools/custom_file_input_label_style"

function ScheduleEventMediaForm ({ 
  t, 
  history, 
  match, 
  isSubmitting, 
  errors, 
  values, 
  returnUrl,
  inputFileName, 
  fileInputLabel, 
  handleFileInputChange=f=>f
})   
{
  return (
    <FoForm>
      <Card.Body>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.date_start')}>
              <CSDatePicker 
                className={(errors.dateStart) ? "form-control is-invalid" : "form-control"} 
                selected={values.dateStart}
                onChange={(date) => {
                  setFieldValue("dateStart", date)
                  setFieldTouched("dateStart", true)
                }}
                onBlur={() => setFieldTouched("dateStart", true)}
              />
              <ErrorMessage name="dateStart" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.date_end')}>
              <CSDatePicker 
                className={(errors.dateEnd) ? "form-control is-invalid" : "form-control"} 
                selected={values.dateEnd}
                onChange={(date) => {
                  setFieldValue("dateEnd", date)
                  setFieldTouched("dateEnd", true)
                }}
                onBlur={() => setFieldTouched("dateEnd", true)}
              />
              <ErrorMessage name="dateEnd" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('schedule.events.earlybird.discountPercentage')}>
              <Field type="text" 
                    name="discountPercentage" 
                    className={(errors.discountPercentage) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
              <ErrorMessage name="discountPercentage" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
      </Card.Body>
      <Card.Footer>
          <Button 
            color="primary"
            className="pull-right" 
            type="submit" 
            disabled={isSubmitting}
          >
            {t('general.submit')}
          </Button>
          <Link to={returnUrl}>
            <Button color="link" role="button">
                {t('general.cancel')}
            </Button>
          </Link>
      </Card.Footer>
    </FoForm>
  )
}

export default withTranslation()(withRouter(ScheduleEventMediaForm))