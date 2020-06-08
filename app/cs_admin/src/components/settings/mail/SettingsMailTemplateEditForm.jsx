// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { Link } from 'react-router-dom'
import { v4 } from "uuid"

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../plugin_config/tinymce"


import {
  Button,
  Card,
  Form
} from "tabler-react";


function SettingsMailTemplateEditForm({ t, history, isSubmitting, errors, values, setFieldTouched, setFieldValue, returnUrl, cardTitle }) {


  return (
    <FoForm>
      <Card title={cardTitle}>
        <Card.Body>    
          <Form.Group label={t('general.subject')} >
            <Field type="text" 
                  name="subject" 
                  className={(errors.subject) ? "form-control is-invalid" : "form-control"} 
                  autoComplete="off" />
            <ErrorMessage name="subject" component="span" className="invalid-feedback" />
          </Form.Group>
          <Form.Group label={t('general.title')} >
            <Field type="text" 
                  name="title" 
                  className={(errors.title) ? "form-control is-invalid" : "form-control"} 
                  autoComplete="off" />
            <ErrorMessage name="title" component="span" className="invalid-feedback" />
          </Form.Group>
          <Form.Group label={t('general.description')}>
            <Editor
                textareaName="description"
                initialValue={values.description}
                init={tinymceBasicConf}
                onChange={(e) => setFieldValue("description", e.target.getContent())}
                onBlur={() => setFieldTouched("description", true)}
              />
            <ErrorMessage name="description" component="span" className="invalid-feedback" />
          </Form.Group>
          <Form.Group label={t('general.content')}>
            <Editor
                textareaName="content"
                initialValue={values.content}
                init={tinymceBasicConf}
                onChange={(e) => setFieldValue("content", e.target.getContent())}
                onBlur={() => setFieldTouched("content", true)}
              />
            <ErrorMessage name="content" component="span" className="invalid-feedback" />
          </Form.Group>
          <Form.Group label={t('general.comments')}>
            <Editor
                textareaName="comments"
                initialValue={values.comments}
                init={tinymceBasicConf}
                onChange={(e) => setFieldValue("comments", e.target.getContent())}
                onBlur={() => setFieldTouched("comments", true)}
              />
            <ErrorMessage name="comments" component="span" className="invalid-feedback" />
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
            <Link to={returnUrl}>
              <Button
                type="button" 
                color="link" 
              >
                {t('general.cancel')}
              </Button>
            </Link>
        </Card.Footer>
      </Card>
    </FoForm>
  )
}


export default withTranslation()(withRouter(SettingsMailTemplateEditForm))