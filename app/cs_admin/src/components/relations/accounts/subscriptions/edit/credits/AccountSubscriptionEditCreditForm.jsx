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
import { tinymceBasicConf } from "../../../../../../plugin_config/tinymce"
import CSDatePicker from "../../../../../ui/CSDatePicker"

function AccountSubscriptionEditCreditForm ({ 
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

  let title
  if ( formTitle == "create" ) {
    title = t('relations.account.subscriptions.credits.add')
  } else {
    title = t('relations.account.subscriptions.credits.edit')
  }

  return (
    <FoForm>
      <Card.Body>
        <h5>{title}</h5>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.credits')}>
              <Field type="number" 
                      name="mutationAmount" 
                      className={(errors.mutationAmount) ? "form-control is-invalid" : "form-control"} 
                      autoComplete="off" />
              <ErrorMessage name="mutationAmount" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('relations.account.subscriptions.credits.mutationType')}>
              <Field component="select" 
                     name="mutationType" 
                     className={(errors.mutationType) ? "form-control is-invalid" : "form-control"} 
                     autoComplete="off">
                <option value="ADD">{t("general.add")}</option>
                <option value="SUB">{t("general.subtract")}</option>
              </Field>
              <ErrorMessage name="mutationType" component="span" className="invalid-feedback" />
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
                onChange={(e) => setFieldValue("description", e.target.getContent())}
                onBlur={() => setFieldTouched("description", true)}
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
          <Button color="link" onClick={() => history.push(returnUrl)} role="button">
              {t('general.cancel')}
          </Button>
      </Card.Footer>
    </FoForm>
  )
}

export default withTranslation()(withRouter(AccountSubscriptionEditCreditForm))