// @flow

import React, {Component } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_SYSTEM_MAIL_TEMPLATE_QUERY, UPDATE_SYSTEM_MAIL_TEMPLATE } from './queries'

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
import SettingsMailTemplateEditForm from "./SettingsMailTemplateEditForm"


function SettingsMailTemplateEdit({ t, match, history }) {
  const id = match.params.id
  const headerSubTitle = t('settings.mail.title')
  const cardTitle = t("settings.mail.templates.edit.title")

  const { loading, error, data } = useQuery(GET_SYSTEM_MAIL_TEMPLATE_QUERY, {
    variables: {
      id: id
    }
  })
  const [ updateSettings, { data: updateData }] = useMutation(UPDATE_SYSTEM_MAIL_TEMPLATE)

  console.log('query data app settings')
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


  return (
    <SettingsBase 
      headerSubTitle={headerSubTitle}
      cardTitle={cardTitle}
      sidebarActive={sidebarActive}
    >  
    <Formik
      initialValues={{ 
        subject: data.systemMailTemplate.subject,
        title: data.systemMailTemplate.title,
        description: data.systemMailTemplate.description,
        content: data.systemMailTemplate.content,
        comments: data.systemMailTemplate.comments        
      }}
      // validationSchema={MOLLIE_SCHEMA}
      onSubmit={(values, { setSubmitting }, errors) => {
          console.log('submit values:')
          console.log(values)
          console.log(errors)

          updateSettings({ variables: {
            input: {
              subject: values.subject,
              title: values.title,
              description: value.description,
              content: data.content,
              comments: comments.comments
            }
          }, refetchQueries: [
              {query: GET_SYSTEM_MAIL_TEMPLATE_QUERY}
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
        <SettingsMailTemplateEditForm
          isSubmitting={isSubmitting}
          errors={errors}
          values={values}
        >
          {console.log(errors)}
        </SettingsMailTemplateEditForm>
      )}
      </Formik>
    </SettingsBase>
  )
}


export default withTranslation()(withRouter(SettingsMailTemplateEdit))