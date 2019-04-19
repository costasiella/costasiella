// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'


import {
  Button,
  Card,
  Form,
} from "tabler-react"


const OrganizationLocationRoomForm = ({ t, history, match, isSubmitting, errors, values, return_url }) => (
  <FoForm>
      <Card.Body>
          <Form.Group>
            <Form.Label className="custom-switch">
              <Field 
                className="custom-switch-input"
                type="checkbox" 
                name="displayPublic" 
                checked={values.displayPublic} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('organization.location_room.public')}</span>
            </Form.Label>
            <ErrorMessage name="displayPublic" component="div" />   
          </Form.Group>    

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
          <Button color="link" onClick={() => history.push(return_url + match.params.location_id)}>
              {t('general.cancel')}
          </Button>
      </Card.Footer>
  </FoForm>
);

export default withTranslation()(withRouter(OrganizationLocationRoomForm))