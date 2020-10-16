// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_SYSTEM_SETTINGS_QUERY, UPDATE_SYSTEM_SETTING } from '../../queries'

import {
  Dimmer,
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container,
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

// import FinancePaymentMethodForm from './AppSettingsGeneralForm'
import SettingsBase from "../../SettingsBase"
import SettingsGeneralSystemForm from "./SettingsGeneralSystemForm"


function SettingsGeneralSystem({ t, match, history }) {
  const headerSubTitle = t('settings.general.title')
  const cardTitle = t("settings.general.system.title")
  const sidebarActive = "general"
  const queryVariables = {
    setting: "system_hostname"
  }

  const { loading, error, data } = useQuery(GET_SYSTEM_SETTINGS_QUERY, {
    variables: queryVariables
  })
  const [ updateSettings, { data: updateData }] = useMutation(UPDATE_SYSTEM_SETTING)

  console.log('query data settings')
  console.log(data)

  if (loading) {
    return (
      <SettingsBase 
          headerSubTitle={headerSubTitle}
          cardTitle={cardTitle}
          sidebarActive={sidebarActive}>  
        <Card.Body>
          <Dimmer active={true}
                  loader={true}>
          </Dimmer>
        </Card.Body>
      </SettingsBase>
    )
  }
  if (error) {
    return (
      <SettingsBase 
          headerSubTitle={headerSubTitle}
          cardTitle={cardTitle}
          sidebarActive={sidebarActive}>  
        <Card.Body>
          {t("settings.general.error_loading")}
        </Card.Body>
      </SettingsBase>
    )
  }

  let hostname = ""
  if (data.systemSettings.edges.length) {
    hostname = data.systemSettings.edges[0].node.value 
  }


  return (
    <SettingsBase 
      headerSubTitle={headerSubTitle}
      cardTitle={cardTitle}
      sidebarActive={sidebarActive}
    >  
    <Formik
      initialValues={{ 
        system_hostname: hostname
      }}
      // validationSchema={MOLLIE_SCHEMA}
      onSubmit={(values, { setSubmitting }, errors) => {
          console.log('submit values:')
          console.log(values)
          console.log(errors)

          updateSettings({ variables: {
            input: {
              setting: "system_hostname",
              value: values.system_hostname
            }
          }, refetchQueries: [
              { query: GET_SYSTEM_SETTINGS_QUERY, variables: queryVariables }
          ]})
          .then(({ data }) => {
              console.log('got data', data)
              toast.success((t('settings.general.toast_edit_success')), {
                  position: toast.POSITION.BOTTOM_RIGHT
              })
              setSubmitting(false)
            }).catch((error) => {
              toast.error((t('general.toast_server_error')) + ': ' +  error, {
                  position: toast.POSITION.BOTTOM_RIGHT
              })
              console.log('there was an error sending the query', error)
              setSubmitting(false)
            })
      }}
    >
      {({ isSubmitting, errors, values }) => (
        <SettingsGeneralSystemForm
          isSubmitting={isSubmitting}
          errors={errors}
          values={values}
        >
          {console.log(errors)}
        </SettingsGeneralSystemForm>
      )}
      </Formik>
    </SettingsBase>
  )
}


export default withTranslation()(withRouter(SettingsGeneralSystem))