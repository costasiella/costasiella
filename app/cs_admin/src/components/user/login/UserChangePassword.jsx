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
  Button,
  Card,
  Icon,
  StandaloneFormPage,
} from "tabler-react"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import { UPDATE_ACCOUNT_PASSWORD } from "../../../queries/system/auth"
import CSLS from "../../../tools/cs_local_storage"
import UserChangePasswordForm from './UserChangePasswordForm';


function UserChangePassword({t, match, history}) {
  let errorMessage
  const [updatePassword, { data }] = useMutation(UPDATE_ACCOUNT_PASSWORD)

  return (
    <StandaloneFormPage imageURL="">
      {/* TODO: point imageURL to logo */}
      <Formik
        initialValues={{ 
          passwordCurrent: "",
          passwordNew: "",
          passwordNew2: ""
        }}
        // validationSchema={ACCOUNT_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
            console.log('submit values:')
            console.log(values)

            let vars = {
              input: {
                passwordCurrent: values.passwordCurrent,
                passwordNew: values.passwordNew
              }
            }

            updatePassword({ variables: vars,
              refetchQueries: [
                // // Refetch list
                // {query: GET_ACCOUNTS_QUERY, variables: get_list_query_variables()},
                // // Refresh local cached results for this account
                // {query: GET_ACCOUNT_QUERY, variables: {"id": match.params.account_id}}
            ]})
            .then(({ data }) => {
                console.log('got data', data)
                toast.info((t('user.change_password.success')), {
                  position: toast.POSITION.BOTTOM_RIGHT
                })
                history.push('/')
              }).catch((error) => {
                if ( error.message.includes('credentials') ) {
                  // Request user to input valid credentials
                  toast.info((t('user.change_password.invalid_credentials')), {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                } else {
                  // Show general error message
                  toast.error(error.message.replace('GraphQL error: ', ''), {
                    position: toast.POSITION.BOTTOM_RIGHT
                  })
                }
                console.log('there was an error sending the query', error)
                setSubmitting(false)
              })
        }}
        >
        {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
          <UserChangePasswordForm
            isSubmitting={isSubmitting}
            etFieldValue={setFieldValue}
            esetFieldTouched={setFieldTouched}
            errors={errors}
            values={values}
          />
        )}
      </Formik>    
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
      <ToastContainer autoClose={5000}/>
    </StandaloneFormPage>
  )
}


export default withTranslation()(withRouter(UserChangePassword))