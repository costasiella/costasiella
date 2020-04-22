// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import {
  Page,
  Grid,
  Container,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import HasPermissionWrapper from "../../HasPermissionWrapper"
import { toast } from 'react-toastify'


function SettingsMailTemplatesBase({ t, children, headerSubTitle, help="" }) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("settings.mail.templates.title")} subTitle={headerSubTitle}>
            {/* To do: back button here */}
          </Page.Header>
          <Grid.Row>
            <Grid.Col md={8}>
              {children}
            </Grid.Col>
            <Grid.Col md={4}>
              {help}
            </Grid.Col>
          </Grid.Row>
        </Container>
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(SettingsMailTemplatesBase))