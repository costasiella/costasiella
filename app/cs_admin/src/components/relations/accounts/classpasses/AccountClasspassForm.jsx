// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from "uuid"

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../../plugin_config/tinymce"
import CSDatePicker from "../../../ui/CSDatePicker"


import {
  Button,
  Card,
  Form,
  Grid,
} from "tabler-react";


const AccountClasspassForm = ({ t, history, inputData, isSubmitting, setFieldValue, setFieldTouched, errors, values, return_url }) => (
  <FoForm>
    <Card.Body> 
      <Grid.Row>
        <Grid.Col>
          <Form.Group label={t('general.classpass')}>
            <Field component="select" 
                  name="organizationClasspass" 
                  className={(errors.organizationClasspass) ? "form-control is-invalid" : "form-control"} 
                  autoComplete="off">
              <option value="" key={v4()}>{t('general.please_select')}</option>
              {inputData.organizationClasspasses.edges.map(({ node }) =>
                <option value={node.id} key={v4()}>{node.name}</option>
              )}
            </Field>
            <ErrorMessage name="organizationClasspass" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
      </Grid.Row> 
      <Grid.Row>
        <Grid.Col>
          <Form.Group label={t('general.date_start')}>
            <CSDatePicker 
              className={(errors.dateStart) ? "form-control is-invalid" : "form-control"} 
              selected={values.dateStart}
              onChange={(date) => {
                setFieldValue("dateStart", date)
                setFieldTouched("dateEnd", true)
              }}
              onBlur={() => setFieldTouched("dateStart", true)}
            />
            <ErrorMessage name="dateStart" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
        <Grid.Col>
          <Form.Group label={t('general.date_end')}>
            <CSDatePicker 
              selected={values.dateEnd}
              onChange={(date) => {
                setFieldValue("dateEnd", date)
                setFieldTouched("dateEnd", true)
              }}
              onBlur={() => setFieldTouched("dateEnd", true)}
              placeholderText={t('schedule.classes.placeholder_enddate')}
            />
            <ErrorMessage name="dateEnd" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
        </Grid.Row>
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
    </Card.Body>
    <Card.Footer>
        <Button 
          className="pull-right"
          color="primary"
          disabled={isSubmitting}
          type="submit"
        >
          {t('general.submit')}
        </Button>
        <Button
          type="button" 
          color="link" 
          onClick={() => history.push(return_url)}
        >
          {t('general.cancel')}
        </Button>
    </Card.Footer>
  </FoForm>
)


export default withTranslation()(withRouter(AccountClasspassForm))