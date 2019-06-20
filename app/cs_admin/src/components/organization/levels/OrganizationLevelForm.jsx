import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
    Button,
    Card,
    Form
  } from "tabler-react"
  import { Form as FoForm, Field, ErrorMessage } from 'formik'

const OrganizationLevelForm = ({ t, history, isSubmitting, errors, return_url }) => (
    <FoForm>
        <Card.Body>
            <Form.Group label={t('general.name')}>
            <Field type="text" 
                    name="name" 
                    className={(errors.name) ? "form-control is-invalid" : "form-control"} 
                    autoComplete="off" />
            <ErrorMessage name="name" component="span" className="invalid-feedback" />
            </Form.Group>
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
  
  
  export default withTranslation()(withRouter(OrganizationLevelForm))