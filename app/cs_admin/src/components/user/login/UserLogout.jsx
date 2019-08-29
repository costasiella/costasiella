// @flow

import React, {Component } from 'react'
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


function UserLogout({t, match, history}) {
  let active = false

  return (
    <StandaloneFormPage imageURL="">
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
          type="submit" 
          onClick={() => {
            active = true
            CSAuth.logout()
            setTimeout(() => toast.info((t('user.logout.success')), {
              position: toast.POSITION.BOTTOM_RIGHT
            }), 350)
            setTimeout(() => history.push('/user/login'), 250)
          }}
        >
          {t('general.logout')}
        </Button>
        </Card.Body>
      </Card>
      <ToastContainer autoClose={5000}/>
    </StandaloneFormPage>
  )
}

export default withTranslation()(withRouter(UserLogout))