// @flow
import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Container,
  Grid
} from "tabler-react";
import HasPermissionWrapper from "../../../HasPermissionWrapper"
import SiteWrapper from "../../../SiteWrapper"
import ScheduleEventEditMenu from "./ScheduleEventEditMenu"


function ScheduleEventEditBaseBase({ t, match, history, children, sidebarContent="", activeLink, eventId }) {
  return (
      <SiteWrapper>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t("schedule.events.title")} >
              <div className="page-options d-flex">
                {/* Page options can go here... */}
              </div>
            </Page.Header>
            <Grid.Row>
            <Grid.Col md={9}>
              { children }
            </Grid.Col>
            <Grid.Col md={3}>
              { sidebarContent }
              <h5>{t("general.menu")}</h5>
              <ScheduleEventEditMenu active_link={activeLink} eventId={eventId}/>
            </Grid.Col>
            </Grid.Row>
          </Container>
        </div>
      </SiteWrapper>
  )
}

export default withTranslation()(withRouter(ScheduleEventEditBaseBase))