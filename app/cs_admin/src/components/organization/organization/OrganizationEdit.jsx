// @flow

import React, { useState, useRef } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ORGANIZATION_QUERY } from './queries'
import { ORGANIZATION_SCHEMA } from './yupSchema'
import OrganizationForm from './OrganizationForm'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"

import OrganizationEditBase from "./OrganizationEditBase"
import OrganizationMenu from "../OrganizationMenu"


const UPDATE_ORGANIZATION = gql`
  mutation UpdateOrganization($input: UpdateOrganizationInput!) {
    updateOrganization(input: $input) {
      organization {
        id
        name
      }
    }
  }
`


function OrganizationEdit({t, match, history}) {
  const id = match.params.id

  const [updateOrganization] = useMutation(UPDATE_ORGANIZATION)
  const { loading, error, data, fetchMore } = useQuery(GET_ORGANIZATION_QUERY, {
    variables: {
      id: id
  }})

  if (loading) return (
    <OrganizationEditBase>
      {t("general.loading_with_dots")}
    </OrganizationEditBase>
  )
  if (error) return (
    <OrganizationEditBase>
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </OrganizationEditBase>
  )

  const initialData = data.organization

  return (
 
    <OrganizationEditBase>
      <Formik
        initialValues={{ 
          name: initialData.name, 
          address: initialData.address,
          phone: initialData.phone,
          email: initialData.email,
          registration: initialData.registration,
          taxRegistration: initialData.taxRegistration,
        }}
        validationSchema={ORGANIZATION_SCHEMA}
        onSubmit={(values, { setSubmitting }) => {
          console.log('submit values:')
          console.log(values)

          updateOrganization({ variables: {
            input: {
              id: match.params.id,
              name: values.name,
              address: values.address,
              phone: values.phone,
              email: values.email,
              registration: values.registration,
              taxRegistration: values.taxRegistration,
            }
          }})
          .then(({ data }) => {
              console.log('got data', data)
              toast.success((t('organization.organization.toast_edit_success')), {
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
        {({ isSubmitting, errors, values, setFieldTouched, setFieldValue }) => (
          <OrganizationForm 
            isSubmitting={isSubmitting}
            values={values}
            errors={errors}
            setFieldTouched={setFieldTouched}
            setFieldValue={setFieldValue}
          />
        )}
      </Formik>
    </OrganizationEditBase>
  )
}


export default withTranslation()(withRouter(OrganizationEdit))