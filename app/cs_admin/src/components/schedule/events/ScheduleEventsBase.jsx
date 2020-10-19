// @flow
import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"

import {
  Page,
  Container
} from "tabler-react";
import SiteWrapper from "../../../SiteWrapper"
// import ShopAccountBack from "../ShopAccountBack"


function ScheduleEventsBase({ t, match, history, children, accountName="" }) {
  return (
      <SiteWrapperShop>
        <div className="my-3 my-md-5">
          <Container>
            <Page.Header title={t("schedule.events.title")} subTitle={ accountName }>
              <div className="page-options d-flex">
                {/* TODO: Add back button ? */}
                Back here...
                {/* <ShopAccountBack /> */}
              </div>
            </Page.Header>
            { children }
          </Container>
        </div>
      </SiteWrapperShop>
  )
}

export default withTranslation()(withRouter(ScheduleEventsBase))
