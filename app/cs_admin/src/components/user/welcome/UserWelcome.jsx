// @flow

import React, { useContext, useState } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { ToastContainer } from 'react-toastify'
import { toast } from 'react-toastify'
import { Link } from "react-router-dom"

import GET_USER_PROFILE from "../../../queries/system/get_user_profile"


import OrganizationContext from '../../context/OrganizationContext'

import {
  Card,
  Button,
  Grid,
  Icon
} from "tabler-react"
// import HasPermissionWrapper from "../../HasPermissionWrapper"

import CSStandalonePageWide from "../../ui/CSStandalonePageWide"


function Welcome({t, match, history}) {
  const organization = useContext(OrganizationContext)
  console.log(organization)
  const { loading, error, data } = useQuery(GET_USER_PROFILE)

  if (loading) return (
    <CSStandalonePageWide urlLogo={organization.urlLogoLogin}>
      {t("general.loading_with_dots")}
    </CSStandalonePageWide>
  )
  if (error) return (
    <CSStandalonePageWide urlLogo={organization.urlLogoLogin}>
      {t("shop.account.class_info.error_loading_data")}
    </CSStandalonePageWide>
  )

  const user = data.user
  console.log(user)

  if (!user.employee && !user.teacher) {
    history.push("/shop")
  } 


  return (
    <CSStandalonePageWide urlLogo={organization.urlLogoLogin}>
      <div className="text-center mb-5">
        <h2>{t("general.welcome")} {user.firstName}</h2>
        <h5>{t("user.welcome.where_next_question")}</h5>
      </div>
      <Grid.Row>
        <Grid.Col md={3} offsetMd={3}>
          <Card>
            <Card.Body>
              <h5>Shop</h5>
              Shop and your personal profile. <br /><br />
              <Link to="/shop">
                <Button 
                  block
                  outline
                  color="primary"
                >
                  To shop <Icon name="chevron-right" />
                </Button>
              </Link>
            </Card.Body>
          </Card>
        </Grid.Col>
        <Grid.Col md={3}>
          <Card>
            <Card.Body>
              <h5>Back end</h5>
              Organization management. <br /><br />
              <Link to="/">
                <Button 
                  block
                  outline
                  color="primary"
                >
                  To back end <Icon name="chevron-right" />
                </Button>
              </Link>
            </Card.Body>
          </Card>
        </Grid.Col>
        <Grid.Col md={3} offsetMd={3}>
          <Card>
            <Card.Body>
              <h5>Self check-in</h5>
              Customer self service check-in. <br /><br />
              <Link to="/">
                <Button 
                  block
                  outline
                  color="primary"
                >
                  To self check-in <Icon name="chevron-right" />
                </Button>
              </Link>
            </Card.Body>
          </Card>
        </Grid.Col>
      </Grid.Row>
    </CSStandalonePageWide>
  )
}

export default withTranslation()(withRouter(Welcome))