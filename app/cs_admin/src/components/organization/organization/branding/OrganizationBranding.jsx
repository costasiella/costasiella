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

import {
  Button,
  GalleryCard,
  Grid,
  Icon
} from "tabler-react";
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import OrganizationBrandingBase from "./OrganizationBrandingBase"


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


function OrganizationBranding({t, match, history}) {
  const id = match.params.id

  const [updateOrganization] = useMutation(UPDATE_ORGANIZATION)
  const { loading, error, data, fetchMore } = useQuery(GET_ORGANIZATION_QUERY, {
    variables: {
      id: id
  }})

  if (loading) return (
    <OrganizationBrandingBase>
      {t("general.loading_with_dots")}
    </OrganizationBrandingBase>
  )
  if (error) return (
    <OrganizationBrandingBase>
      <p>{t('general.error_sad_smiley')}</p>
      <p>{error.message}</p>
    </OrganizationBrandingBase>
  )

  const organization = data.organization

  return (
 
    <OrganizationBrandingBase>
        <Grid.Row>
          <Grid.Col md={4}>
            <GalleryCard>
              <h5>{t('organization.branding.logo_login')}</h5>
              <GalleryCard.Image
                src={organization.urlLogoLogin}
              >
              </GalleryCard.Image>
              <GalleryCard.Details>
                <Link to={`/organization/edit/${id}/branding/logoLogin`}>
                  <Button block color="secondary">
                    {t("organization.branding.link_change")} <Icon name="chevron-right" />
                  </Button>
                </Link>
              </GalleryCard.Details>
            </GalleryCard>
          </Grid.Col>
          <Grid.Col md={4}>
            <GalleryCard>
              <h5>{t('organization.branding.logo_invoice')}</h5>
              <GalleryCard.Image
                src={organization.urlLogoInvoice}
              >
              </GalleryCard.Image>
              <GalleryCard.Details>
                <Link to={`/organization/edit/${id}/branding/logoInvoice`}>
                  <Button block color="secondary">
                    {t("organization.branding.link_change")} <Icon name="chevron-right" />
                  </Button>
                </Link>
              </GalleryCard.Details>
            </GalleryCard>
          </Grid.Col>
          <Grid.Col md={4}>
            <GalleryCard>
              <h5>{t('organization.branding.logo_email')}</h5>
              <GalleryCard.Image
                src={organization.urlLogoEmail}
              >
              </GalleryCard.Image>
              <GalleryCard.Details>
                <Link to={`/organization/edit/${id}/branding/logoEmail`}>
                  <Button block color="secondary">
                    {t("organization.branding.link_change")} <Icon name="chevron-right" />
                  </Button>
                </Link>
              </GalleryCard.Details>
            </GalleryCard>
          </Grid.Col>
          <Grid.Col md={4}>
            <GalleryCard>
              <h5>{t('organization.branding.logo_shop_header')}</h5>
              <GalleryCard.Image
                src={organization.urlLogoShopHeader}
              >
              </GalleryCard.Image>
              <GalleryCard.Details>
                <Link to={`/organization/edit/${id}/branding/logoShopHeader`}>
                  <Button block color="secondary">
                    {t("organization.branding.link_change")} <Icon name="chevron-right" />
                  </Button>
                </Link>
              </GalleryCard.Details>
            </GalleryCard>
          </Grid.Col>
          <Grid.Col md={4}>
            <GalleryCard>
              <h5>{t('organization.branding.logo_self_checkin')}</h5>
              <GalleryCard.Image
                src={organization.urlLogoSelfCheckin}
              >
              </GalleryCard.Image>
              <GalleryCard.Details>
                <Link to={`/organization/edit/${id}/branding/logoSelfCheckin`}>
                  <Button block color="secondary">
                    {t("organization.branding.link_change")} <Icon name="chevron-right" />
                  </Button>
                </Link>
              </GalleryCard.Details>
            </GalleryCard>
          </Grid.Col>
        </Grid.Row>
    </OrganizationBrandingBase>
  )
}


export default withTranslation()(withRouter(OrganizationBranding))