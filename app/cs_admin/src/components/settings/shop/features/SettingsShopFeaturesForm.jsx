// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Form as FoForm, Field, ErrorMessage } from 'formik'
import { v4 } from 'uuid'


import {
  Button,
  Card,
  Form,
} from "tabler-react"


const SettingsShopFeaturesForm = ({ t, history, isSubmitting, errors, values, return_url }) => (
  <FoForm>
      <Card.Body>
        {/* <Form.Group>
          <Form.Label className="custom-switch">
              <Field 
              className="custom-switch-input"
              type="checkbox" 
              name="memberships" 
              checked={values.memberships} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('general.memberships')}</span>
          </Form.Label>
          <ErrorMessage name="memberships" component="div" />   
        </Form.Group>   */}
        <Form.Group>
          <Form.Label className="custom-switch">
              <Field 
              className="custom-switch-input"
              type="checkbox" 
              name="subscriptions" 
              checked={values.subscriptions} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('general.subscriptions')}</span>
          </Form.Label>
          <ErrorMessage name="subscriptions" component="div" />   
        </Form.Group>  
        <Form.Group>
          <Form.Label className="custom-switch">
              <Field 
              className="custom-switch-input"
              type="checkbox" 
              name="classpasses" 
              checked={values.classpasses} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('general.classpasses')}</span>
          </Form.Label>
          <ErrorMessage name="classpasses" component="div" />   
        </Form.Group>  
        <Form.Group>
          <Form.Label className="custom-switch">
              <Field 
              className="custom-switch-input"
              type="checkbox" 
              name="classes" 
              checked={values.classes} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('general.classes')}</span>
          </Form.Label>
          <ErrorMessage name="classes" component="div" />   
        </Form.Group>  
        <Form.Group>
          <Form.Label className="custom-switch">
              <Field 
              className="custom-switch-input"
              type="checkbox" 
              name="events" 
              checked={values.events} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('general.events')}</span>
          </Form.Label>
          <ErrorMessage name="events" component="div" />   
        </Form.Group>  
      </Card.Body>
      <Card.Footer>
          <Button 
            color="primary"
            type="submit" 
            disabled={isSubmitting}
          >
            {t('general.submit')}
          </Button>
          {/* <Link to={return_url}>
            <Button 
              type="button" 
              color="link">
                {t('general.cancel')}
            </Button>
          </Link> */}
      </Card.Footer>
  </FoForm>
)

export default withTranslation()(withRouter(SettingsShopFeaturesForm))