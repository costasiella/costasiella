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


let footerFormTypingTimer
const formSubmitTimeout = 750

// Use editor as controlled component:
// https://github.com/tinymce/tinymce-react/blob/master/README.md

const FinanceInvoiceEditFooterForm = ({ t, isSubmitting, values, errors, handleChange, submitForm, setFieldTouched, setFieldValue }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group label={t('general.footer')}>
        <Editor
            textareaName="footer"
            initialValue={values.footer}
            init={tinymceBasicConf}
            onEditorChange={(content, editor) => {
              clearTimeout(footerFormTypingTimer)
              setFieldValue("footer", content)
              setFieldTouched("footer", true)
              footerFormTypingTimer = setTimeout(() => {
                submitForm()
              }, formSubmitTimeout)         
            }}
            onKeyDown={() => clearTimeout(footerFormTypingTimer)}
            onBlur={() => setFieldTouched("footer", true)}
          />
        <ErrorMessage name="footer" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FinanceInvoiceEditFooterForm))