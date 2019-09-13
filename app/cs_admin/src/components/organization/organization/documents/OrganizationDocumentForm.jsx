import React, { useState, useRef } from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'

import CSDatePicker from "../../../ui/CSDatePicker"


import {
  Button,
  Card,
  Form,
  Grid
} from "tabler-react"


const customFileInputLabelStyle = {
  whiteSpace: "nowrap",
  display: "block",
  overflow: "hidden"
}
  

function OrganizationDocumentForm ({ t, history, isSubmitting, values, errors, setFieldTouched, setFieldValue, return_url }) {
  const [fileName, setFileName] = useState(values.fileName)
  const inputFileName = useRef(null)
  const fileInputLabel = fileName || t("general.custom_file_input_inner_label")


  const _handleOnChange = (event) => {
    console.log('on change triggered')
    setFileName(event.target.files[0].name)
  }

  return (
    <FoForm>
      <Card.Body>
        <Grid.Row>
          <Grid.Col>
            <Form.Group label={t('general.version')}>
              <Field type="text" 
                    name="version" 
                    className={(errors.version) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
              <ErrorMessage name="version" component="span" className="invalid-feedback" />
            </Form.Group>
          </Grid.Col>
          <Grid.Col>
            <Form.Group label={t('general.custom_file_input_label')}>
              <div className="custom-file">
                <input type="file" ref={inputFileName} className="custom-file-input" onChange={_handleOnChange} />
                <label className="custom-file-label" style={customFileInputLabelStyle}>
                  {fileInputLabel}
                </label>
              </div>
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
        <Button color="link" onClick={() => history.push(return_url)}>
          {t('general.cancel')}
        </Button>
      </Card.Footer>
    </FoForm>
  )
}
  
  
  export default withTranslation()(withRouter(OrganizationDocumentForm))