// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'


import {
  Dimmer,
  Form,
} from "tabler-react"

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../plugin_config/tinymce"


let termsFormTypingTimer


const FinanceInvoiceEditTermsForm = ({ t, isSubmitting, values, errors, handleChange, submitForm, setFieldTouched, setFieldValue }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group label={t('general.terms_and_conditions')}>
        <Editor
            textareaName="terms"
            initialValue={values.terms}
            init={tinymceBasicConf}
            onChange={(e) => setFieldValue("terms", e.target.getContent())}
            onBlur={() => setFieldTouched("terms", true)}
          />
        <ErrorMessage name="terms" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FinanceInvoiceEditTermsForm))