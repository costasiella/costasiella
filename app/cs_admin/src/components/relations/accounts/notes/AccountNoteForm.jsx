// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { Link } from "react-router-dom"

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../../plugin_config/tinymce"


import {
  Button,
  Card,
  Form,
  Grid,
} from "tabler-react";


const AccountNoteForm = ({ t, history, isSubmitting, values, errors, setFieldTouched, setFieldValue, returnUrl }) => (
  <FoForm>
    <Card.Body> 
      <Grid.Row>
        <Grid.Col>
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
        </Grid.Col>
      </Grid.Row>
      <Grid.Row>
        <Grid.Col>
          <Form.Group>
            <Form.Label className="custom-switch">
                <Field 
                className="custom-switch-input"
                type="checkbox" 
                name="injury" 
                checked={values.injury} />
                <span className="custom-switch-indicator" ></span>
                <span className="custom-switch-description">{t('general.injury')}</span>
            </Form.Label>
            <ErrorMessage name="injury" component="div" />   
          </Form.Group>  
        </Grid.Col>
      </Grid.Row>
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
  </FoForm>
)


export default withTranslation()(withRouter(AccountNoteForm))