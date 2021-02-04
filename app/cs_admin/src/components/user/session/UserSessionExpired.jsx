// @flow

import React, { useContext, useState } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { ToastContainer } from 'react-toastify'
import { toast } from 'react-toastify'

// import { GET_ACCOUNTS_QUERY, GET_ACCOUNT_QUERY } from './queries'
// import { ACCOUNT_SCHEMA } from './yupSchema'

import {
  Card,
  Button,
  Icon,
  StandaloneFormPage,
} from "tabler-react"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import OrganizationContext from '../../context/OrganizationContext'
import { CSAuth } from "../../../tools/authentication"
import CSStandaloneFormPage from "../../ui/CSStandaloneFormPage"

function UserSessionExpired({t, match, history}) {
  const organization = useContext(OrganizationContext)
  console.log(organization)

  const [active, setActive] = useState(false);

  return (
    <CSStandaloneFormPage>
      {/* TODO: point imageURL to logo */}
      <Card>
        <Card.Body>
          <Card.Title>
            {t('user.session_expired.title')}
          </Card.Title>
          {t('user.session_expired.message')} <br /><br />
          <Button 
            block
            loading={active}
            disabled={active}
            color="primary"
            type="button" 
            onClick={() => {
              setActive(true)
              setTimeout(() => history.push('/user/login'), 250)
            }}
          >
            {t('user.session_expired.go_to_login')} <Icon name="chevron-right" />
          </Button>
        </Card.Body>
      </Card>
      <ToastContainer autoClose={5000}/>
    </CSStandaloneFormPage>
  )
}

export default withTranslation()(withRouter(UserSessionExpired))