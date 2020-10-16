// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"


import {
  Page,
  Grid,
  Container,
} from "tabler-react";
import SiteWrapper from "../../../../SiteWrapper"
import HasPermissionWrapper from "../../../../HasPermissionWrapper"
import AutomationBack from "../../../AutomationBack"

function AutomationAccountSubscriptionMollieCollectionBase({t, history, match, children, returnUrl="/automation"}) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t('automation.title')} >
            <div className="page-options d-flex">
              <AutomationBack returnUrl={returnUrl} />
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

export default withTranslation()(withRouter(AutomationAccountSubscriptionMollieCollectionBase))