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
import { tinymceBasicConf } from "../../../../plugin_config/tinymce"


let termsFormTypingTimer
const formSubmitTimeout = 750

// Use editor as controlled component:
// https://github.com/tinymce/tinymce-react/blob/master/README.md

const FinanceInvoiceEditTermsForm = ({ t, isSubmitting, values, errors, handleChange, submitForm, setFieldTouched, setFieldValue }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group label={t('general.terms_and_conditions')}>
        <Editor
            textareaName="terms"
            initialValue={values.terms}
            init={tinymceBasicConf}
            onEditorChange={(content, editor) => {
              clearTimeout(termsFormTypingTimer)
              setFieldValue("terms", content)
              setFieldTouched("terms", true)
              termsFormTypingTimer = setTimeout(() => {
                submitForm()
              }, formSubmitTimeout)         
            }}
            onKeyDown={() => clearTimeout(termsFormTypingTimer)}
            onBlur={() => setFieldTouched("terms", true)}
          />
        <ErrorMessage name="terms" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FinanceInvoiceEditTermsForm))