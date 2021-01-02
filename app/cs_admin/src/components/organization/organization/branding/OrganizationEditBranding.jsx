// @flow

import React, { useState, useRef } from 'react'
import gql from "graphql-tag"
import { useQuery, useMutation } from "react-apollo"
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"
import { Formik } from 'formik'
import { toast } from 'react-toastify'

import { GET_ORGANIZATION_QUERY } from '../queries'
// import { ORGANIZATION_SCHEMA } from './yupSchema'
import OrganizationEditBrandingForm from './OrganizationEditBrandingForm'


import {
  Page,
  Grid,
  Icon,
  Button,
  Card,
  Container
} from "tabler-react";
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import OrganizationEditBrandingBase from "./OrganizationEditBrandingBase"


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
    <OrganizationEditBrandingBase>
      {t("general.loading_with_dots")}
    </OrganizationEditBrandingBase>
  )
  if (error) return (
    <OrganizationEditBrandingBase>
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </OrganizationEditBrandingBase>
  )

  const organization = data.organization

  return (
 
    <OrganizationEditBrandingBase>
        hello world
    </OrganizationEditBrandingBase>
  )
}


export default withTranslation()(withRouter(OrganizationEdit))