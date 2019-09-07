// @flow

import React, { useState } from 'react'
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
  StandaloneFormPage,
} from "tabler-react"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import { CSAuth } from "../../../tools/authentication"


function UserSessionExpired({t, match, history}) {
  const [active, setActive] = useState(false);

  return (
    <StandaloneFormPage imageURL="">
      {/* TODO: point imageURL to logo */}
      <Card>
        <Card.Body>
          <Card.Title>
            {t('user.session_expired.title')}
          </Card.Title>
          {t('user.session_expired.confirmation_message')} <br /><br />
          <Button 
            block
            loading={active}
            disabled={active}
            color="primary"
            type="button" 
            onClick={() => {
              setActive(true)
              CSAuth.logout()
              setTimeout(() => toast.info((t('user.session_expired.success')), {
                position: toast.POSITION.BOTTOM_RIGHT
              }), 350)
              setTimeout(() => history.push('/user/login'), 250)
            }}
          >
            {t('general.login')}
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
      <ToastContainer autoClose={5000}/>
    </StandaloneFormPage>
  )
}

export default withTranslation()(withRouter(UserSessionExpired))