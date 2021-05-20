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


const SettingsFinanceBankAccountsForm = ({ t, history, isSubmitting, errors, values, return_url }) => (
  <FoForm>
      <Card.Body>
        <Form.Group>
          <Form.Label className="custom-switch">
              <Field 
              className="custom-switch-input"
              type="checkbox" 
              name="finance_bank_accounts_iban" 
              checked={values.finance_bank_accounts_iban} />
              <span className="custom-switch-indicator" ></span>
              <span className="custom-switch-description">{t('settings.finance.bank_accounts.iban')}</span>
          </Form.Label>
          <ErrorMessage name="finance_bank_accounts_iban" component="div" />   
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

export default withTranslation()(withRouter(SettingsFinanceBankAccountsForm))