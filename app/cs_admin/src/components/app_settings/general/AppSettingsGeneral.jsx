// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_APP_SETTINGS_QUERY, UPDATE_APP_SETTINGS } from '../queries'
import { GENERAL_SCHEMA } from './yupSchema'



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
import AppSettingsGeneralForm from "./AppSettingsGeneralForm"


function AppSettingsGeneral({ t, match, history }) {
  const cardTitle = t("settings.general.title")
  const sidebarActive = "general"

  const { loading, error, data } = useQuery(GET_APP_SETTINGS_QUERY)
  const [ updateSettings, { data: updateData }] = useMutation(UPDATE_APP_SETTINGS)

  console.log('query data app settings')
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
    <Formik
      initialValues={{ 
        dateFormat: data.appSettings.dateFormat,
        timeFormat: data.appSettings.timeFormat,
        note: "",
      }}
      validationSchema={GENERAL_SCHEMA}
      onSubmit={(values, { setSubmitting }, errors) => {
          console.log('submit values:')
          console.log(values)
          console.log(errors)

          updateSettings({ variables: {
            input: {
              dateFormat: values.dateFormat,
              timeFormat: values.timeFormat,
            }
          }, refetchQueries: [
              {query: GET_APP_SETTINGS_QUERY}
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
        <AppSettingsGeneralForm
          isSubmitting={isSubmitting}
          errors={errors}
          values={values}
        >
          {console.log(errors)}
        </AppSettingsGeneralForm>
      )}
      </Formik>
    </AppSettingsBase>
  )
}


export default withTranslation()(withRouter(AppSettingsGeneral))