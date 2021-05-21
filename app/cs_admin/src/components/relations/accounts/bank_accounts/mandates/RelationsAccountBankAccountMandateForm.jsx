// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from "uuid"
import { Link } from 'react-router-dom'

import {
  Button,
  Card,
  Form,
  Grid,
} from "tabler-react";

import CSDatePicker from "../../../../ui/CSDatePicker"
import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../../../plugin_config/tinymce"


const RelationsAccountBankAccountMandateForm = ({ t, history, inputData, isSubmitting, setFieldValue, setFieldTouched, errors, values, returnUrl }) => (
  <FoForm>
    <Card.Body>
      <Grid.Row>
        <Grid.Col>
          <Form.Group label={t('relations.account.bank_accounts.mandates.reference')}>
            <Field type="text" 
                    name="reference" 
                    className={(errors.reference) ? "form-control is-invalid" : "form-control"}
                    placeholder={t('relations.account.bank_accounts.mandates.reference_placeholder')}
                    autoComplete="off" />
            <ErrorMessage name="reference" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
        <Grid.Col>
          <Form.Group label={t('relations.account.bank_accounts.mandates.signature_date')}>
            <CSDatePicker 
              selected={values.signatureDate}
              onChange={(date) => setFieldValue("signatureDate", date)}
              onBlur={() => setFieldTouched("signatureDate", true)}
            />
            <ErrorMessage name="signatureDate" component="span" className="invalid-feedback" />
          </Form.Group>
        </Grid.Col>
      </Grid.Row>
      <Grid.Row>
        <Grid.Col>
          <Form.Group label={t('relations.account.bank_accounts.mandates.content')}>
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


export default withTranslation()(withRouter(RelationsAccountBankAccountMandateForm))