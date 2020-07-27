// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Grid,
  Card,
  Container,
} from "tabler-react";
import SiteWrapper from "../SiteWrapper"
import HasPermissionWrapper from "../HasPermissionWrapper"
import SettingsBack from "./SettingsBack"


function SettingsBase({ t, children, headerSubTitle="", cardTitle, sidebarActive, sidebarContent, returnUrl="/settings" }) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('settings.title')} subTitle={headerSubTitle}>
            <div className="page-options d-flex">
              <SettingsBack returnUrl={returnUrl} />
            </div>
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={12}>
            <Card>
              <Card.Header>
                <Card.Title>{cardTitle}</Card.Title>
              </Card.Header>
              {children}
            </Card>
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(SettingsBase))