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
  Button,
  GalleryCard,
  Grid,
  Icon
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
        <Grid.Row>
          <Grid.Col md={4}>
            <GalleryCard>
              <GalleryCard.Image
                src={organization.urlLogoLogin}
              >
              </GalleryCard.Image>
              <GalleryCard.Details>
                Logo login
              </GalleryCard.Details>
              <GalleryCard.Details>
                <Link to={`/organization/edit/${id}/branding/logoLogin`}>
                  <Button block color="link">
                    {t("organization.branding.link_change")} <Icon name="chevron-right" />
                  </Button>
                </Link>
              </GalleryCard.Details>
            </GalleryCard>
          </Grid.Col>
        </Grid.Row>
    </OrganizationEditBrandingBase>
  )
}


export default withTranslation()(withRouter(OrganizationEdit))