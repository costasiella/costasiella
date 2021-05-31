// @flow

import React, { useContext, useState } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

// import { GET_ACCOUNTS_QUERY, GET_ACCOUNT_QUERY } from './queries'
// import { ACCOUNT_SCHEMA } from './yupSchema'

import OrganizationContext from '../../context/OrganizationContext'

import {
  Card,
  Button,
  StandaloneFormPage,
} from "tabler-react"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import { CSAuth } from "../../../tools/authentication"
import { TOKEN_COOKIE_DELETE, TOKEN_REFRESH_COOKIE_DELETE } from "../../../queries/system/auth"

import CSStandaloneFormPage from "../../ui/CSStandaloneFormPage"


function UserLogout({t, match, history}) {
  const [ deleteCookie ] = useMutation(TOKEN_COOKIE_DELETE)
  const [ deleteRefreshCookie ] = useMutation(TOKEN_REFRESH_COOKIE_DELETE)
  const [active, setActive] = useState(false)

  const organization = useContext(OrganizationContext)
  console.log(organization)

  return (
    <CSStandaloneFormPage urlLogo={organization.urlLogoLogin}>
      {/* TODO: point imageURL to logo */}
      <Card>
        <Card.Body>
          <Card.Title>
            {t('user.logout.title')}
          </Card.Title>
          {t('user.logout.confirmation_message')} <br /><br />
          <Button 
            block
            loading={active}
            disabled={active}
            color="primary"
            type="button" 
            onClick={() => {
              setActive(true)
              CSAuth.logout()
              deleteCookie().then(({ data }) => {
                console.log('got data', data)
                })
              .catch((error) => {
                console.log(error)
              })
              deleteRefreshCookie().then(({ data }) => {
                console.log('got data', data)
                })
              .catch((error) => {
                console.log(error)
              })
              setTimeout(() => toast.info(t('user.logout.success'), {
                position: toast.POSITION.BOTTOM_RIGHT
              }), 350)
              setTimeout(() => history.push('/'), 250)
            }}
          >
            {t('general.logout')}
          </Button>
        </Card.Body>
      </Card>
      <Button 
        block
        color="link"
        onClick={(event) => {
          event.preventDefault()  
          window.history.back()
        }}
      >
        {t('general.cancel')}
      </Button>
    </CSStandaloneFormPage>
  )
}

export default withTranslation()(withRouter(UserLogout))