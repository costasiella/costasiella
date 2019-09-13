// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import {
  Page,
  Grid,
  Container,
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
import OrganizationMenu from "../../OrganizationMenu"


function OrganizationDocumentsBase({ t, children, headerLinks, sidebarButton }) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('organization.title')}>
            <div className="page-options d-flex">
              {headerLinks}
            </div>
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={9}>
              {children}        
            </Grid.Col>
            <Grid.Col md={3}>
              {sidebarButton}
              <OrganizationMenu active_link='organization'/>
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(OrganizationDocumentsBase))