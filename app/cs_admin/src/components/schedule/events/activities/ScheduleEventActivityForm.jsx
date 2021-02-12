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

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../../plugin_config/tinymce"
import CSDatePicker from "../../../ui/CSDatePicker"
import CSTimePicker from "../../../ui/CSTimePicker"

function ScheduleEventActivityForm ({ 
  t, 
  history, 
  match, 
  isSubmitting, 
  errors, 
  values, 
  inputData, 
  returnUrl, 
  setFieldTouched, 
  setFieldValue, 
  formTitle="create" })   
{

  return (
    <FoForm>
      <Card.Body>
        <Grid.Row>
          <Grid.Col>
            <Form.Group>
              <Form.Label className="custom-switch">
                  <Field 
                    className="custom-switch-input"
                    type="checkbox" 
                    name="displayPublic" 
                    checked={values.displayPublic} />
                  <span className="custom-switch-indicator" ></span>
                  <span className="custom-switch-description">{t('schedule.events.activities.public')}</span>
              </Form.Label>
              <ErrorMessage name="displayPublic" component="div" />   
            </Form.Group>  
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.name')}>
              <Field type="text" 
                      name="name" 
                      className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="name" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.location')}>
              <Field component="select" 
                    name="organizationLocationRoom" 
                    className={(errors.organizationLocationRoom) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
                <option value="" key={v4()}>{t("general.please_select")}</option>
                {inputData.organizationLocationRooms.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.organizationLocation.name} - {node.name}</option>
                )}
              </Field>
              <ErrorMessage name="organizationLocationRoom" component="span" className="invalid-feedback" />
            </Form.Group> 
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.spaces')}>
                <Field type="text" 
                    name="spaces" 
                    className={(errors.spaces) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
                <ErrorMessage name="spaces" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.date')}>
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
           <Form.Group label={t('general.time_start')}>
              <CSTimePicker 
                className={(errors.timeStart) ? "form-control is-invalid" : "form-control"} 
                selected={values.timeStart}
                onChange={(date) => setFieldValue("timeStart", date)}
                onBlur={() => setFieldTouched("timeStart", true)}
                clearable={false}
              />
              {/* {errors.timeStart}
              {errors.timeStart && touched.timeStart ? (
                <span className="invalid-feedback">{errors.timeStart} - hacky thingy</span>
              ) : null} */}
              <ErrorMessage name="timeStart" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
           <Form.Group label={t('general.time_end')}>
              <CSTimePicker 
                className={(errors.timeEnd) ? "form-control is-invalid" : "form-control"} 
                selected={values.timeEnd}
                onChange={(date) => setFieldValue("timeEnd", date)}
                onBlur={() => setFieldTouched("timeEnd", true)}
                clearable={false}
              />
              <ErrorMessage name="timeEnd" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.teacher')}>
              <Field component="select" 
                      name="account" 
                      className={(errors.account) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off">
                {console.log("query data in schedule class teacher add:")}
                {console.log(inputData)}
                <option value="" key={v4()}>{t('general.please_select')}</option>
                {inputData.accounts.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.fullName}</option>
                )}
              </Field>
              <ErrorMessage name="account" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.teacher2')}>
              <Field component="select" 
                      name="account2" 
                      className={(errors.account2) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off">
                <option value="" key={v4()}></option>
                {inputData.accounts.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.fullName}</option>
                )}
              </Field>
              <ErrorMessage name="account2" component="span" className="invalid-feedback" />
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
          <Button color="link" onClick={() => history.push(returnUrl)} role="button">
              {t('general.cancel')}
          </Button>
      </Card.Footer>
    </FoForm>
  )
}

export default withTranslation()(withRouter(ScheduleEventActivityForm))