import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"

import {
    Button,
    Card,
    Form,
    Grid
  } from "tabler-react"
  import { Form as FoForm, Field, ErrorMessage } from 'formik'

import CSDatePicker from "../../ui/CSDatePicker"
import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../plugin_config/tinymce"

function OrganizationAnnouncementForm({ t, history, isSubmitting, values, errors, setFieldTouched, setFieldValue, returnUrl }) {
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
                  <span className="custom-switch-description">{t('organization.announcements.display_public')}</span>
              </Form.Label>
              <ErrorMessage name="displayPublic" component="div" />   
            </Form.Group>  
          </Grid.Col>
          <Grid.Col>
            <Form.Group>
              <Form.Label className="custom-switch">
                  <Field 
                  className="custom-switch-input"
                  type="checkbox" 
                  name="displayShop" 
                  checked={values.displayShop} />
                  <span className="custom-switch-indicator" ></span>
                  <span className="custom-switch-description">{t('organization.announcements.display_shop')}</span>
              </Form.Label>
              <ErrorMessage name="displayShop" component="div" />   
            </Form.Group>  
          </Grid.Col>
          <Grid.Col>
            <Form.Group>
              <Form.Label className="custom-switch">
                  <Field 
                  className="custom-switch-input"
                  type="checkbox" 
                  name="displayBackend" 
                  checked={values.displayBackend} />
                  <span className="custom-switch-indicator" ></span>
                  <span className="custom-switch-description">{t('organization.announcements.display_backend')}</span>
              </Form.Label>
              <ErrorMessage name="displayBackend" component="div" />   
            </Form.Group>  
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.title')}>
              <Field type="text" 
                      name="title" 
                      className={(errors.title) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="title" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('organization.announcements.content')}>
              <Editor
                textareaName="content"
                initialValue={values.content}
                init={tinymceBasicConf}
                onChange={(e) => setFieldValue("content", e.target.getContent())}
                onBlur={() => setFieldTouched("content", true)}
                />
              <ErrorMessage name="content" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
        </Grid.Row>
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
          <Grid.Col>
            <Form.Group label={t('general.priority')}>
              <Field type="text" 
                      name="priority" 
                      className={(errors.priority) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="priority" component="span" className="invalid-feedback" />
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
            <Button color="link">
                {t('general.cancel')}
            </Button>
          </Link>
      </Card.Footer>
    </FoForm>
  )
}
  
  
export default withTranslation()(withRouter(OrganizationAnnouncementForm))