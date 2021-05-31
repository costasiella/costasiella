// @flow

import React, { useContext } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo";
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { PASSWORD_CHANGE_SCHEMA } from './yupSchema'
import OrganizationContext from '../../context/OrganizationContext'

import {
  Button,
  Card,
  Icon,
  List,
  StandaloneFormPage,
} from "tabler-react"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import { UPDATE_ACCOUNT_PASSWORD } from "../../../queries/system/auth"
import CSLS from "../../../tools/cs_local_storage"
import UserPasswordChangeForm from './UserPasswordChangeForm';

import CSStandaloneFormPage from "../../ui/CSStandaloneFormPage"


function UserChangePassword({t, match, history}) {
  const organization = useContext(OrganizationContext)
  console.log(organization)

  let errorMessage
  const [updatePassword, { data }] = useMutation(UPDATE_ACCOUNT_PASSWORD)

  return (
    <CSStandaloneFormPage urlLogo={organization.urlLogoLogin} >
      {/* TODO: point imageURL to logo */}
      <Formik
        initialValues={{ 
          passwordCurrent: "",
          passwordNew: "",
          passwordNew2: ""
        }}
        validationSchema={PASSWORD_CHANGE_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
            console.log('submit values:')
            console.log(values)

            let vars = {
              input: {
                passwordCurrent: values.passwordCurrent,
                passwordNew: values.passwordNew
              }
            }

            updatePassword({ variables: vars })
              .then(({ data }) => {
                console.log('got data', data)
                setTimeout(() => toast.success((t('user.change_password.success')), {
                  position: toast.POSITION.BOTTOM_RIGHT
                }), 300)
                window.history.back()
              }).catch((error) => {
                console.log('#############')
                console.log(error.messages)
                console.log(error.graphQLErrors)
                console.log(Object.keys(error))

                if (error.graphQLErrors) {
                  let i
                  for (i = 0; i < error.graphQLErrors.length; i++) {
                    toast.error(error.graphQLErrors[0].message
                        .replace(/'/g, "")
                        .replace(/,/g, "")
                        .replace(/\[/g, "")
                        .replace(/\]/g, ""), {
                      position: toast.POSITION.BOTTOM_RIGHT
                    })
                  }
                } else {
                  // Show general error message
                  toast.error((t('general.toast_server_error')) + ': ' +  error, {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                }
                
                console.log('there was an error sending the query', error)
                setSubmitting(false)
              })
        }}
        >
        {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
          <UserPasswordChangeForm
            isSubmitting={isSubmitting}
            etFieldValue={setFieldValue}
            esetFieldTouched={setFieldTouched}
            errors={errors}
            values={values}
          />
        )}
      </Formik>    
      <h5>{t('user.change_password.requirements')}</h5>
      <List>
        <List.Item>{t('user.change_password.requirement_not_a_digit')}</List.Item>
        <List.Item>{t('user.change_password.requirement_not_common')}</List.Item>
        <List.Item>{t('user.change_password.requirement_min_length')}</List.Item>
        <List.Item>{t('user.change_password.requirement_not_similar_account')}</List.Item>
      </List>
      {/* Cancel button below form */}
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


export default withTranslation()(withRouter(UserChangePassword))