import React, { Component } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { v4 } from "uuid"

import {
    Button,
    Card,
    Form,
    Grid
  } from "tabler-react"
import { Form as FoForm, Field, ErrorMessage } from 'formik'

// import { Editor } from '@tinymce/tinymce-react'
// import { tinymceBasicConf } from "../../../plugin_config/tinymce"
import CSDatePicker from "../../../../ui/CSDatePicker"
import CSTimePicker from "../../../../ui/CSTimePicker"

const ScheduleClassEditForm = ({ t, history, inputData, isSubmitting, setFieldValue, setFieldTouched, errors, values, touched, return_url }) => (
    <FoForm>
      <Card.Body>
        {/* <Form.Group>
          <Form.Label className="custom-switch">
              <Field 
              className="custom-switch-input"
              type="checkbox" 
              name="displayPublic" 
              checked={values.displayPublic} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('schedule.classes.public')}</span>
          </Form.Label>
          <ErrorMessage name="displayPublic" component="div" />   
        </Form.Group>   */}
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.location')}>
              <Field component="select" 
                    name="organizationLocationRoom" 
                    className={(errors.organizationLocationRoom) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
                <option value="" key={v4()}>{t("general.no_change")}</option>
                {inputData.organizationLocationRooms.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.organizationLocation.name} - {node.name}</option>
                )}
              </Field>
              <ErrorMessage name="organizationLocationRoom" component="span" className="invalid-feedback" />
            </Form.Group> 
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.level')}>
              <Field component="select" 
                    name="organizationLevel" 
                    className={(errors.organizationLevels) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off">
                <option value="" key={v4()}>{t("general.no_change")}</option>
                {inputData.organizationLevels.edges.map(({ node }) =>
                  <option value={node.id} key={v4()}>{node.name}</option>
                )}
              </Field>
              <ErrorMessage name="organizationLevels" component="span" className="invalid-feedback" />
            </Form.Group> 
          </Grid.Col>
        </Grid.Row>
        <Form.Group label={t('general.class')}>
          <Field component="select" 
                name="organizationClasstype" 
                className={(errors.organizationClasstype) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off">
            <option value="" key={v4()}>{t("general.no_change")}</option>
            {inputData.organizationClasstypes.edges.map(({ node }) =>
              <option value={node.id} key={v4()}>{node.name}</option>
            )}
          </Field>
          <ErrorMessage name="organizationClasstype" component="span" className="invalid-feedback" />
        </Form.Group> 
        <Grid.Row>
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
        {/* <Form.Group label={t('general.note')}>
          <Editor
              textareaName="note"
              initialValue={values.note}
              init={tinymceBasicConf}
              onChange={(e) => setFieldValue("note", e.target.getContent())}
              onBlur={() => setFieldTouched("note", true)}
            />
          <ErrorMessage name="note" component="span" className="invalid-feedback" />
        </Form.Group> */}
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
        <Button color="link" onClick={() => history.push(return_url)}>
            {t('general.cancel')}
        </Button>
      </Card.Footer>
    </FoForm>
)
  
  
  export default withTranslation()(withRouter(ScheduleClassEditForm))