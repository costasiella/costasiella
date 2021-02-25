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
import SettingsWorkflowClassBookingForm from "./SettingsWorkflowClassBookingForm"


function SettingsWorkflowClassBooking({ t, match, history }) {
  const headerSubTitle = t('settings.workflow.title')
  const cardTitle = t("settings.workflow.class_booking.title")

  const { 
    loading: loadingDaysAdvance, 
    error: errorDaysAdvance, 
    data: dataDaysAdvance 
  } = useQuery(GET_SYSTEM_SETTINGS_QUERY, {
    variables: {
      setting: "workflow_class_book_days_advance"
    }
  })
  const { 
    loading: loadingCancelUntil, 
    error: errorCancelUntil, 
    data: dataCancelUntil 
  } = useQuery(GET_SYSTEM_SETTINGS_QUERY, {
    variables: {
      setting: "workflow_class_cancel_until"
    }
  })
  const [ updateSettings, { data: updateData }] = useMutation(UPDATE_SYSTEM_SETTING)

  if ((loadingDaysAdvance) || (loadingCancelUntil)) {
    return (
      <SettingsBase 
          headerSubTitle={headerSubTitle}
          cardTitle={cardTitle}
      >  
        <Card.Body>
          <Dimmer active={true}
                  loader={true}>
          </Dimmer>
        </Card.Body>
      </SettingsBase>
    )
  }
  if ((errorDaysAdvance) || errorCancelUntil) {
    return (
      <SettingsBase 
          headerSubTitle={headerSubTitle}
          cardTitle={cardTitle}
      >  
        <Card.Body>
          {t("settings.general.error_loading")}
        </Card.Body>
      </SettingsBase>
    )
  }

  console.log('query data app settings')
  console.log(dataDaysAdvance)
  console.log(dataCancelUntil)

  let initialValues = {
    workflow_class_book_days_advance: "30",
    workflow_class_cancel_until: "2"
  }
  if (dataDaysAdvance.systemSettings.edges.length){
    initialValues['workflow_class_book_days_advance'] = dataDaysAdvance.systemSettings.edges[0].node.value
  } 
  if (dataCancelUntil.systemSettings.edges.length){
    initialValues['workflow_class_cancel_until'] = dataCancelUntil.systemSettings.edges[0].node.value
  } 
    


  return (
    <SettingsBase 
      headerSubTitle={headerSubTitle}
      cardTitle={cardTitle}
    >  
    <Formik
      initialValues={{ 
        workflow_class_book_days_advance: initialValues['workflow_class_book_days_advance'],
        workflow_class_cancel_until: initialValues['workflow_class_cancel_until']
      }}
      // validationSchema={MOLLIE_SCHEMA}
      onSubmit={(values, { setSubmitting }, errors) => {
          console.log('submit values:')
          console.log(values)
          console.log(errors)

          const settings = [
            { setting: "workflow_class_book_days_advance", value: values.workflow_class_book_days_advance },
            { setting: "workflow_class_cancel_until", value: values.workflow_class_cancel_until },
          ]

          let error = false

          for (let i in settings) {

            console.log(i)
            console.log(settings[i].setting)
            console.log(settings[i].value)

            updateSettings({ variables: {
              input: {
                setting: settings[i].setting,
                value: settings[i].value,
              }
            }, refetchQueries: [
                {query: GET_SYSTEM_SETTINGS_QUERY, variables: { setting: settings[i].setting }},
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
          }
      }}
    >
      {({ isSubmitting, errors, values }) => (
        <SettingsWorkflowClassBookingForm
          isSubmitting={isSubmitting}
          errors={errors}
          values={values}
        >
          {console.log(errors)}
        </SettingsWorkflowClassBookingForm>
      )}
      </Formik>
    </SettingsBase>
  )
}


export default withTranslation()(withRouter(SettingsWorkflowClassBooking))