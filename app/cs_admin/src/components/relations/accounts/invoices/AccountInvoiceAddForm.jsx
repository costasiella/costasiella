// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from "uuid"

import { Editor } from '@tinymce/tinymce-react'
import { tinymceBasicConf } from "../../../../plugin_config/tinymce"
import CSDatePicker from "../../../ui/CSDatePicker"


import {
  Button,
  Card,
  Form,
  Grid,
} from "tabler-react";


const AccountInvoiceAddForm = ({ t, history, inputData, isSubmitting, setFieldValue, setFieldTouched, errors, values, return_url }) => (
  <FoForm>
    <Card.Body> 
      <Form.Group label={t('general.last_name')}>
        <Field type="text" 
                name="lastName" 
                className={(errors.lastName) ? "form-control is-invalid" : "form-control"} 
                autoComplete="off" />
        <ErrorMessage name="lastName" component="span" className="invalid-feedback" />
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
        <Button
          type="button" 
          color="link" 
          onClick={() => history.push(return_url)}
        >
            {t('general.cancel')}
        </Button>
    </Card.Footer>
  </FoForm>
)


export default withTranslation()(withRouter(AccountInvoiceAddForm))