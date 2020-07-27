// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Card,
  Page,
  Grid,
  Container,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
import { toast } from 'react-toastify'

import SettingsBack from "../SettingsBack"

function SettingsMailTemplatesBase({ t, children, headerSubTitle, }) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("settings.mail.templates.title")} subTitle={headerSubTitle}>
            <div className="page-options d-flex">
              <SettingsBack />
            </div>
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={12}>
              {children}
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(SettingsMailTemplatesBase))