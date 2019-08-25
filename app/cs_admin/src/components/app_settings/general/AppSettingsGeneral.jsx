// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_APP_SETTINGS_QUERY } from './queries'
// import { PAYMENT_METHOD_SCHEMA } from './yupSchema'



import {
  Dimmer,
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

// import FinancePaymentMethodForm from './AppSettingsGeneralForm'
import AppSettingsBase from "../AppSettingsBase"
import AppSettingsMenu from "../AppSettingsMenu"


const UPDATE_PAYMENT_METHOD = gql`
  mutation UpdateFinancePaymentMethod($input: UpdateFinancePaymentMethodInput!) {
    updateFinancePaymentMethod(input: $input) {
      financePaymentMethod {
        id
        name
        code
      }
    }
  }
`

function AppSettingsGeneral({ t, match, history }) {
  const { loading, error, data } = useQuery(GET_APP_SETTINGS_QUERY)
  const cardTitle = t("settings.general.title")
  const sidebarActive = "general"

  console.log('queyr data app settings')
  console.log(data)

  if (loading) {
    return (
      <AppSettingsBase 
          cardTitle={cardTitle}
          sidebarActive={sidebarActive}>  
        <Card.Body>
          <Dimmer active={true}
                  loader={true}>
          </Dimmer>
        </Card.Body>
      </AppSettingsBase>
    )
  }
  if (error) {
    return (
      <AppSettingsBase 
          cardTitle={cardTitle}
          sidebarActive={sidebarActive}>  
        <Card.Body>
          {t("settings.general.error_loading")}
        </Card.Body>
      </AppSettingsBase>
    )
  }


  return (
    <AppSettingsBase 
    cardTitle={cardTitle}
      sidebarActive={sidebarActive}
    >  

    </AppSettingsBase>
  )
}


export default withTranslation()(withRouter(AppSettingsGeneral))