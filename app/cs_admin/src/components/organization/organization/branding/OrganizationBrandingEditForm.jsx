import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
    Button,
    Card,
    Form,
    Grid
  } from "tabler-react"
  import { Form as FoForm, Field, ErrorMessage } from 'formik'

import { customFileInputLabelStyle } from "../../../../tools/custom_file_input_label_style"


const OrganizationBrandingEditForm = ({ 
  t, 
  history, 
  formTitle,
  isSubmitting, 
  inputFileName, 
  fileInputLabel, 
  handleFileInputChange=f=>f
}) => (
    <FoForm>
      <Card title={formTitle}>
        <Card.Body>
          <Grid.Row>
            <Grid.Col>
              <Form.Group label={t('general.custom_file_input_label')}>
                <div className="custom-file">
                  <input type="file" ref={inputFileName} className="custom-file-input" onChange={handleFileInputChange} />
                  <label className="custom-file-label" style={customFileInputLabelStyle}>
                    {fileInputLabel}
                  </label>
                </div>
              </Form.Group>
            </Grid.Col>
          </Grid.Row>
        </Card.Body>
        <Card.Footer>
            <Button 
            color="primary"
            // className="pull-right" 
            type="submit" 
            disabled={isSubmitting}
            >
            {t('general.submit')}
            </Button>
        </Card.Footer>
      </Card>
    </FoForm>
)
  
  
  export default withTranslation()(withRouter(OrganizationBrandingEditForm))