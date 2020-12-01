// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from 'uuid'

import {
  Dimmer,
  Grid,
  Form,
} from "tabler-react"


const ScheduleEventTicketEditActivityForm = ({ t, history, match, disabled, isSubmitting, setSubmitting, submitForm, errors, values, setFieldTouched, setFieldValue }) => (
  <FoForm>
    <Dimmer active={isSubmitting} loader={isSubmitting} >
      <Form.Group className='mb-0'>
        <Form.Label className="custom-switch">
          <Field 
            className="custom-switch-input"
            type="checkbox" 
            name="included" 
            onChange={() => {
              setFieldValue('included', !values.included)
              setFieldTouched('included', true)
              setSubmitting(true)
              setTimeout(() => {submitForm()}, 200)
            }}
            checked={values.included} 
            disabled={disabled} 
          />
          <span className="custom-switch-indicator" ></span>
          <span className="custom-switch-description">{t('general.included')}</span>
        </Form.Label>
        <ErrorMessage name="included" component="div" />   
      </Form.Group>  
    </Dimmer>
  </FoForm>
)

export default withTranslation()(withRouter(ScheduleEventTicketEditActivityForm))