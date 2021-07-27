// @flow

import React from 'react'
import { withTranslation } from 'react-i18next'
import { withRouter } from "react-router"
import { Link } from 'react-router-dom'

import {
  Container,
  Page
} from "tabler-react";
import SiteWrapper from "../../SiteWrapper"


function HomeHomeBase({ t, match, history, children }) {
  
  return (
    <SiteWrapper>
      <div className="my-3 my-md-5">
        <Container>
          <Page.Header title={t("organization.announcements.title")} />
          {children}
        </Container>
      </div>
    </SiteWrapper>
  )
}


export default withTranslation()(withRouter(HomeHomeBase))