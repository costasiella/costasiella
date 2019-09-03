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

import AppSettingsMenu from "./AppSettingsMenu"

function AppSettingsBase({ t, children, cardTitle, sidebarActive, sidebarContent }) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('settings.title')} />
          <Grid.Row>
            <Grid.Col md={9}>
            <Card>
              <Card.Header>
                <Card.Title>{cardTitle}</Card.Title>
              </Card.Header>
              {children}
            </Card>
            </Grid.Col>
            <Grid.Col md={3}>
              <AppSettingsMenu active_link={sidebarActive} />
              {sidebarContent}
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(AppSettingsBase))