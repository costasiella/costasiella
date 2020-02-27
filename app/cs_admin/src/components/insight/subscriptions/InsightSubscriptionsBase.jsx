import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Grid,
  Container,
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"
import InsightBackHome from '../InsightBackHome'

function InsightSubscriptionsBase ({ t, history, children, year }) {
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("insight.title")} subTitle={t("general.subscriptions") + " " + year}>
            <div className="page-options d-flex">
              <InsightBackHome />
            </div>
          </Page.Header>
          <Grid.Row>
            {children}
          </Grid.Row>
        </Container>  
      </div>
    </SiteWrapper>
  )
}

export default withTranslation()(withRouter(InsightSubscriptionsBase))