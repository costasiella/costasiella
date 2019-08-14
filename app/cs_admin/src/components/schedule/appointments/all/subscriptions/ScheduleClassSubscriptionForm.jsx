// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from 'uuid'

import {
  Button,
  Card,
  Dimmer,
  Grid,
  Form,
  Table,
  Text
} from "tabler-react"


import FormHelp from "../../../../ui/FormHelp"


const ScheduleClassSubscriptionForm = ({ t, history, match, isSubmitting, submitForm, errors, values, setFieldTouched, setFieldValue }) => (
  <FoForm>
    <Dimmer active={isSubmitting} loader={isSubmitting} >
      <Grid.Row>
        <Grid.Col>
          <Form.Group className='mb-0'>
            <Form.Label className="custom-switch">
              <Field 
                className="custom-switch-input"
                type="checkbox" 
                name="enroll" 
                onChange={() => {
                  setFieldValue('enroll', !values.enroll)
                  setFieldTouched('enroll', true)
                  if (!values.enroll) {
                    setFieldValue('attend', true)
                    setFieldTouched('attend', true)
                  }
                  setTimeout(() => {submitForm()}, 200)
                }}
                checked={values.enroll} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('general.enroll')}</span>
            </Form.Label>
            <ErrorMessage name="enroll" component="div" />   
          </Form.Group>  
        </Grid.Col>
        <Grid.Col>
          <Form.Group className='mb-0'>
            <Form.Label className="custom-switch">
              <Field 
                className="custom-switch-input"
                type="checkbox" 
                name="shopBook" 
                onChange={() => {
                  setFieldValue('shopBook', !values.shopBook)
                  setFieldTouched('shopBook', true)
                  if (!values.shopBook) {
                    setFieldValue('attend', true)
                    setFieldTouched('attend', true)
                  }
                  setTimeout(() => {submitForm()}, 200)
                }}
                checked={values.shopBook} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('schedule.classes.subscriptions.shop_book')}</span>
            </Form.Label>
            <ErrorMessage name="shopBook" component="div" />   
          </Form.Group>  
        </Grid.Col>
        <Grid.Col>
          <Form.Group className='mb-0'>
            <Form.Label className="custom-switch">
              <Field 
                className="custom-switch-input"
                type="checkbox" 
                name="attend" 
                disabled={((values.shopBook) || (values.enroll))}
                onChange={() => {
                  setFieldValue('attend', !values.attend)
                  setFieldTouched('attend', true)
                  setTimeout(() => {submitForm()}, 200)
                }}
                checked={values.attend} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('general.attend')}</span>
            </Form.Label>
            {/* Show message to inform user they can't disable attend while enroll or shopBook is enabled*/}
            { ((values.shopBook) || (values.enroll)) ? <div>
                <Text.Small>{t('schedule.classes.subscriptions.attend_disabled')}</Text.Small> { ' ' }
                <FormHelp message={t('schedule.classes.subscriptions.attend_disabled_help')} />
              </div> : "" }
            <ErrorMessage name="attend" component="div" />   
          </Form.Group>  
        </Grid.Col>
      </Grid.Row>
    </Dimmer>
  </FoForm>
);

export default withTranslation()(withRouter(ScheduleClassSubscriptionForm))