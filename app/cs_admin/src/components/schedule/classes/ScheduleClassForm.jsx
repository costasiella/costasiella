import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
    Button,
    Card,
    Form
  } from "tabler-react"
import { Form as FoForm, Field, ErrorMessage } from 'formik'

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../plugin_config/tinymce"

const ScheduleClassForm = ({ t, history, inputData, isSubmitting, setFieldValue, setFieldTouched, errors, values, return_url }) => (
    <FoForm>
      <Card.Body>
        <Form.Group>
          <Form.Label className="custom-switch">
              <Field 
              className="custom-switch-input"
              type="checkbox" 
              name="displayPublic" 
              checked={values.displayPublic} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('organization.classtype.public')}</span>
          </Form.Label>
          <ErrorMessage name="displayPublic" component="div" />   
        </Form.Group>  
        <Form.Group label={t('schedule.classes.frequencyType')}>
          <Field component="select" 
                name="frequencyType" 
                className={(errors.frequencyType) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off">
            <option value="SPECIFIC" key={v4()}>{t('schedule.classes.select_specific')}</option>
            <option value="WEEKLY" key={v4()}>{t('schedule.classes.select_weekly')}</option>
          </Field>
          <ErrorMessage name="frequencyType" component="span" className="invalid-feedback" />
        </Form.Group>
        { (values.frequencyType == "SPECIFIC") ? "" :
          <Form.Group label={t('schedule.classes.frequencyInterval')}>
            <Field component="select" 
                  name="frequencyType" 
                  className={(errors.frequencyType) ? "form-control is-invalid" : "form-control"} 
                  autoComplete="off">
              <option value="1" key={v4()}>{t('general.monday')}</option>
              <option value="2" key={v4()}>{t('general.tuesday')}</option>
              <option value="3" key={v4()}>{t('general.wednesday')}</option>
              <option value="4" key={v4()}>{t('general.thursday')}</option>
              <option value="5" key={v4()}>{t('general.friday')}</option>
              <option value="6" key={v4()}>{t('general.saturday')}</option>
              <option value="7" key={v4()}>{t('general.sunday')}</option>
            </Field>
            <ErrorMessage name="frequencyType" component="span" className="invalid-feedback" />
          </Form.Group>
        }
        <Form.Group label={t('general.membership')}>
          <Field component="select" 
                name="organizationLocationRoom" 
                className={(errors.organizationLocationRoom) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off">
            <option value="" key={v4()}>{t("general.please_select")}</option>
            {inputData.organizationLocationRooms.edges.map(({ node }) =>
              <option value={node.id} key={v4()}>{node.organizationLocation.name} - {node.name})</option>
            )}
          </Field>
          <ErrorMessage name="organizationMembership" component="span" className="invalid-feedback" />
        </Form.Group> 
        <Form.Group label={t('general.note')}>
          <Editor
              textareaName="note"
              initialValue={values.note}
              init={tinymceBasicConf}
              onChange={(e) => setFieldValue("note", e.target.getContent())}
              onBlur={() => setFieldTouched("note", true)}
            />
          <ErrorMessage name="note" component="span" className="invalid-feedback" />
        </Form.Group>
        {/* <Form.Group label={t('general.name')}>
          <Field type="text" 
                  name="name" 
                  className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                  autoComplete="off" />
          <ErrorMessage name="name" component="span" className="invalid-feedback" />
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
  
  
  export default withTranslation()(withRouter(ScheduleClassForm))