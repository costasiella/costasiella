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


let noteFormTypingTimer
const formSubmitTimeout = 750

// Use editor as controlled component:
// https://github.com/tinymce/tinymce-react/blob/master/README.md

const FinanceInvoiceEditNoteForm = ({ t, isSubmitting, values, errors, handleChange, submitForm, setFieldTouched, setFieldValue }) => (
  <Dimmer loader={isSubmitting} active={isSubmitting}>
    <FoForm>
      <Form.Group label={t('general.note')}>
        <Editor
            textareaName="note"
            initialValue={values.note}
            init={tinymceBasicConf}
            onEditorChange={(content, editor) => {
              clearTimeout(noteFormTypingTimer)
              setFieldValue("note", content)
              setFieldTouched("note", true)
              noteFormTypingTimer = setTimeout(() => {
                submitForm()
              }, formSubmitTimeout)         
            }}
            onKeyDown={() => clearTimeout(noteFormTypingTimer)}
            onBlur={() => setFieldTouched("note", true)}
          />
        <ErrorMessage name="note" component="span" className="invalid-feedback" />
      </Form.Group>
    </FoForm>
  </Dimmer>
)

export default withTranslation()(withRouter(FinanceInvoiceEditNoteForm))