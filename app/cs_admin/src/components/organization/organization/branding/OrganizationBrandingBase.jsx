// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from "react-router-dom"


import {
  Page,
  Grid,
  Button,
  Card,
  Container
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import HasPermissionWrapper from "../../../HasPermissionWrapper"

import OrganizationMenu from "../../OrganizationMenu"


function OrganizationBrandingBase({t, match, history, children}) {
  const id = match.params.id

  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('organization.title')} />
          <Grid.Row>
            <Grid.Col md={9}>
              <h3>{t('organization.organization.branding.title')}</h3>
              {children}
            </Grid.Col>
            <Grid.Col md={3}>
              <h5>{t("general.menu")}</h5>
              <OrganizationMenu active_link='organization_branding'/>
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(OrganizationBrandingBase))