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

const AccountSubscriptionEditPauseForm = ({ t, history, match, isSubmitting, errors, values, inputData, return_url, setFieldTouched, setFieldValue }) => (
  <FoForm>
    <Card.Body>
      <Grid.Row>
        <Grid.Col>
          <Form.Group label={t('general.date_start')}>
            <CSDatePicker 
              selected={values.dateStart}
              onChange={(date) => setFieldValue("dateStart", date)}
              onBlur={() => setFieldTouched("dateStart", true)}
            />
            <ErrorMessage name="dateStart" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
        <Grid.Col>
          <Form.Group label={t('general.date_end')}>
            <CSDatePicker 
              selected={values.dateEnd}
              onChange={(date) => setFieldValue("dateEnd", date)}
              onBlur={() => setFieldTouched("dateEnd", true)}
            />
            <ErrorMessage name="dateEnd" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
      </Grid.Row>
      <Grid.Row>
        <Grid.Col>
        <Form.Group label={t('general.description')}>
          <Editor
              textareaName="description"
              initialValue={values.description}
              init={tinymceBasicConf}
              onChange={(e) => setFieldValue("note", e.target.getContent())}
              onBlur={() => setFieldTouched("note", true)}
            />
          <ErrorMessage name="description" component="span" className="invalid-feedback" />
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
        <Button color="link" onClick={() => history.push(return_url)} role="button">
            {t('general.cancel')}
        </Button>
    </Card.Footer>
  </FoForm>
);

export default withTranslation()(withRouter(AccountSubscriptionEditPauseForm))